import streamlit as st
from map import display_map



st.set_page_config(layout="wide")

if "lat" not in st.session_state:
    st.session_state.clicked_lat = 52.2
    st.session_state.clicked_lon = 19.21

col1, col2 = st.columns([1,5])

with col2:
    display_map()

with col1:
    st.subheader("Lokalizacja:")
    st.write(f"📍 Latitude: {st.session_state.clicked_lat :.5f}")
    st.write(f"📍 Longitude: {st.session_state.clicked_lon :.5f}")


