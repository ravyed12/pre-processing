import requests
import pandas as pd
import time
import random

def fetch_data():
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    all_products = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    pages = list(range(1, 50))
    failed_pages = []

    for page in pages:
        success = fetch_page(page, url, headers, all_products)

        if not success:
            failed_pages.append(page)

    if failed_pages:
        print(f"\n🔁 Retrying failed pages: {failed_pages}")
        time.sleep(5)

        for page in failed_pages:
            fetch_page(page, url, headers, all_products)

    save_data(all_products)


def fetch_page(page, url, headers, all_products):
    params = {
        "search_terms": "food",
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page": page,
        "page_size": 100,
        "fields": "product_name,nutriments,nutrition_grade_fr,nutriscore_grade"
    }

    print(f"\n📄 Fetching page {page}...")

    MAX_RETRIES = 5

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 503:
                raise Exception("503 Server Busy")

            response.raise_for_status()

            data = response.json()
            products = data.get("products", [])

            print(f"✅ Products fetched: {len(products)}")

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
                "energy_100g": nutrients.get("energy_100g"),
                "sugars_100g": nutrients.get("sugars_100g"),
                "fat_100g": nutrients.get("fat_100g"),
                "proteins_100g": nutrients.get("proteins_100g"),
                "salt_100g": nutrients.get("salt_100g"),
                "fiber_100g": nutrients.get("fiber_100g"),             
                "carbohydrates_100g": nutrients.get("carbohydrates_100g"), 
                "nutrition_grade": grade
                })

            return True 

        except Exception as e:
            wait = random.uniform(2, 6) * (attempt + 1)
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
            print(f"⏳ Waiting {wait:.1f}s...")
            time.sleep(wait)

    print(f"❌ Failed to fetch page {page}")
    return False


def save_data(all_products):
    df = pd.DataFrame(all_products)

    print(f"\n📊 Total raw records: {len(df)}")

    if df.empty:
        print("❌ No data collected.")
        return

    df.dropna(subset=[
        "energy_100g",
        "sugars_100g",
        "fat_100g",
        "proteins_100g",
        "salt_100g"
    ], how="all", inplace=True)

    print(f"🧹 After cleaning: {len(df)}")

    df.to_csv("raw_data.csv", index=False)
    print("💾 Saved to raw_data.csv")


if __name__ == "__main__":
    fetch_data()