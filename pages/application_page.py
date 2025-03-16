import streamlit as st
import geemap.foliumap as geemap
import ee
import time

import json

# Securely load the service account key
EE_USER = "gee-service-account@analytical-rig-437519-k7.iam.gserviceaccount.com"
EE_PRIVATE_KEY = "analytical-rig-437519-k7-86c701a6e623.json" 


# Set page configuration
st.set_page_config(page_title="🗺️ Cholera Prediction Application", layout="wide")

# Initialize Earth Engine
try:
    with open(EE_PRIVATE_KEY) as key_file:
        service_account_info = json.load(key_file)
    credentials = ee.ServiceAccountCredentials(EE_USER, key_data=service_account_info)
    ee.Initialize(credentials)
except Exception as e:
    st.error("Earth Engine authentication required. Run `earthengine authenticate` in your terminal.")
    st.stop()

# Title
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
            "Prediction Map": False,
        }

    def toggle_layer(layer_name):
        st.session_state.layers[layer_name] = not st.session_state.layers[layer_name]

    # Dataset Fetching Section
    st.markdown("### 📂 Dataset Section")
    
    # Styled Buttons for Fetching Layers
    layer_buttons = {
        "Cholera Cases": "red",
        "Rivers (100m Buffer)": "blue",
        "Dumping Sites": "orange",
        "LULC": "green",
        "Rainfall": "purple",
        "Temperature": "brown",
    }

    for layer_name, color in layer_buttons.items():
        if st.button(f"Toggle {layer_name}", key=layer_name):
            toggle_layer(layer_name)

    # Load / Process Model Section
    st.markdown("### ⚙️ Cholera Prediction Model")
    if st.button("Run Prediction Model"):
        with st.spinner("Processing model..."):
            time.sleep(3)  # Simulate processing time
            st.session_state.layers["Prediction Map"] = True
        st.success("Prediction model generated successfully!")

    # Show Results Section
    st.markdown("### 📊 Show Results")
    if st.button("View Prediction Results"):
        st.info("Prediction results are now displayed on the map.")

# Load GEE datasets
cholera_cases = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Cholera_Histo_Cases")
rivers = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Rivers-Bufzone_100m")
dumping_sites = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/DumpingSites")
lulc = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/LULC_2019")
rainfall = ee.Image("projects/analytical-rig-437519-k7/assets/Rainfall_2020")
temperature = ee.Image("projects/analytical-rig-437519-k7/assets/MMTemp_19")

# Load Nairobi Population FeatureCollection for zoom extent
nairobi_population = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Nairobi_Pop2019")
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

# Cholera Prediction Model (Weighted Overlay)
if st.session_state.layers["Prediction Map"]:
    # Get max values for normalization
    max_rainfall = rainfall.reduceRegion(ee.Reducer.max(), nairobi_bounds, 30).get("b1")
    max_temperature = temperature.reduceRegion(ee.Reducer.max(), nairobi_bounds, 30).get("b1")

if max_rainfall is not None and max_temperature is not None:
    rainfall_scaled = rainfall.divide(ee.Image.constant(max_rainfall))
    temperature_scaled = temperature.divide(ee.Image.constant(max_temperature))
else:
    st.error("Error computing max values for rainfall or temperature.")

    # Fix: Convert max values to ee.Image before division
    # rainfall_scaled = rainfall.divide(ee.Image.constant(max_rainfall))
    # temperature_scaled = temperature.divide(ee.Image.constant(max_temperature))
    
    # Convert cholera cases to raster (1 where cases exist)
    cholera_raster = cholera_cases.reduceToImage(["ID"], ee.Reducer.first()).gt(0)
    
    # Weighted sum model for prediction
    prediction = (
        rainfall_scaled.multiply(0.4)  # 40% weight for rainfall
        .add(temperature_scaled.multiply(0.3))  # 30% weight for temperature
        .add(cholera_raster.multiply(0.3))  # 30% weight for past cases
    )

    prediction_params = {
        "min": 0,
        "max": 1,
        "palette": ["green", "yellow", "red"]
    }

    m.addLayer(prediction, prediction_params, "Cholera Prediction Map")

# Display map in the left column
with col1:
    m.to_streamlit(height=700)
