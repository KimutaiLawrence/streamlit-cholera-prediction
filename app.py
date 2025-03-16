import streamlit as st

st.set_page_config(page_title="Cholera Prediction", layout="wide")

st.sidebar.title("Navigation")
st.sidebar.page_link("pages/project_info.py", label="📄 Project Info")
st.sidebar.page_link("pages/application_page.py", label="🗺️ Application")
st.sidebar.page_link("pages/about_author.py", label="👤 About Author")

st.title("Cholera Prediction System")
st.write("Welcome to the Cholera Prediction Web Application. Use the sidebar to navigate.")
