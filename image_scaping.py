from ddgs import DDGS
import pandas as pd
import numpy as np
import time

INPUT_CSV = "data_files/all_segment_cars.csv"
OUTPUT_CSV = "data_files/cars_with_images.csv"
FETCH_LIMIT = None
DELAY_SECONDS = 3

EXPECTED_COLUMNS = [
    "Price_Category",
    "Car_Name",
    "Actual_Price",
    "Mileage",
    "Engine",
    "Seating_Capacity",
    "Image_URL"
]

def fetch_image(car_name):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(
                query=f"{car_name} car",
                max_results=1
            ))
            if results:
                return results[0]["image"]
    except Exception as e:
        print(f"❌ Error fetching {car_name}: {e}")
    return None

def main():
    print("📄 Loading CSV...")
    df = pd.read_csv(INPUT_CSV)

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df["Image_URL"] = df["Image_URL"].astype(str)

    missing_df = df[
        (df["Image_URL"].isin(["", "nan"])) &
        (df["Car_Name"].notna())
    ]

    if FETCH_LIMIT:
        missing_df = missing_df.head(FETCH_LIMIT)

    total = len(missing_df)

    if total == 0:
        print("✅ No valid rows found for image fetching.")
        return

    print(f"🖼️ Fetching images for {total} cars...\n")

    for i, (idx, row) in enumerate(missing_df.iterrows(), start=1):
        car_name = str(row["Car_Name"]).strip()

        if not car_name or car_name.lower() == "nan":
            print(f"⚠️ Skipping invalid car name at row {idx}")
            continue

        print(f"🔍 {i}/{total} Fetching: {car_name}")

        image_url = fetch_image(car_name)

        if image_url:
            df.at[idx, "Image_URL"] = image_url
        else:
            print(f"⚠️ No image found for {car_name}")

        time.sleep(DELAY_SECONDS)

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Image pipeline completed. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
