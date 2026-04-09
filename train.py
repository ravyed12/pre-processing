import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier  
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib


def train_model():
    print("📂 Loading processed_data.csv...")

    try:
        df = pd.read_csv("processed_data.csv")
    except FileNotFoundError:
        print("❌ processed_data.csv not found! Run preprocess.py first.")
        return

    if df.empty:
        print("❌ No data available for training.")
        return

    print(f"📊 Dataset shape: {df.shape}")

    features = [
        "energy_100g",
        "sugars_100g",
        "fat_100g",
        "proteins_100g",
        "salt_100g",
        "fiber_100g",
        "carbohydrates_100g"
    ]

    X = df[features]
    y = df["label"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    joblib.dump(le, "label_encoder.pkl")

    print("🔀 Splitting data (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded
    )

    print("🚀 Training Gradient Boosting...")
    clf = GradientBoostingClassifier(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=3,
        random_state=42
    )

    clf.fit(X_train, y_train)

    print("📈 Evaluating model...")
    y_pred = clf.predict(X_test)

    print("\n" + "="*50)
    print(f"🎯 Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
    print("="*50)

    print("📊 Classification Report:")
    print(classification_report(y_test, y_pred))
    print("="*50)


    importance = pd.Series(clf.feature_importances_, index=features)
    print("\n🔥 Feature Importance:")
    print(importance.sort_values(ascending=False))

    joblib.dump(clf, "model.pkl")

    print("\n💾 Model saved as 'model.pkl'")
    print("💾 Label encoder saved as 'label_encoder.pkl'")


if __name__ == "__main__":
    train_model()