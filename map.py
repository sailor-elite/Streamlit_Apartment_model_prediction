from streamlit_folium import st_folium
import folium
import streamlit as st




def display_map():
    """
    Displays a Streamlit Folium map and updates session_state with coordinates
    based on user's click. Prevents map from re-rendering unnecessarily.
    """
    if "initial_lat" not in st.session_state:
        st.session_state.initial_lat = 52.2
    if "initial_lon" not in st.session_state:
        st.session_state.initial_lon = 19.21

    if "clicked_lat" not in st.session_state:
        st.session_state.clicked_lat = None
    if "clicked_lon" not in st.session_state:
        st.session_state.clicked_lon = None

    make_map_responsive = """
     <style>
     [title~="st.iframe"] { width: 100%}
     </style>
    """
    st.markdown(make_map_responsive, unsafe_allow_html=True)

    m = folium.Map(location=[st.session_state.initial_lat, st.session_state.initial_lon], zoom_start=6)
    m.add_child(folium.LatLngPopup())

    output = st_folium(m, use_container_width=True, key="static_map")

    if output and output["last_clicked"]:
        st.session_state.clicked_lat = output["last_clicked"]["lat"]
        st.session_state.clicked_lon = output["last_clicked"]["lng"]

    return st.session_state.clicked_lat, st.session_state.clicked_lon