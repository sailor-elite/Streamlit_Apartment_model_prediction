from streamlit_folium import st_folium
import folium
import streamlit as st




def display_map():
    """
    Displays Streamlit Folium map and registers latitude and longitude based on user's activity.
    Map uses container width.
    Args:


    Returns:
        st.session_state.lat : st.session_state element with latitude based on user click
        st.session_state.lon : st.session_state element with longitude based on user click
     """

    lat = st.session_state.get("lat", 52.2)
    lon = st.session_state.get("lon", 19.21)
    make_map_responsive = """
     <style>
     [title~="st.iframe"] { width: 100%}
     </style>
    """
    st.markdown(make_map_responsive, unsafe_allow_html=True)
    m = folium.Map(location=[lat, lon], zoom_start=6)
    m.add_child(folium.LatLngPopup())
    output = st_folium(m, use_container_width=True)
    if output and output["last_clicked"]:
        st.session_state.lat = output["last_clicked"]["lat"]
        st.session_state.lon = output["last_clicked"]["lng"]