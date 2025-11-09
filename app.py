import streamlit as st
from map import display_map
import joblib
from price_calculation import calculate_price


st.set_page_config(layout="wide", page_title="Nie przepłacaj! - porównaj ceny mieszkań w twojej okolicy", page_icon = "data/favicon.ico")
data = {"model": joblib.load("model/11-25_model_all.pkl")}






if "lat" not in st.session_state:
    st.session_state.clicked_lat = 52.2
    st.session_state.clicked_lon = 19.21

col1, col2 = st.columns([1,5])

with col2:
    with st.expander("Jak używać aplikacji?"):
        st.markdown("""
        1. Kliknij na mapie, aby wybrać lokalizację.
        2. Wprowadź dane mieszkania.
        3. Wynik pojawi się w okienku. <br>
        Cena została oszacowana na podstawie analizy danych historycznych dotyczących transakcji mieszkań. <br>
        Model powstał na podstawie danych z [okna-bej.github.io](https://okna-bej.github.io/mieszkanka/) oraz
        [Dane i Analizy (prokulski.science)](https://prokulski.science/).
        """, unsafe_allow_html=True)
    display_map()

with col1:
    with st.expander("Rozwiń, by wpisać parametry mieszkania"):
        st.write(f"Lokalizacja: {st.session_state.clicked_lat :.4f}, {st.session_state.clicked_lon :.4f}")
        st.session_state.area = st.number_input("Powierzchnia mieszkania (m²)", min_value=1, max_value=500, value=40)
        st.session_state.floor_max = st.number_input("Liczba pięter w budynku", min_value=0, max_value=100, value=0)
        if "floor" not in st.session_state:
            st.session_state.floor = 0
        st.session_state.floor = st.number_input("Piętro, na którym znajduje się mieszkanie", min_value=0, max_value=st.session_state.floor_max, value=st.session_state.floor)
        if "floors" not in st.session_state:
            st.session_state.floors = 0
        st.session_state.floors = st.number_input("Liczba kondygnacji (budynku/mieszkania)", min_value=0, max_value=st.session_state.floor_max, value=st.session_state.floors)
        st.session_state.balcony = st.selectbox("Balkon", options=[0, 1], format_func=lambda x: "Tak" if x else "Nie", index=0)
        st.session_state.garden = st.selectbox("Ogród", options=[0, 1], format_func=lambda x: "Tak" if x else "Nie", index=0)
        st.session_state.loggia = st.selectbox("Loggia", options=[0, 1], format_func=lambda x: "Tak" if x else "Nie", index=0)
        st.session_state.terrace = st.selectbox("Taras", options=[0, 1], format_func=lambda x: "Tak" if x else "Nie", index=0)
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

    st.session_state.price_m2_lower, st.session_state.price_m2_upper, st.session_state.price_total_lower, st.session_state.price_total_upper = calculate_price(data)
    st.markdown(
        f"""
        <div style="padding: 1em; border-radius: 8px; background-color: #f0f2f6; border-left: 8px solid #4CAF50;">
            <h7 style="color: #4CAF50;">💰 Cena za m²: <span style="font-weight: bold;">{st.session_state.price_m2_lower:,.0f} - {st.session_state.price_m2_upper:,.0f} zł <br></span></h7>
            <h7 style="color: #2196F3;">🏠 Cena całkowita: <span style="font-weight: bold;">{st.session_state.price_total_lower:,.0f} - {st.session_state.price_total_upper:,.0f} zł</span></h7>
        </div>
        """,
        unsafe_allow_html=True
    )