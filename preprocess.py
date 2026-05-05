import pandas as pd
import numpy as np


def preprocess():
    print("Loading raw_data.csv...", flush=True)

    try:
        df = pd.read_csv("raw_data.csv")
    except FileNotFoundError:
        print("ERROR: raw_data.csv not found! Run fetch_data.py first.")
        return

    print(f"Initial shape: {df.shape}", flush=True)

    # ═══════════════════════════════════════════════════════════════════
    # COLUMN GROUPS — must match what fetch_data.py collects
    # ═══════════════════════════════════════════════════════════════════

    # Core nutrients (rows dropped if these are ALL missing)
    core_numeric = [
        "energy_100g",
        "sugars_100g",
        "fat_100g",
        "proteins_100g",
        "salt_100g",
    ]

    # Extended macronutrients (imputed with median if missing)
    extended_macro = [
        "saturated_fat_100g",
        "sodium_100g",
        "fiber_100g",
        "carbohydrates_100g",
        "trans_fat_100g",
        "cholesterol_100g",
    ]

    # Micronutrients / vitamins / minerals (imputed with 0 if missing)
    micro_nutrients = [
        "vitamin_a_100g",
        "vitamin_c_100g",
        "calcium_100g",
        "iron_100g",
        "potassium_100g",
    ]

    # Food quality indicators (imputed)
    quality_indicators = [
        "nova_group",
        "additives_n",
        "ingredients_from_palm_oil_n",
    ]

    all_numeric = core_numeric + extended_macro + micro_nutrients + quality_indicators

    # ═══════════════════════════════════════════════════════════════════
    # STEP 1: Numeric conversion
    # ═══════════════════════════════════════════════════════════════════
    for col in all_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ═══════════════════════════════════════════════════════════════════
    # STEP 2: Filter valid nutrition grades
    # ═══════════════════════════════════════════════════════════════════
    df["nutrition_grade"] = (
        df["nutrition_grade"].astype(str).str.lower().str.strip()
    )
    valid_grades = ["a", "b", "c", "d", "e"]
    df = df[df["nutrition_grade"].isin(valid_grades)]
    print(f"After filtering valid grades: {df.shape}", flush=True)

    # ═══════════════════════════════════════════════════════════════════
    # STEP 3: Drop rows missing core nutrients
    # ═══════════════════════════════════════════════════════════════════
    df = df.dropna(subset=core_numeric)
    print(f"After dropping rows missing core nutrients: {df.shape}", flush=True)

    # ═══════════════════════════════════════════════════════════════════
    # STEP 4: Imputation
    # ═══════════════════════════════════════════════════════════════════

    # Extended macros → median imputation (they have reasonable distributions)
    for col in extended_macro:
        if col in df.columns:
            med = df[col].median()
            df[col] = df[col].fillna(med if not pd.isna(med) else 0)

    # Micronutrients → fill with 0 (absence = not reported = assume 0)
    for col in micro_nutrients:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Quality indicators → specific defaults
    if "nova_group" in df.columns:
        df["nova_group"] = df["nova_group"].fillna(2).clip(1, 4)
    if "additives_n" in df.columns:
        df["additives_n"] = df["additives_n"].fillna(0).clip(0, 30)
    if "ingredients_from_palm_oil_n" in df.columns:
        df["ingredients_from_palm_oil_n"] = df["ingredients_from_palm_oil_n"].fillna(0)

    print(f"After imputation: {df.shape}", flush=True)

    # ═══════════════════════════════════════════════════════════════════
    # STEP 5: Outlier removal (IQR on key columns only)
    # ═══════════════════════════════════════════════════════════════════
    iqr_cols = core_numeric + ["fiber_100g", "carbohydrates_100g", "saturated_fat_100g"]
    for col in iqr_cols:
        if col not in df.columns:
            continue
        Q1 = df[col].quantile(0.02)
        Q3 = df[col].quantile(0.98)
        IQR = Q3 - Q1
        lower = max(0, Q1 - 1.5 * IQR)
        upper = Q3 + 1.5 * IQR
        df = df[(df[col] >= lower) & (df[col] <= upper)]

    print(f"After IQR outlier removal: {df.shape}", flush=True)

    # ═══════════════════════════════════════════════════════════════════
    # STEP 6: Create labels from nutrition grade
    # ═══════════════════════════════════════════════════════════════════
    def map_grade(grade):
        if grade in ["a", "b"]:
            return "Healthy"
        elif grade == "c":
            return "Moderate"
        else:
            return "Unhealthy"

    df["label"] = df["nutrition_grade"].apply(map_grade)

    # ═══════════════════════════════════════════════════════════════════
    # STEP 7: Feature Engineering
    # ═══════════════════════════════════════════════════════════════════
    eps = 1  # avoid division by zero

    # --- Ratio features (capture Nutri-Score relationships) ---
    df["sugar_energy_ratio"] = df["sugars_100g"] / (df["energy_100g"] + eps)
    df["fat_energy_ratio"] = df["fat_100g"] / (df["energy_100g"] + eps)
    df["protein_energy_ratio"] = df["proteins_100g"] / (df["energy_100g"] + eps)
    df["fiber_carb_ratio"] = df["fiber_100g"] / (df["carbohydrates_100g"] + eps)
    df["sugar_fiber_ratio"] = df["sugars_100g"] / (df["fiber_100g"] + eps)
    df["fat_protein_ratio"] = df["fat_100g"] / (df["proteins_100g"] + eps)
    df["salt_energy_ratio"] = df["salt_100g"] / (df["energy_100g"] + eps)

    # --- Saturated fat features (critical for Nutri-Score) ---
    if "saturated_fat_100g" in df.columns:
        df["sat_fat_ratio"] = df["saturated_fat_100g"] / (df["fat_100g"] + eps)
        df["sat_fat_energy_ratio"] = df["saturated_fat_100g"] / (df["energy_100g"] + eps)
        df["unsat_fat_100g"] = (df["fat_100g"] - df["saturated_fat_100g"]).clip(lower=0)

    # --- Trans fat feature ---
    if "trans_fat_100g" in df.columns:
        df["trans_fat_ratio"] = df["trans_fat_100g"] / (df["fat_100g"] + eps)

    # --- Sodium / salt consistency ---
    if "sodium_100g" in df.columns:
        df["sodium_salt_ratio"] = df["sodium_100g"] / (df["salt_100g"] + eps)

    # --- Micronutrient density (higher = more nutritious per calorie) ---
    micro_sum = 0
    for col in micro_nutrients:
        if col in df.columns:
            micro_sum = micro_sum + df[col]
    if not isinstance(micro_sum, int):
        df["micronutrient_density"] = micro_sum / (df["energy_100g"] + eps)

    # --- Composite Nutri-Score-like scores ---
    neg_parts = df["sugars_100g"] + df["fat_100g"] + df["salt_100g"] * 10
    if "saturated_fat_100g" in df.columns:
        neg_parts = neg_parts + df["saturated_fat_100g"]
    if "trans_fat_100g" in df.columns:
        neg_parts = neg_parts + df["trans_fat_100g"] * 5
    df["negative_score"] = neg_parts

    pos_parts = df["proteins_100g"] + df["fiber_100g"]
    if "potassium_100g" in df.columns:
        # Normalize potassium (mg) to a scale comparable to grams
        df["positive_score"] = pos_parts + df["potassium_100g"] / 100
    else:
        df["positive_score"] = pos_parts

    df["health_balance"] = df["positive_score"] - df["negative_score"]

    # --- Energy density category ---
    df["energy_density"] = pd.cut(
        df["energy_100g"],
        bins=[0, 600, 1200, 2000, 5000],
        labels=[0, 1, 2, 3],
    ).astype(float).fillna(1)

    # --- Palm oil binary flag ---
    if "ingredients_from_palm_oil_n" in df.columns:
        df["has_palm_oil"] = (df["ingredients_from_palm_oil_n"] > 0).astype(int)

    # --- Additives risk level ---
    if "additives_n" in df.columns:
        df["additives_risk"] = pd.cut(
            df["additives_n"],
            bins=[-1, 0, 3, 7, 100],
            labels=[0, 1, 2, 3],
        ).astype(float).fillna(0)

    # ═══════════════════════════════════════════════════════════════════
    # STEP 8: Drop non-feature columns & save
    # ═══════════════════════════════════════════════════════════════════
    drop_cols = ["nutrition_grade", "product_name", "ingredients_from_palm_oil_n"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    df.to_csv("processed_data.csv", index=False)

    feature_cols = [c for c in df.columns if c != "label"]
    print(f"\nSaved as processed_data.csv", flush=True)
    print(f"Final shape: {df.shape}", flush=True)
    print(f"Total features: {len(feature_cols)}", flush=True)
    print(f"\nClass distribution:", flush=True)
    print(df["label"].value_counts(), flush=True)
    print(f"\nAll features ({len(feature_cols)}):", flush=True)
    for i, col in enumerate(feature_cols, 1):
        print(f"  {i:2d}. {col}", flush=True)


if __name__ == "__main__":
    preprocess()