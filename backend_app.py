from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from predict import analyze_food_product
import os

app = Flask(__name__)
CORS(app)

# Load data for searching
try:
    df_raw = pd.read_csv('raw_data.csv')
    # Filter to unique products with names and fill NaN values
    df_raw = df_raw.dropna(subset=['product_name']).drop_duplicates(subset=['product_name'])
    df_raw = df_raw.fillna(0)
except Exception as e:
    print(f"Error loading raw_data.csv: {e}")
    df_raw = pd.DataFrame()

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    # Simple search in product names
    matches = df_raw[df_raw['product_name'].str.contains(query, case=False, na=False)].head(10)
    
    results = []
    for _, row in matches.iterrows():
        results.append({
            "name": row['product_name'],
            "features": {
                "energy_100g": row.get('energy_100g', 0),
                "sugars_100g": row.get('sugars_100g', 0),
                "fat_100g": row.get('fat_100g', 0),
                "proteins_100g": row.get('proteins_100g', 0),
                "salt_100g": row.get('salt_100g', 0),
                "fiber_100g": row.get('fiber_100g', 0),
                "carbohydrates_100g": row.get('carbohydrates_100g', 0),
                "saturated_fat_100g": row.get('saturated_fat_100g', 0),
                "nova_group": row.get('nova_group', 2),
                "additives_n": row.get('additives_n', 0),
                "ingredients_from_palm_oil_n": row.get('ingredients_from_palm_oil_n', 0)
            },
            "ingredients": row.get('product_name', '') # Mock ingredients if not available
        })
    
    return jsonify(results)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    features = data.get('features', {})
    ingredients = data.get('ingredients', '')
    
    result = analyze_food_product(features, ingredients)
    
    if "error" in result:
        return jsonify(result), 500
        
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
