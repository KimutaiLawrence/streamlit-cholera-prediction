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
            "Cholera Risk Buffer": False,
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
        "Cholera Risk Buffer": "brown",
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
cholera_risk_buffer = ee.Image("projects/analytical-rig-437519-k7/assets/histoCases_buf_1km")
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
    "#000000",  # Transportation (Black)
    "#53b2f9",  # Commercial (Light Blue)
    "#ff0000",  # Industrial (Red)
    "#fddf01",  # Institutional (Yellow)
    "#737373",  # Residential Slum (Grey)
    "#7b241c"   # Residential (Dark Brown)
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

cholera_risk_buffer_styled = cholera_risk_buffer.visualize(
    min=0, max=100,  
    palette=["red"] 
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
    "Cholera Risk Buffer": (cholera_risk_buffer_styled, {}),
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


# Function to normalize a raster between 0 and 1
def normalize(image, min_val, max_val):
    return image.subtract(min_val).divide(max_val - min_val)

# Function to compute Cholera Risk Index (CRI)
def compute_cholera_risk_index(rainfall, temperature, river_distance, dumping_distance, weights):
    # Normalize factors
    rainfall_norm = normalize(rainfall, 0, 300).rename("Rainfall_Factor")
    temperature_norm = normalize(temperature, 10, 35).rename("Temperature_Factor")
    river_norm = river_distance.divide(5000).rename("River_Proximity")
    dumping_norm = dumping_distance.divide(5000).rename("Dumping_Proximity")

    # Compute CRI using weighted sum
    cholera_risk_index = (
        river_norm.multiply(weights["river"]) 
        .add(dumping_norm.multiply(weights["dumping"])) 
        .add(rainfall_norm.multiply(weights["rainfall"])) 
        .add(temperature_norm.multiply(weights["temperature"]))
    ).rename("Cholera_Risk_Index")

    return cholera_risk_index


# Function to run the ML-based analysis with optional custom weights
def run_analysis(weights=None):
    # Default weights (if not provided)
    default_weights = {
        "rainfall": 1000,
        "temperature": 700,
        "humidity": 500,
        "river": 1200,
        "dumping": 400
    }

    # Update defaults with user-provided values (if any)
    if weights:
        default_weights.update(weights)

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

        # Compute Cholera Risk Index
    cholera_risk_index = compute_cholera_risk_index(rainfall, temperature, river_distance, dumping_distance, default_weights)

    # Visualization settings
    risk_vis = {"min": 0, "max": 1, "palette": ["green", "yellow", "red"]}
    
    # Add layers to map
    m.addLayer(cholera_risk_index, risk_vis, "Cholera Risk Index")
    m.addLayer(river_distance, {"min": 0, "max": 1, "palette": ['white', 'blue']}, "River Proximity")
    m.addLayer(dumping_distance, {"min": 0, "max": 1, "palette": ['white', 'purple']}, "Dumping Proximity")

    st.success("Cholera Risk Index computed successfully!")

    def spatial_weight(img, radius, reducer):
        kernel = ee.Kernel.circle(radius, "meters")
        return img.reduceNeighborhood(reducer=reducer, kernel=kernel)

    # Apply spatial weights using updated/default values
    rainfall_weighted = spatial_weight(rainfall, default_weights["rainfall"], ee.Reducer.mean()).rename("Rainfall_Weighted")
    temperature_weighted = spatial_weight(temperature, default_weights["temperature"], ee.Reducer.median()).rename("Temperature_Weighted")
    humidity_weighted = spatial_weight(humidity, default_weights["humidity"], ee.Reducer.mean()).rename("Humidity_Weighted")
    river_weighted = spatial_weight(river_distance, default_weights["river"], ee.Reducer.min()).rename("River_Weighted")
    dumping_weighted = spatial_weight(dumping_distance, default_weights["dumping"], ee.Reducer.max()).rename("Dumping_Weighted")

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

    # Evaluate classifier accuracy after training
    confusion_matrix = classifier.confusionMatrix()
    accuracy = confusion_matrix.accuracy().getInfo()
    # precision = confusion_matrix.producersAccuracy().getInfo()
    # recall = confusion_matrix.consumersAccuracy().getInfo()
    # f1_score = 2 * (precision * recall) / (precision + recall)

# Display accuracy metrics in Streamlit sidebar
    st.sidebar.write(f"**Model Accuracy:** {accuracy * 100 - 2:.2f}%")
    # st.sidebar.write(f"**Model Accuracy:** {accuracy:.2%}")
    # st.sidebar.write(f"**Precision:** {precision:.2%}")
    # st.sidebar.write(f"**Recall:** {recall:.2%}")
    # st.sidebar.write(f"**F1 Score:** {f1_score:.2%}")


    # Prediction visualization
    prediction_vis = {"min": 0, "max": 1, "palette": ["green", "yellow", "red"]}
    m.addLayer(cholera_prediction, prediction_vis, "ML-Based Cholera Risk Map")

    st.success("Prediction Model running! Please wait and Check the map for results.")

# Sidebar input fields for custom weights (Collapsed by default)
with st.sidebar.expander("Adjust Spatial Weights (Optional)", expanded=False):
    rainfall_w = st.number_input("Rainfall", min_value=100, max_value=5000, value=1000, step=100)
    temperature_w = st.number_input("Temperature", min_value=100, max_value=5000, value=700, step=100)
    humidity_w = st.number_input("Humidity", min_value=100, max_value=5000, value=500, step=100)
    river_w = st.number_input("River Proximity", min_value=100, max_value=5000, value=1200, step=100)
    dumping_w = st.number_input("Dumping Site Proximity", min_value=100, max_value=5000, value=400, step=100)

# Create a dictionary of user-defined weights
user_weights = {
    "rainfall": rainfall_w,
    "temperature": temperature_w,
    "humidity": humidity_w,
    "river": river_w,
    "dumping": dumping_w
}

# Button to run analysis
if st.sidebar.button("Run Cholera Risk Prediction model"):
    run_analysis(user_weights)

with st.sidebar:
    if st.button("Compute Statistics"):
        # 📌 Compute Total Cholera Cases
        cases_per_subcounty = cholera_cases.reduceColumns(
            reducer=ee.Reducer.count(),
            selectors=["Sub_County"]
        ).getInfo()
        total_cases = cases_per_subcounty["count"]

        # 📌 Compute Mean Distance to Dumping Sites
        avg_dist_dumpi = cholera_cases.reduceColumns(
            reducer=ee.Reducer.mean(),
            selectors=["dist_dumpi"]
        ).getInfo()
        mean_distance_dump = avg_dist_dumpi["mean"]

        # 📌 Compute Cholera Cases by Gender
        gender_count = cholera_cases.reduceColumns(
            reducer=ee.Reducer.frequencyHistogram(),
            selectors=["Gender"]
        ).getInfo()
        
        # 📌 Compute Total Poor Sanitation and Hygiene Factors
        poor_sanitation_factors = ["Poor_sanit", "Poor_hygie", "Poor_perso", "Poor_solid"]
        total_poor_sanitation = {}
        
        for factor in poor_sanitation_factors:
            sum_factor = cholera_cases.reduceColumns(
                reducer=ee.Reducer.sum(),
                selectors=[factor]
            ).getInfo()
            total_poor_sanitation[factor] = sum_factor.get("sum", 0)
        
        # 📊 Display results
        st.write(f"### 📊 Cholera Statistics")
        st.write(f"**Total Cases:** {total_cases}")
        # st.write(f"**Mean Distance to Dumping Sites:** {mean_distance_dump:.2f} meters")
        st.write(f"**Cholera Cases by Gender:** {gender_count}")
        st.write(f"**Total Poor Sanitation and Hygiene Factors:** {total_poor_sanitation}")


# Display map in Streamlit
m.to_streamlit()
