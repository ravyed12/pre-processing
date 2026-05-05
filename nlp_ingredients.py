import re

def analyze_ingredients(text):
    """
    Analyzes the ingredients text and detects harmful or noteworthy items.
    Returns a list of dictionaries with warnings and reasons.
    """
    if not isinstance(text, str) or not text.strip():
        return [{"item": "Unknown", "warning": "No ingredient text provided", "reason": "Cannot analyze missing ingredients"}]

    text_lower = text.lower()
    findings = []

    # 1. Sugars and Sweeteners
    sugar_keywords = [
        "sugar", "syrup", "fructose", "glucose", "sucrose", "dextrose", 
        "maltose", "honey", "molasses", "nectar", "caramel"
    ]
    found_sugars = [s for s in sugar_keywords if s in text_lower]
    if found_sugars:
        findings.append({
            "item": "Added Sugars",
            "detected": found_sugars,
            "warning": "High Sugar Content",
            "reason": "Excessive sugar consumption is linked to obesity, diabetes, and heart disease."
        })

    # 2. Palm Oil
    if "palm oil" in text_lower or "palmolein" in text_lower:
        findings.append({
            "item": "Palm Oil",
            "detected": ["palm oil" if "palm oil" in text_lower else "palmolein"],
            "warning": "High Saturated Fat & Environmental Impact",
            "reason": "Palm oil is high in saturated fats which can raise cholesterol. Its production is also linked to deforestation."
        })

    # 3. Trans Fats / Hydrogenated Oils
    trans_fat_keywords = ["partially hydrogenated", "hydrogenated oil", "shortening"]
    found_trans = [t for t in trans_fat_keywords if t in text_lower]
    if found_trans:
        findings.append({
            "item": "Trans Fats",
            "detected": found_trans,
            "warning": "Harmful Trans Fats Detected",
            "reason": "Trans fats increase bad cholesterol (LDL) and lower good cholesterol (HDL), significantly increasing heart disease risk."
        })

    # 4. Preservatives & Additives
    preservative_keywords = [
        "nitrate", "nitrite", "benzoate", "sorbate", "bha", "bht", 
        "sulfite", "sulphite", "msg", "monosodium glutamate", "e2", "e3"
    ]
    found_preservatives = [p for p in preservative_keywords if p in text_lower or re.search(rf'\b{p}\b', text_lower)]
    if found_preservatives:
        findings.append({
            "item": "Preservatives / Additives",
            "detected": found_preservatives,
            "warning": "Chemical Preservatives Present",
            "reason": "Certain synthetic preservatives and additives may cause allergic reactions or have long-term health concerns."
        })

    # 5. Artificial Colors/Dyes
    dye_keywords = ["red 40", "yellow 5", "yellow 6", "blue 1", "color", "dye", "lake"]
    found_dyes = [d for d in dye_keywords if d in text_lower]
    if found_dyes:
        findings.append({
            "item": "Artificial Colors",
            "detected": found_dyes,
            "warning": "Artificial Dyes Detected",
            "reason": "Some artificial food colors have been linked to hyperactivity in children and other health issues."
        })
        
    # 6. High Sodium / Salt
    sodium_keywords = ["salt", "sodium chloride", "monosodium glutamate", "baking soda", "sodium bicarbonate"]
    found_sodium = [s for s in sodium_keywords if s in text_lower]
    if found_sodium:
        findings.append({
            "item": "Sodium Sources",
            "detected": found_sodium,
            "warning": "Potential High Sodium",
            "reason": "High sodium intake is a major risk factor for hypertension and cardiovascular diseases."
        })

    if not findings:
        findings.append({
            "item": "Clean",
            "warning": "No major harmful ingredients detected.",
            "reason": "The ingredient list does not contain common harmful additives, sugars, or unhealthy oils based on our current filters."
        })

    return findings

def print_analysis(text):
    print(f"\n[Analysis] Analyzing Ingredients: '{text}'")
    print("-" * 50)
    results = analyze_ingredients(text)
    for res in results:
        if res["item"] == "Clean" or res["item"] == "Unknown":
            print(f"OK - {res['item']}: {res['warning']} ({res['reason']})")
        else:
            detected_str = ", ".join(res.get("detected", []))
            print(f"WARN - {res['item']} ({detected_str})")
            print(f"   Warning: {res['warning']}")
            print(f"   Reason:  {res['reason']}")
    print("-" * 50)

if __name__ == "__main__":
    # Test cases
    test_ingredients_1 = "Whole wheat flour, sugar, partially hydrogenated soybean oil, high fructose corn syrup, salt, sodium benzoate, Red 40"
    test_ingredients_2 = "Organic oats, almonds, honey, dried cranberries"
    test_ingredients_3 = "Water, palm oil, MSG, artificial flavor, yellow 5"
    
    print_analysis(test_ingredients_1)
    print_analysis(test_ingredients_2)
    print_analysis(test_ingredients_3)
