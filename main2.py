import pandas as pd
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

INPUT_EXCEL = "data_files/titu.xlsx"
OUTPUT_CSV = "data_files/cars_prepared.csv"

def clean_price(price):
    price = str(price).lower().strip()
    if "crore" in price:
        num = float(re.findall(r"[\d\.]+", price)[0])
        return num * 10_000_000
    if "lakh" in price:
        num = float(re.findall(r"[\d\.]+", price)[0])
        return num * 100_000
    if re.findall(r"[\d\.]+", price):
        return float(re.findall(r"[\d\.]+", price)[0])
    return 0

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def main():
    print("📄 Loading Excel file...")
    df = pd.read_excel(INPUT_EXCEL, header=None)

    df.columns = [
        "Price_Category",
        "Car_Name",
        "Actual_Price",
        "Mileage",
        "Engine",
        "Seating_Capacity",
        "Image_URL",
        "Car_type"
    ]

    print("🧠 Creating overview text...")
    df["overview"] = df.apply(
        lambda row: " ".join([str(row[c]) for c in [
            "Price_Category",
            "Car_Name",
            "Actual_Price",
            "Mileage",
            "Engine",
            "Seating_Capacity",
            "Car_type"
        ] if pd.notnull(row[c]) and str(row[c]).strip() != ""]),
        axis=1
    )

    print("🧹 Cleaning text...")
    df["overview_clean"] = df["overview"].apply(clean_text)

    print("💰 Normalizing prices...")
    df["Price_Num"] = df["Actual_Price"].apply(clean_price)

    print("📐 Building TF-IDF matrix...")
    vectorizer = TfidfVectorizer(stop_words="english", max_features=15000)
    tfidf_matrix = vectorizer.fit_transform(df["overview_clean"])

    print("💾 Saving outputs...")
    df.to_csv(OUTPUT_CSV, index=False)
    joblib.dump(vectorizer, "models/vectorizer.joblib")
    joblib.dump(tfidf_matrix, "models/tfidf_matrix.joblib")

    print("\n✅ Data preparation completed")
    print("Files created:")
    print(" - data_files/cars_prepared.csv")
    print(" - models/vectorizer.joblib")
    print(" - models/tfidf_matrix.joblib")

if __name__ == "__main__":
    main()
