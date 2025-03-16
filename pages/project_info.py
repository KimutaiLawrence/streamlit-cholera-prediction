import streamlit as st

st.set_page_config(page_title="Project Info")

st.title("📄 Project Information")

st.write("""
### Project Overview
This application aims to predict cholera outbreaks in **Nairobi, Kenya** using **geospatial data** from **Google Earth Engine (GEE)**.

### Data Sources
- **Cholera Cases**: Historical cases of cholera outbreaks.
- **Land Use/Land Cover (LULC)**: Helps in analyzing urbanization and water contamination.
- **Rainfall & Temperature**: Climatic factors influencing disease spread.
- **Population Density**: Identifies high-risk zones.
- **Dumping Sites & Rivers**: Possible sources of contamination.

### Methodology
1. **Data Ingestion**: Earth Engine processes raster and vector datasets.
2. **Spatial Analysis**: Overlay cholera cases with environmental factors.
3. **Visualization**: Interactive maps for pattern identification.
""")
