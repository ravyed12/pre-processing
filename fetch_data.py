import requests
import pandas as pd
import time
import random
import sys


def fetch_data():
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    all_products = []

    headers = {
        "User-Agent": "FoodAnalyzer/1.0 (academic project)"
    }

    # 50 pages x 100 products = up to 5000 products
    pages = list(range(1, 51))
    failed_pages = []

    for page in pages:
        success = fetch_page(page, url, headers, all_products)

        if not success:
            failed_pages.append(page)

    if failed_pages:
        print(f"\nRetrying {len(failed_pages)} failed pages...", flush=True)
        time.sleep(5)

        for page in failed_pages:
            fetch_page(page, url, headers, all_products)

    save_data(all_products)


def fetch_page(page, url, headers, all_products):
    # Comprehensive nutrient fields for a full-fledged food analyzer
    params = {
        "search_terms": "food",
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page": page,
        "page_size": 100,
        "fields": ",".join([
            "product_name",
            "nutriments",
            "nutrition_grade_fr",
            "nutriscore_grade",
            "nova_group",
            "additives_n",
            "ingredients_from_palm_oil_n",
        ]),
    }

    print(f"Fetching page {page}/50...", end=" ", flush=True)

    MAX_RETRIES = 4

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 503:
                raise Exception("503 Server Busy")

            response.raise_for_status()

            data = response.json()
            products = data.get("products", [])

            print(f"got {len(products)} products (total: {len(all_products)})", flush=True)

            if not products:
                return True

            for p in products:
                nutrients = p.get("nutriments", {})

                if not p.get("product_name"):
                    continue

                grade = (
                    p.get("nutrition_grade_fr")
                    or p.get("nutriscore_grade")
                    or ""
                )

                all_products.append({
                    "product_name": p.get("product_name", ""),
                    # ── Core macronutrients ──
                    "energy_100g": nutrients.get("energy_100g"),
                    "sugars_100g": nutrients.get("sugars_100g"),
                    "fat_100g": nutrients.get("fat_100g"),
                    "saturated_fat_100g": nutrients.get("saturated-fat_100g"),
                    "proteins_100g": nutrients.get("proteins_100g"),
                    "salt_100g": nutrients.get("salt_100g"),
                    "sodium_100g": nutrients.get("sodium_100g"),
                    "fiber_100g": nutrients.get("fiber_100g"),
                    "carbohydrates_100g": nutrients.get("carbohydrates_100g"),
                    # ── Additional nutrients ──
                    "trans_fat_100g": nutrients.get("trans-fat_100g"),
                    "cholesterol_100g": nutrients.get("cholesterol_100g"),
                    "vitamin_a_100g": nutrients.get("vitamin-a_100g"),
                    "vitamin_c_100g": nutrients.get("vitamin-c_100g"),
                    "calcium_100g": nutrients.get("calcium_100g"),
                    "iron_100g": nutrients.get("iron_100g"),
                    "potassium_100g": nutrients.get("potassium_100g"),
                    # ── Food quality indicators ──
                    "nova_group": p.get("nova_group"),
                    "additives_n": p.get("additives_n"),
                    "ingredients_from_palm_oil_n": p.get("ingredients_from_palm_oil_n"),
                    "nutrition_grade": grade,
                })

            return True

        except Exception as e:
            wait = random.uniform(1, 3) * (attempt + 1)
            print(f"retry {attempt+1}/{MAX_RETRIES} ({e})...", end=" ", flush=True)
            time.sleep(wait)

    print("FAILED", flush=True)
    return False


def save_data(all_products):
    df = pd.DataFrame(all_products)

    print(f"\nTotal raw records: {len(df)}", flush=True)

    if df.empty:
        print("ERROR: No data collected.")
        return

    # Drop rows missing ALL core nutrients
    core_cols = ["energy_100g", "sugars_100g", "fat_100g", "proteins_100g", "salt_100g"]
    df.dropna(subset=core_cols, how="all", inplace=True)

    print(f"After cleaning: {len(df)}", flush=True)

    df.to_csv("raw_data.csv", index=False)
    print("Saved to raw_data.csv", flush=True)


if __name__ == "__main__":
    fetch_data()