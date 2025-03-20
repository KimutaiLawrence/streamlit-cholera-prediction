import streamlit as st
import geemap.foliumap as geemap
import ee
import time

m = geemap.Map()

# Set page configuration
st.set_page_config(page_title="🗺️ Cholera Prediction Application", layout="wide")

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception as e:
    st.error("Earth Engine authentication required. Run `earthengine authenticate` in your terminal.")
    st.stop()

# Title
st.title("🗺️ Cholera Prediction Application")

# Create layout with two columns
col1, col2 = st.columns([4, 1])  # Left (map) takes 4x space, right (controls) takes 1x space

# Create interactive map in the left column
with col1:
    m.add_basemap("HYBRID")

# Sidebar for controls
with st.sidebar:
    st.subheader("🛠️ Layer Controls")

    basemap = st.selectbox("Select Basemap", ["HYBRID", "OSM", "ROADMAP", "SATELLITE", "TERRAIN"])
    m.add_basemap(basemap)

    # Define session state for layers
    if "layers" not in st.session_state:
        st.session_state.layers = {
            "Cholera Cases": False,
            "Rivers (100m Buffer)": False,
            "Dumping Sites": False,
            "Dumping Sites Buffer": False,  # Fix: Added missing entry
            "LULC": False,
            "Rainfall": False,
            "Temperature": False,
            "Humidity": False,
            "Prediction Map": False,
            "Cholera Risk Map": False,
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
        "Dumping Sites Buffer": "yellow",
        "LULC": "green",
        "Rainfall": "purple",
        "Temperature": "brown",
        "Humidity": "brown",
        "Cholera Risk Map": "brown",
    }

    for layer_name, color in layer_buttons.items():
        if st.button(f"Fetch {layer_name}", key=layer_name):
            toggle_layer(layer_name)


# Load GEE datasets
cholera_cases = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Cholera_Histo_Cases")
rivers = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Rivers-Bufzone_100m")
dumping_sites = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/DumpingSites")
dumping_sites_buffer = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/dampingSite_buff500m")
lulc = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/LULC_2019")
rainfall = ee.Image("projects/analytical-rig-437519-k7/assets/Rainfall_2020")
temperature = ee.Image("projects/analytical-rig-437519-k7/assets/MMTemp_19")
humidity = ee.Image("projects/analytical-rig-437519-k7/assets/RHU_2020")
cholera_risk_map = ee.Image("projects/analytical-rig-437519-k7/assets/chorera_riskMap")


# Load Nairobi Population FeatureCollection for zoom extent
nairobi_population = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Nairobi_Pop2019")
nairobi_bounds = nairobi_population.geometry().bounds()
m.centerObject(nairobi_bounds, 11)  # Adjust zoom level as needed


# Define land use classification mapping
lulc_classes = {
    "transportation": 1,
    "commercial": 2,
    "industrial": 3,
    "institutional": 4,
    "res_slum": 5,
    "residential": 6
}


# Define color palette
lulc_palette = [
    "#FF0000",  # Transportation (Red)
    "#FFA500",  # Commercial (Orange)
    "#808080",  # Industrial (Gray)
    "#0000FF",  # Institutional (Blue)
    "#8B0000",  # Residential Slum (Dark Red)
    "#008000"   # Residential (Green)
]


# Convert string LANDUSE to numeric values
def convert_landuse(feature):
    landuse = feature.get("LANDUSE")  # Get LANDUSE value
    value = ee.Dictionary(lulc_classes).get(landuse, 0)  # Assign numeric value, default to 0
    return feature.set("LANDUSE_NUM", value)  # Create new numeric column


lulc_numeric = lulc.map(convert_landuse)  # Apply transformation


# Convert FeatureCollection to Image
lulc_image = lulc_numeric.reduceToImage(
    properties=['LANDUSE_NUM'],  # Use new numeric property
    reducer=ee.Reducer.first()  # Take the first value for each pixel
)


# Apply color styling
lulc_styled = lulc_image.visualize(
    min=1, max=len(lulc_classes),
    palette=lulc_palette
)


# Function to add a legend dynamically
def add_legend():
    """Displays a legend when the LULC layer is added."""
    st.sidebar.markdown("### LULC Legend")
    for i, (label, color) in enumerate(zip(lulc_classes.keys(), lulc_palette)):
        st.sidebar.markdown(
            f'<div style="display:flex;align-items:center;">'
            f'<div style="width:20px;height:20px;background:{color};margin-right:10px;"></div>'
            f'{label.capitalize()}</div>',
            unsafe_allow_html=True
        )


rainfall_styled = rainfall.visualize(
    min=0, max=200,  # Adjust max value based on dataset
    palette=["blue", "green", "yellow", "red"]  # Blue (low) → Green → Yellow → Red (high)
)

temperature_styled = temperature.visualize(
    min=10, max=40,  # Adjust min/max based on dataset
    palette=["blue", "green", "yellow", "red"]  # Blue (cold) → Green → Yellow → Red (hot)
)

humidity_styled = humidity.visualize(
    min=0, max=100,  # Adjust based on dataset
    palette=["blue", "green", "yellow", "red"]  # Blue (low humidity) → Green → Yellow → Red (high humidity)
)



# Define layers and their styles
layer_styles = {
    "Cholera Cases": (cholera_cases, {"color": "red"}),
    "Rivers (100m Buffer)": (rivers, {"color": "blue"}),
    "Dumping Sites": (dumping_sites, {"color": "orange"}),
    "Dumping Sites Buffer": (dumping_sites_buffer, {"color": "yellow"}),
    "LULC": (lulc_styled, {}),
    "Rainfall": (rainfall_styled, {}),
    "Temperature": (temperature_styled, {}),
    "Humidity": (humidity_styled, {}),
    "Cholera Risk Map": (cholera_risk_map, {}),
}


legend_active = False  # Track if legend should be displayed


# Add layers dynamically based on session state
for layer_name, dataset in layer_styles.items():
    if st.session_state.layers.get(layer_name, False):  # Ensure it doesn't fail if the key is missing
        m.addLayer(*dataset, layer_name)
        if layer_name == "LULC":  
            legend_active = True  # Set flag for legend




# Show or clear legend based on active layer
if legend_active:
    add_legend()
else:
    st.sidebar.markdown("")  # Clear legend when LULC is deselected

# Function to run the ML-based analysis
def run_analysis():
    # init_ee()

    # Load vector datasets
    cholera_cases = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Cholera_Histo_Cases")
    rivers = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Rivers-Bufzone_100m")
    dumping_sites = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/DumpingSites")
    population = ee.FeatureCollection("projects/analytical-rig-437519-k7/assets/Nairobi_Pop2019")  # AOI

    # Define AOI
    aoi = population.geometry()

    # Load and preprocess raster datasets
    rainfall = ee.Image("projects/analytical-rig-437519-k7/assets/Rainfall_2020").clip(aoi).select("b1").rename("Rainfall_Factor")
    temperature = ee.Image("projects/analytical-rig-437519-k7/assets/MMTemp_19").clip(aoi).select("b1").rename("Temperature_Factor")
    humidity = ee.Image("projects/analytical-rig-437519-k7/assets/RHU_2020").clip(aoi).select("b1").rename("Humidity")

    # Convert vector to raster using proximity
    river_distance = rivers.distance(5000).divide(5000).rename("River_Proximity").clip(aoi)
    dumping_distance = dumping_sites.distance(5000).divide(5000).rename("Dumping_Proximity").clip(aoi)

    def spatial_weight(img, radius, reducer):
        kernel = ee.Kernel.circle(radius, "meters")
        return img.reduceNeighborhood(reducer=reducer, kernel=kernel)

    rainfall_weighted = spatial_weight(rainfall, 1000, ee.Reducer.mean()).rename("Rainfall_Weighted")
    temperature_weighted = spatial_weight(temperature, 700, ee.Reducer.median()).rename("Temperature_Weighted")
    humidity_weighted = spatial_weight(humidity, 500, ee.Reducer.mean()).rename("Humidity_Weighted")
    river_weighted = spatial_weight(river_distance, 1200, ee.Reducer.min()).rename("River_Weighted")  # Lower distance = higher risk
    dumping_weighted = spatial_weight(dumping_distance, 400, ee.Reducer.max()).rename("Dumping_Weighted")  # Worst pollution affects the most


    # Feature extraction function
    def extract_features(points):
        return (
            river_distance
            .addBands(dumping_distance)
            .addBands(rainfall)
            .addBands(temperature)
            .addBands(humidity)
            .addBands(rainfall_weighted)
            .addBands(temperature_weighted)
            .addBands(humidity_weighted)
            .addBands(river_weighted)
            .addBands(dumping_weighted)
            .sampleRegions(
                collection=points,
                scale=30,
                properties=["label"],
                tileScale=2
            )
        )

    # Assign cholera cases a label of 1
    cholera_samples = cholera_cases.map(lambda feature: feature.set("label", 1))

    # Generate random points (label = 0)
    random_points = ee.FeatureCollection.randomPoints(region=aoi, points=500, seed=42)
    random_samples = random_points.map(lambda feature: feature.set("label", 0))

    # Extract features and merge datasets
    training_samples = extract_features(cholera_samples).merge(extract_features(random_samples))

    # Define bands
    bands = [
        "Rainfall_Factor", "Temperature_Factor", "River_Proximity", "Dumping_Proximity", "Humidity",
        "Rainfall_Weighted", "Temperature_Weighted", "Humidity_Weighted", "River_Weighted", "Dumping_Weighted"
    ]

    # Train a Random Forest model
    classifier = ee.Classifier.smileRandomForest(50).train(
        features=training_samples,
        classProperty="label",
        inputProperties=bands
    )

    # Apply model for prediction
    cholera_prediction = (
        river_distance
        .addBands(dumping_distance)
        .addBands(rainfall)
        .addBands(temperature)
        .addBands(humidity)
        .addBands(rainfall_weighted)
        .addBands(temperature_weighted)
        .addBands(humidity_weighted)
        .addBands(river_weighted)
        .addBands(dumping_weighted)
        .classify(classifier)
        .unmask(0)
        .clip(aoi)
    )

    # Prediction visualization
    prediction_vis = {"min": 0, "max": 1, "palette": ["green", "yellow", "red"]}
    m.addLayer(cholera_prediction, prediction_vis, "ML-Based Cholera Risk Map")

    st.success("Prediction Model running! Please wait and Check the map for results.")

# Button to run analysis
if st.sidebar.button("Run Cholera Risk Prediction model"):
    run_analysis()

# Display map in Streamlit
m.to_streamlit()
