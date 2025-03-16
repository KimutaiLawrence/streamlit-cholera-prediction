import streamlit as st
import geemap.foliumap as geemap
import ee
import time  # For simulating loading effect

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception as e:
    st.error("Earth Engine authentication required. Run `earthengine authenticate` in your terminal.")

st.set_page_config(page_title="🗺️ Cholera Prediction Application", layout="wide")

st.title("🗺️ Cholera Prediction Application")

# Create layout with two columns
col1, col2 = st.columns([3, 1])  # Left (map) takes 3x space, right (controls) takes 1x space

# Create interactive map in the left column
with col1:
    m = geemap.Map()
    m.add_basemap("HYBRID")

# Right column for controls
with col2:
    st.subheader("🛠️ Layer Controls")

    basemap = st.selectbox("Select Basemap", ["HYBRID", "ROADMAP", "SATELLITE", "TERRAIN"])
    m.add_basemap(basemap)

    # Define session state for layers
    if "layers" not in st.session_state:
        st.session_state.layers = {
            "Cholera Cases": False,
            "Rivers (100m Buffer)": False,
            "Dumping Sites": False,
            "LULC": False,
            "Rainfall": False,
            "Temperature": False,
        }

    def fetch_layer(layer_name):
        with st.spinner(f"Fetching {layer_name}..."):
            time.sleep(1)  # Simulate loading time
        st.session_state.layers[layer_name] = not st.session_state.layers[layer_name]

    # Dataset Fetching Section
    st.markdown("### 📂 Dataset Section")
    
    st.markdown('<style>div.stButton > button { width: 100%; background-color: #007BFF; color: white; }</style>', unsafe_allow_html=True)
    
    if st.button("Fetch Cholera Cases"):
        fetch_layer("Cholera Cases")
    if st.button("Fetch Rivers (100m Buffer)"):
        fetch_layer("Rivers (100m Buffer)")
    if st.button("Fetch Dumping Sites"):
        fetch_layer("Dumping Sites")
    if st.button("Fetch LULC"):
        fetch_layer("LULC")
    if st.button("Fetch Rainfall"):
        fetch_layer("Rainfall")
    if st.button("Fetch Temperature"):
        fetch_layer("Temperature")

    # Load / Process Model Section
    st.markdown("### ⚙️ Load / Process Model")
    if st.button("Run Prediction Model"):
        with st.spinner("Processing model..."):
            time.sleep(3)  # Simulate processing time
        st.success("Model processed successfully!")

    # Show Results Section
    st.markdown("### 📊 Show Results")
    if st.button("View Prediction Results"):
        st.info("Results will be displayed here.")

# Load GEE datasets
cholera_cases = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Cholera_Histo_Cases")
rivers = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Rivers-Bufzone_100m")
dumping_sites = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/DumpingSites")
lulc = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/LULC_2019")
rainfall = ee.Image("projects/analytical-rig-437519-k7/assets/Rainfall_2020")
temperature = ee.Image("projects/analytical-rig-437519-k7/assets/MMTemp_19")

# Load Nairobi Population FeatureCollection for zoom extent
nairobi_population = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Nairobi_Pop2019")

# Get bounds of Nairobi Population and set default zoom
nairobi_bounds = nairobi_population.geometry().bounds()
m.centerObject(nairobi_bounds, 11)  # Adjust zoom level as needed

# Add layers dynamically based on session state
if st.session_state.layers["Cholera Cases"]:
    m.addLayer(cholera_cases, {"color": "red"}, "Cholera Cases")
if st.session_state.layers["Rivers (100m Buffer)"]:
    m.addLayer(rivers, {"color": "blue"}, "Rivers (100m Buffer)")
if st.session_state.layers["Dumping Sites"]:
    m.addLayer(dumping_sites, {"color": "orange"}, "Dumping Sites")
if st.session_state.layers["LULC"]:
    m.addLayer(lulc, {}, "Land Use Land Cover (LULC)")
if st.session_state.layers["Rainfall"]:
    m.addLayer(rainfall, {}, "Rainfall 2020")
if st.session_state.layers["Temperature"]:
    m.addLayer(temperature, {}, "Mean Monthly Temperature 2019")

# Display map in the left column
with col1:
    m.to_streamlit(height=700)
