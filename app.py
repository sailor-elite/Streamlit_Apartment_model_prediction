import streamlit as st
from map import display_map
import joblib
import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic
import pandas as pd
import xgboost


st.set_page_config(layout="wide")
data = {"model": joblib.load("model/06-25_model_all.pkl")}
dict_gmin_centrum_gdf = gpd.read_file("model/slownik_gmin_centrum.gpkg")
dict_gmin_obrys_gdf = gpd.read_file("model/slownik_gmin_obrys.gpkg")

def find_gmina_teryt(map_df, lat, lng):
    """finds gmina at current point"""
    point = Point(lng, lat)

    for idx, row in map_df.iterrows():
        if row["geometry"].contains(point):
            return row["gmina_teryt"]
    return None

def get_distance_to_city_center(map_df, teryt, lat, lng):
    """distance from gmina center"""
    center = map_df[map_df["gmina_teryt"] == teryt]["geometry"].values[0]
    return geodesic((center.y, center.x), (lat, lng)).km

def get_gus_data(map_df, teryt):
    """getting GUS data for specified gmina"""
    row = map_df[map_df["gmina_teryt"] == teryt]
    if row.shape[0]:
        return {
            "ludnosc": row["ludnosc"].values[0],
            "wynagrodzenie": row["wynagrodzenie"].values[0],
            "gmina_area": row["gmina_area"].values[0],
            "gmina_area_per_person": row["gmina_area"].values[0] / row["ludnosc"].values[0],
            "gmina_rodzaj": row["gmina_rodzaj"].values[0],
        }
    return {
            "ludnosc": None,
            "wynagrodzenie": None,
            "gmina_area": None,
            "gmina_area_per_person": None,
            "gmina_rodzaj": None,
        }


if "lat" not in st.session_state:
    st.session_state.clicked_lat = 52.2
    st.session_state.clicked_lon = 19.21

col1, col2 = st.columns([1,5])

with col2:
    display_map()

with col1:
    st.write(f"Latitude: {st.session_state.clicked_lat :.5f}")
    st.write(f"Longitude: {st.session_state.clicked_lon :.5f}")
    st.session_state.area = st.number_input("Powierzchnia mieszkania (m²)", min_value=1, max_value=500, value=40)
    st.session_state.balcony = st.selectbox("Balkon", options=[0, 1], format_func=lambda x: "Tak" if x else "Nie", index=0)
    st.session_state.floor = st.number_input("Piętro", min_value=0, max_value=100, value=0)
    st.session_state.floor_max = st.number_input("Liczba pięter w budynku", min_value=0, max_value=100, value=0)
    st.session_state.floors = st.number_input("Liczba kondygnacji w mieszkaniu", min_value=0, max_value=100, value=0)

    st.session_state.garden = st.selectbox("Ogród", options=[0, 1], format_func=lambda x: "Tak" if x else "Nie")
    st.session_state.loggia = st.selectbox("Loggia", options=[0, 1], format_func=lambda x: "Tak" if x else "Nie")
    st.session_state.terrace = st.selectbox("Taras", options=[0, 1], format_func=lambda x: "Tak" if x else "Nie")
    data["user_entry"] = {
    "lng": st.session_state.clicked_lon,
    "lat": st.session_state.clicked_lat,
    "area": st.session_state.area,
    "balcony": st.session_state.balcony,
    "floor": st.session_state.floor,
    "floor_max": st.session_state.floor_max,
    "floors": st.session_state.floors,
    "garden": st.session_state.garden,
    "loggia": st.session_state.loggia,
    "terrace": st.session_state.terrace,
    }
    data["user_entry"]["top_floor"] = 1 if data["user_entry"]["floor"] == data["user_entry"]["floor_max"] else 0
    data["user_entry"]["has_loggia"] = 1 if data["user_entry"]["loggia"] > 0 else 0
    data["user_entry"]["has_terrace"] = 1 if data["user_entry"]["terrace"] > 0 else 0
    data["user_entry"]["balcony_and_loggia"] = data["user_entry"]["balcony"] + data["user_entry"]["loggia"]
    data["user_entry"]["terrace_and_garden"] = data["user_entry"]["terrace"] + data["user_entry"]["garden"]
    data["user_entry"].pop("loggia")
    data["user_entry"].pop("terrace")
    gm_teryt = find_gmina_teryt(dict_gmin_obrys_gdf, data["user_entry"]["lat"], data["user_entry"]["lng"])
    data["user_entry"]["distance_to_city_center"] = get_distance_to_city_center(
        dict_gmin_centrum_gdf, gm_teryt, data["user_entry"]["lat"], data["user_entry"]["lng"]
    )
    data["GUS"] = get_gus_data(dict_gmin_obrys_gdf, gm_teryt)
    data["user_entry"] = data["user_entry"] | data["GUS"]
    feature_names = data["model"].get_booster().feature_names
    data["predict"] = pd.DataFrame([data["user_entry"]])
    data["predict"] = data["predict"][feature_names]
    rmse = 750
    price_m2 = data["model"].predict(data["predict"])[0]
    price_m2_lower = max(price_m2 - rmse, 0)
    price_m2_upper = price_m2 + rmse
    price_total_lower = price_m2_lower * data["user_entry"]["area"]
    price_total_upper = price_m2_upper * data["user_entry"]["area"]

    st.markdown(
        f"""
        <div style="padding: 1em; border-radius: 8px; background-color: #f0f2f6; border-left: 8px solid #4CAF50;">
            <h7 style="color: #4CAF50;">💰 Cena za m²: <span style="font-weight: bold;">{price_m2_lower:,.2f} - {price_m2_upper:,.2f} zł <br></span></h7>
            <h7 style="color: #2196F3;">🏠 Cena całkowita: <span style="font-weight: bold;">{price_total_lower:,.2f} - {price_total_upper:,.2f} zł</span></h7>
        </div>
        """,
        unsafe_allow_html=True
    )