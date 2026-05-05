import pandas as pd
import joblib
from nlp_ingredients import analyze_ingredients

def load_models():
    """Load the trained scaler, label encoder, and stacking model."""
    try:
        model = joblib.load("model.pkl")
        scaler = joblib.load("scaler.pkl")
        le = joblib.load("label_encoder.pkl")
        return model, scaler, le
    except FileNotFoundError as e:
        print(f"Error loading models: {e}")
        print("Please ensure model.pkl, scaler.pkl, and label_encoder.pkl exist.")
        return None, None, None

def analyze_food_product(features_dict, ingredients_text):
    """
    Complete analysis combining ML prediction from features
    and NLP ingredient analysis.
    """
    model, scaler, le = load_models()
    if not model:
        return

    # 1. Feature Engineering (mimicking preprocess.py)
    eps = 1
    
    # Required core features (with defaults if missing)
    energy = features_dict.get("energy_100g", 0)
    sugars = features_dict.get("sugars_100g", 0)
    fat = features_dict.get("fat_100g", 0)
    proteins = features_dict.get("proteins_100g", 0)
    salt = features_dict.get("salt_100g", 0)
    carbs = features_dict.get("carbohydrates_100g", 0)
    fiber = features_dict.get("fiber_100g", 0)
    sat_fat = features_dict.get("saturated_fat_100g", 0)
    
    # Calculate derived features
    features_dict["sugar_energy_ratio"] = sugars / (energy + eps)
    features_dict["fat_energy_ratio"] = fat / (energy + eps)
    features_dict["protein_energy_ratio"] = proteins / (energy + eps)
    features_dict["fiber_carb_ratio"] = fiber / (carbs + eps)
    features_dict["sugar_fiber_ratio"] = sugars / (fiber + eps)
    features_dict["fat_protein_ratio"] = fat / (proteins + eps)
    features_dict["salt_energy_ratio"] = salt / (energy + eps)
    features_dict["sat_fat_ratio"] = sat_fat / (fat + eps)
    features_dict["sat_fat_energy_ratio"] = sat_fat / (energy + eps)
    features_dict["unsat_fat_100g"] = max(0, fat - sat_fat)
    
    features_dict["trans_fat_ratio"] = features_dict.get("trans_fat_100g", 0) / (fat + eps)
    features_dict["sodium_salt_ratio"] = features_dict.get("sodium_100g", 0) / (salt + eps)
    
    micro_sum = (features_dict.get("vitamin_a_100g", 0) + 
                 features_dict.get("vitamin_c_100g", 0) + 
                 features_dict.get("calcium_100g", 0) + 
                 features_dict.get("iron_100g", 0) + 
                 features_dict.get("potassium_100g", 0))
    features_dict["micronutrient_density"] = micro_sum / (energy + eps)
    
    neg_score = sugars + fat + (salt * 10) + sat_fat + (features_dict.get("trans_fat_100g", 0) * 5)
    features_dict["negative_score"] = neg_score
    
    pos_score = proteins + fiber + (features_dict.get("potassium_100g", 0) / 100)
    features_dict["positive_score"] = pos_score
    features_dict["health_balance"] = pos_score - neg_score
    
    # Energy density bin
    if energy <= 600: ed = 0
    elif energy <= 1200: ed = 1
    elif energy <= 2000: ed = 2
    else: ed = 3
    features_dict["energy_density"] = ed
    
    features_dict["has_palm_oil"] = 1 if features_dict.get("ingredients_from_palm_oil_n", 0) > 0 else 0
    
    additives = features_dict.get("additives_n", 0)
    if additives <= 0: ar = 0
    elif additives <= 3: ar = 1
    elif additives <= 7: ar = 2
    else: ar = 3
    features_dict["additives_risk"] = ar

    # Align columns with scaler
    df_features = pd.DataFrame([features_dict])
    expected_cols = scaler.feature_names_in_
    
    # Fill any missing columns with 0
    for col in expected_cols:
        if col not in df_features.columns:
            df_features[col] = 0
            
    df_features = df_features[expected_cols]
    
    # 2. Make Prediction
    X_scaled = scaler.transform(df_features)
    pred_idx = model.predict(X_scaled)[0]
    pred_label = le.inverse_transform([pred_idx])[0]
    pred_probs = model.predict_proba(X_scaled)[0]
    
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)

    print("\n" + "="*60)
    print("[REPORT] FULL FOOD ANALYSIS REPORT")
    print("="*60)
    
    print(f"\n[ML MODEL PREDICTION]: [{pred_label.upper()}]")
    print(f"Confidence: Healthy ({pred_probs[0]*100:.1f}%), Moderate ({pred_probs[1]*100:.1f}%), Unhealthy ({pred_probs[2]*100:.1f}%)")
    
    # 3. NLP Analysis
    print("\n[NLP] INGREDIENTS NLP ANALYSIS:")
    print(f"Text: '{ingredients_text}'")
    print("-" * 60)
    
    nlp_results = analyze_ingredients(ingredients_text)
    for res in nlp_results:
        if res["item"] in ["Clean", "Unknown"]:
            print(f"OK - {res['warning']} ({res['reason']})")
        else:
            detected_str = ", ".join(res.get("detected", []))
            print(f"WARN - {res['item'].upper()} detected ({detected_str})")
            print(f"   -> {res['warning']}")
            print(f"   -> {res['reason']}")
            
    print("="*60 + "\n")

if __name__ == "__main__":
    # Example 1: Unhealthy Product (e.g., Chocolate Bar)
    choc_features = {
        "energy_100g": 2200, "sugars_100g": 55, "fat_100g": 30, "saturated_fat_100g": 18,
        "proteins_100g": 5, "salt_100g": 0.2, "fiber_100g": 3, "carbohydrates_100g": 60,
        "additives_n": 3, "ingredients_from_palm_oil_n": 1
    }
    choc_ingredients = "Sugar, cocoa butter, whole milk powder, palm oil, soy lecithin, artificial flavor, red 40."
    analyze_food_product(choc_features, choc_ingredients)
    
    # Example 2: Healthy Product (e.g., Oatmeal)
    oat_features = {
        "energy_100g": 1500, "sugars_100g": 1.5, "fat_100g": 7, "saturated_fat_100g": 1.2,
        "proteins_100g": 13, "salt_100g": 0.01, "fiber_100g": 10, "carbohydrates_100g": 60,
        "additives_n": 0, "ingredients_from_palm_oil_n": 0
    }
    oat_ingredients = "Whole grain rolled oats."
    analyze_food_product(oat_features, oat_ingredients)
