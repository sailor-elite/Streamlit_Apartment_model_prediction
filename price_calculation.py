import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic
import pandas as pd

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

def calculate_price(data):
    """
    Calculating price based on user input.
    :param data: user input
    :return price_m2_lower, price_m2_upper, price_total_lower, price_total_upper: lower and upper bounds of price per m2 and total
    """
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

    return price_m2_lower, price_m2_upper, price_total_lower, price_total_upper