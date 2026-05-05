import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import (
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib


def train_model():
    print("Loading processed_data.csv...")

    try:
        df = pd.read_csv("processed_data.csv")
    except FileNotFoundError:
        print("ERROR: processed_data.csv not found! Run preprocess.py first.")
        return

    if df.empty:
        print("ERROR: No data available for training.")
        return

    print(f"Dataset shape: {df.shape}")

    # ── All features (original + engineered) ────────────────────────────
    features = [c for c in df.columns if c != "label"]
    print(f"Using {len(features)} features: {features}")

    X = df[features]
    y = df["label"]

    # ── Encode labels ───────────────────────────────────────────────────
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    joblib.dump(le, "label_encoder.pkl")

    # ── Feature Scaling ─────────────────────────────────────────────────
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=features, index=X.index)
    joblib.dump(scaler, "scaler.pkl")

    # ── Train/Test split ────────────────────────────────────────────────
    print("Splitting data (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded,
    )

    # ── Build individual models ─────────────────────────────────────────
    print("\nTraining ensemble of 3 models...")

    gb = GradientBoostingClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        subsample=0.8,
        max_features="sqrt",
        random_state=42,
    )

    hgb = HistGradientBoostingClassifier(
        max_iter=400,
        learning_rate=0.05,
        max_depth=7,
        min_samples_leaf=10,
        l2_regularization=0.1,
        random_state=42,
    )

    rf = RandomForestClassifier(
        n_estimators=400,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=3,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    # ── Soft-Voting Ensemble ────────────────────────────────────────────
    ensemble = VotingClassifier(
        estimators=[("gb", gb), ("hgb", hgb), ("rf", rf)],
        voting="soft",
        weights=[2, 2, 1],  # boosting models get higher weight
    )

    ensemble.fit(X_train, y_train)

    # ── Evaluate on test set ────────────────────────────────────────────
    print("\nEvaluating model...")
    y_pred = ensemble.predict(X_test)

    acc = accuracy_score(y_test, y_pred) * 100
    print("\n" + "=" * 50)
    print(f"ACCURACY: {acc:.2f}%")
    print("=" * 50)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    print("=" * 50)

    # ── Cross-Validation score ──────────────────────────────────────────
    print("\nRunning 5-fold Cross-Validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(ensemble, X_scaled, y_encoded, cv=cv, scoring="accuracy")
    print(f"CV Scores: {[round(s*100, 2) for s in cv_scores]}")
    print(f"CV Mean:   {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")

    # ── Individual model performance (for insight) ──────────────────────
    print("\n--- Individual Model Accuracy ---")
    for name, model in ensemble.named_estimators_.items():
        y_ind = model.predict(X_test)
        ind_acc = accuracy_score(y_test, y_ind) * 100
        print(f"  {name:>4s}: {ind_acc:.2f}%")

    # ── Feature importance (from GradientBoosting) ──────────────────────
    importance = pd.Series(
        ensemble.named_estimators_["gb"].feature_importances_, index=features
    )
    print("\nTop Feature Importance:")
    print(importance.sort_values(ascending=False).head(12))

    # ── Save model ──────────────────────────────────────────────────────
    joblib.dump(ensemble, "model.pkl")

    print("\nModel saved as 'model.pkl'")
    print("Label encoder saved as 'label_encoder.pkl'")
    print("Scaler saved as 'scaler.pkl'")


if __name__ == "__main__":
    train_model()