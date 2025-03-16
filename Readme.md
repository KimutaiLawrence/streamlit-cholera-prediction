# Cholera Prediction using Geospatial Data 🌍💧

This Streamlit application leverages **Google Earth Engine (GEE)** and **machine learning** to predict cholera outbreak risk zones in **Nairobi, Kenya**. The model is trained on historical cholera cases and environmental factors such as **land use, population density, rainfall, and temperature**.

## 🌟 Features

- **Project Overview:** Explains the motivation and data sources.
- **Interactive Map:** Uses **geemap** for spatial visualization.
- **Cholera Risk Prediction:** Machine learning model predicts high-risk areas.
- **Geospatial Data Integration:** Fetches data directly from **Google Earth Engine**.
- **User Controls:** Streamlit widgets for interactive exploration.
- **Model Training:** Trains a **Random Forest/XGBoost** model on geospatial data.
- **Prediction Output:** Generates risk maps based on trained model.

## 📂 Project Structure

```
streamlit-cholera-prediction/
├── pages/  # Additional pages
│   ├── project_info.py         # Overview of the project
│   ├── cholera_prediction.py   # Main application with interactive map
│   ├── about_author.py         # Information about the developer
├── model/  # Machine learning model files
│   ├── train_model.py          # Script for training the model
│   ├── predict.py              # Script for making predictions
├── data/  # Contains processed datasets
├── app.py  # Main entry point
├── requirements.txt  # Dependencies
├── README.md  # Project documentation
```

## 🗺️ Data Sources

- **Google Earth Engine Assets**
  - Historical cholera cases
  - Population density (2019)
  - Land Use/Land Cover (LULC, 2019)
  - Rainfall & temperature (2020)
  - Dumping sites (potential contamination sources)
  - River buffer zones (proximity to water sources)

## 🔬 Model Training & Prediction

- **Algorithm:** Uses a supervised machine learning model (e.g., **Random Forest, XGBoost**).
- **Feature Engineering:** Extracts geospatial features for training.
- **Training Pipeline:** Processes data, extracts features, and trains the model.
- **Prediction Output:** Displays risk zones on an interactive map.
- **Evaluation:** Assesses model performance using accuracy metrics.

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/KimutaiLawrence/streamlit-cholera-prediction.git
   cd streamlit-cholera-prediction
   ```

2. **Create a virtual environment & install dependencies:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application:**
   ```sh
   streamlit run app.py
   ```

## 📖 Usage

- Navigate to **Project Info** for background details.
- Use **Cholera Prediction** to visualize risk zones on the map.
- Visit **About Author** to learn about the developer.
- Train a new model using **train_model.py** if needed.
- Run **predict.py** to generate predictions from the trained model.

## 📝 Author

👤 **Lawrence Kimutai**  
📧 Email: [lawrencekimutai001@gmail.com](mailto:lawrencekimutai001@gmail.com)  
🔗 GitHub: [KimutaiLawrence](https://github.com/KimutaiLawrence)

---

🚀 **Let's predict and prevent cholera outbreaks using geospatial intelligence!**  

