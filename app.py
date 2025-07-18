import streamlit as st
from map import display_map
import joblib
from price_calculation import calculate_price


st.set_page_config(layout="wide")
data = {"model": joblib.load("model/06-25_model_all.pkl")}






if "lat" not in st.session_state:
    st.session_state.clicked_lat = 52.2
    st.session_state.clicked_lon = 19.21

col1, col2 = st.columns([1,5])

with col2:
    display_map()

with col1:
    st.write(f"Latitude: {st.session_state.clicked_lat :.4f}")
    st.write(f"Longitude: {st.session_state.clicked_lon :.4f}")
    st.session_state.area = st.number_input("Powierzchnia mieszkania (m²)", min_value=1, max_value=500, value=40)
    st.session_state.balcony = st.selectbox("Balkon", options=[0, 1], format_func=lambda x: "Tak" if x else "Nie", index=0)
    st.session_state.floor = st.number_input("Piętro", min_value=0, max_value=100, value=0)
    st.session_state.floor_max = st.number_input("Liczba pięter w budynku", min_value=0, max_value=100, value=0)
    st.session_state.floors = st.number_input("Liczba pięter w mieszkaniu", min_value=0, max_value=100, value=0)

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

    price_m2_lower, price_m2_upper, price_total_lower, price_total_upper = calculate_price(data)
    st.markdown(
        f"""
        <div style="padding: 1em; border-radius: 8px; background-color: #f0f2f6; border-left: 8px solid #4CAF50;">
            <h7 style="color: #4CAF50;">💰 Cena za m²: <span style="font-weight: bold;">{price_m2_lower:,.2f} - {price_m2_upper:,.2f} zł <br></span></h7>
            <h7 style="color: #2196F3;">🏠 Cena całkowita: <span style="font-weight: bold;">{price_total_lower:,.2f} - {price_total_upper:,.2f} zł</span></h7>
        </div>
        """,
        unsafe_allow_html=True
    )