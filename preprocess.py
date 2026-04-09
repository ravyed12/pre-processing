import pandas as pd
def preprocess():
    print("📂 Loading raw_data.csv...")
    try:
        df = pd.read_csv("raw_data.csv")
    except FileNotFoundError:
        print("❌ raw_data.csv not found! Run fetch_data.py first.")
        return

    print(f"📊 Initial shape: {df.shape}")
    numeric_cols = [
    "energy_100g",
    "sugars_100g",
    "fat_100g",
    "proteins_100g",
    "salt_100g",
    "fiber_100g",              
    "carbohydrates_100g"       
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df["nutrition_grade"] = (
        df["nutrition_grade"]
        .astype(str)
        .str.lower()
        .str.strip())
    valid_grades = ["a", "b", "c", "d", "e"]
    df = df[df["nutrition_grade"].isin(valid_grades)]

    print(f"✅ After filtering valid grades: {df.shape}")

    
    df = df.dropna(subset=numeric_cols)

    print(f"🧹 After dropping NaNs: {df.shape}")

    df = df[
    (df["energy_100g"] >= 0) & (df["energy_100g"] <= 4000) &
    (df["sugars_100g"] >= 0) & (df["sugars_100g"] <= 100) &
    (df["fat_100g"] >= 0) & (df["fat_100g"] <= 100) &
    (df["proteins_100g"] >= 0) & (df["proteins_100g"] <= 100) &
    (df["salt_100g"] >= 0) & (df["salt_100g"] <= 100) &
    (df["fiber_100g"] >= 0) & (df["fiber_100g"] <= 50) &               
    (df["carbohydrates_100g"] >= 0) & (df["carbohydrates_100g"] <= 100) 
    ]

    print(f"⚖️ After removing outliers: {df.shape}")


    def map_grade(grade):
        if grade in ["a", "b"]:
            return "Healthy"
        elif grade == "c":
            return "Moderate"
        else:
            return "Unhealthy"

    df["label"] = df["nutrition_grade"].apply(map_grade)

    df = df.drop(columns=["nutrition_grade", "product_name"], errors="ignore")

    df.to_csv("processed_data.csv", index=False)

    print("\n💾 Saved as processed_data.csv")
    print(f"📊 Final shape: {df.shape}")


    print("\n📊 Class distribution:")
    print(df["label"].value_counts())


if __name__ == "__main__":
    preprocess()