import streamlit as st
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity

@st.cache_data
def load_all():
    df = pd.read_csv("data_files/cars_prepared.csv")
    vectorizer = joblib.load("models/vectorizer.joblib")
    tfidf_matrix = joblib.load("models/tfidf_matrix.joblib")
    return df, vectorizer, tfidf_matrix

df, vectorizer, tfidf_matrix = load_all()

def recommend(query, top_n=5):
    query = query.lower()
    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_idx = sims.argsort()[::-1][:top_n]
    return df.iloc[top_idx]

if "details_view" not in st.session_state:
    st.session_state.details_view = False

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

def show_details(idx):
    car = df.iloc[idx]
    st.header(car["Car_Name"])
    st.image(car["Image_URL"], width=350)
    st.subheader("Car Specifications")
    st.write(f"**Price:** ₹{car['Actual_Price']}")
    st.write(f"**Mileage:** {car['Mileage']}")
    st.write(f"**Engine:** {car['Engine']}")
    st.write(f"**Seating:** {car['Seating_Capacity']}")
    st.write(f"**Fuel Type:** {car['Car_type']}")
    st.subheader("Overview")
    st.write(car["overview"])
    if st.button("⬅ Back"):
        st.session_state.details_view = False
        st.rerun()

if st.session_state.details_view:
    show_details(st.session_state.selected_index)
    st.stop()

st.title("🚗 Car Recommendation System")
query = st.text_input("Write what you want (e.g. EV under 10 lakh, 7 seater diesel)")

if st.button("Search"):
    if not query.strip():
        st.warning("Please type something")
    else:
        results = recommend(query)
        st.subheader("Top Matches")
        results = results.reset_index(drop=True)
        for i, row in results.iterrows():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(row["Image_URL"], width=200)
            with col2:
                st.write(f"### {row['Car_Name']}")
                st.write(f"**Price:** ₹{row['Actual_Price']}")
                if st.button(f"View Details → {row['Car_Name']}", key=f"btn_{i}"):
                    st.session_state.selected_index = row.name
                    st.session_state.details_view = True
                    st.rerun()
