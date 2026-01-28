import streamlit as st
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# -------------------- CONFIG --------------------
st.set_page_config(page_title="Car Recommendation System", layout="wide")

PLACEHOLDER_IMAGE = "https://via.placeholder.com/300x200?text=No+Image"

# -------------------- LOAD DATA --------------------
@st.cache_data(show_spinner="Loading data...")
def load_all():
    df = pd.read_csv("data_files/cars_prepared.csv")
    vectorizer = joblib.load("models/vectorizer.joblib")
    tfidf_matrix = joblib.load("models/tfidf_matrix.joblib")
    return df, vectorizer, tfidf_matrix

df, vectorizer, tfidf_matrix = load_all()

# -------------------- HELPERS --------------------
def safe_image(img_url, width=200):
    """Safely display image or fallback"""
    if isinstance(img_url, str) and img_url.startswith("http"):
        st.image(img_url, width=width)
    else:
        st.image(PLACEHOLDER_IMAGE, width=width)

def recommend(query, top_n=5):
    query_vec = vectorizer.transform([query.lower()])
    sims = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_idx = sims.argsort()[::-1][:top_n]
    return df.iloc[top_idx]

# -------------------- SESSION STATE --------------------
if "details_view" not in st.session_state:
    st.session_state.details_view = False

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

# -------------------- DETAILS PAGE --------------------
def show_details(idx):
    car = df.iloc[idx]

    st.header(car["Car_Name"])
    safe_image(car.get("Image_URL"), width=350)

    st.subheader("Car Specifications")
    st.write(f"**Price:** ₹{car.get('Actual_Price', 'N/A')}")
    st.write(f"**Mileage:** {car.get('Mileage', 'N/A')}")
    st.write(f"**Engine:** {car.get('Engine', 'N/A')}")
    st.write(f"**Seating Capacity:** {car.get('Seating_Capacity', 'N/A')}")
    st.write(f"**Fuel Type:** {car.get('Car_type', 'N/A')}")

    st.subheader("Overview")
    st.write(car.get("overview", "No description available."))

    if st.button("⬅ Back to results"):
        st.session_state.details_view = False
        st.rerun()

# -------------------- ROUTING --------------------
if st.session_state.details_view:
    show_details(st.session_state.selected_index)
    st.stop()

# -------------------- MAIN UI --------------------
st.title("🚗 Car Recommendation System")

query = st.text_input(
    "Describe your car (e.g. EV under 10 lakh, 7-seater diesel SUV)"
)

if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a car description.")
    else:
        results = recommend(query)

        st.subheader("Top Matches")
        results = results.reset_index(drop=False)

        for i, row in results.iterrows():
            col1, col2 = st.columns([1, 2])

            with col1:
                safe_image(row.get("Image_URL"), width=200)

            with col2:
                st.write(f"### {row['Car_Name']}")
                st.write(f"**Price:** ₹{row.get('Actual_Price', 'N/A')}")

                if st.button(
                    f"View Details → {row['Car_Name']}",
                    key=f"details_{i}"
                ):
                    st.session_state.selected_index = row["index"]
                    st.session_state.details_view = True
                    st.rerun()
