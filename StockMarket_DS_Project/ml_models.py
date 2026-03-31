"""
ml_models.py
------------
Trains and compares 4 machine learning models to predict
next-day stock price direction (up or down).

Models compared:
  1. Logistic Regression   (baseline)
  2. Random Forest
  3. Gradient Boosting (XGBoost-style via sklearn)
  4. Support Vector Classifier

Output:
  - Model performance comparison table
  - Feature importance chart (Random Forest)
  - ROC curves for all models
  - Confusion matrices
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_auc_score, roc_curve
)
import warnings
import os

warnings.filterwarnings("ignore")
os.makedirs("charts", exist_ok=True)

# ─────────────────────────────────────────────
# 1. Load & Prepare Data
# ─────────────────────────────────────────────
print("=" * 55)
print("  STOCK MARKET DIRECTION PREDICTION — ML PIPELINE")
print("=" * 55)

df = pd.read_csv("data/stocks_features.csv", parse_dates=["date"])
df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

FEATURES = [
    "daily_return", "return_5d", "return_20d",
    "rsi_14", "macd", "macd_hist", "macd_signal",
    "bb_width", "bb_position", "volatility_20d",
    "volume_ratio", "price_vs_sma20", "high_low_range",
    "sma_5", "sma_20", "sma_50",
]
TARGET = "target"

X = df[FEATURES]
y = df[TARGET]

print(f"\nDataset: {len(df):,} rows | {len(FEATURES)} features | {df['ticker'].nunique()} tickers")
print(f"Target balance: {y.mean():.1%} up days\n")

# ─────────────────────────────────────────────
# 2. Train / Test Split (time-aware)
# ─────────────────────────────────────────────
# Use last 20% of data as test set (time series — no random shuffling)
split_idx = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# Scale features
scaler  = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print(f"Train size: {len(X_train):,} | Test size: {len(X_test):,}")

# ─────────────────────────────────────────────
# 3. Define Models
# ─────────────────────────────────────────────
models = {
    "Logistic Regression":    LogisticRegression(max_iter=1000, C=0.1),
    "Random Forest":          RandomForestClassifier(n_estimators=300, max_depth=8,
                                                     min_samples_leaf=20, random_state=42),
    "Gradient Boosting":      GradientBoostingClassifier(n_estimators=200, max_depth=4,
                                                          learning_rate=0.05, random_state=42),
    "Support Vector Machine": SVC(kernel="rbf", C=1.0, probability=True),
}

# ─────────────────────────────────────────────
# 4. Train & Evaluate
# ─────────────────────────────────────────────
results = {}
trained_models = {}

tscv = TimeSeriesSplit(n_splits=5)

print("\nTraining models...\n")
for name, model in models.items():
    print(f"  [{name}]")

    # Cross-val on training set (time-series aware)
    cv_scores = cross_val_score(
        model, X_train_scaled, y_train, cv=tscv, scoring="accuracy"
    )

    # Fit on full training set
    model.fit(X_train_scaled, y_train)
    y_pred      = model.predict(X_test_scaled)
    y_prob      = model.predict_proba(X_test_scaled)[:, 1]
    test_acc    = accuracy_score(y_test, y_pred)
    roc_auc     = roc_auc_score(y_test, y_prob)

    results[name] = {
        "CV Accuracy (mean)": cv_scores.mean(),
        "CV Accuracy (std)":  cv_scores.std(),
        "Test Accuracy":      test_acc,
        "ROC-AUC":            roc_auc,
    }
    trained_models[name] = (model, y_pred, y_prob)
    print(f"    CV Acc: {cv_scores.mean():.3f} ± {cv_scores.std():.3f} | "
          f"Test Acc: {test_acc:.3f} | AUC: {roc_auc:.3f}")

# ─────────────────────────────────────────────
# 5. Results Table
# ─────────────────────────────────────────────
results_df = pd.DataFrame(results).T.round(4)
print("\n" + "=" * 55)
print("  MODEL COMPARISON RESULTS")
print("=" * 55)
print(results_df.to_string())

best_model = results_df["ROC-AUC"].idxmax()
print(f"\nBest model by ROC-AUC: {best_model}")

# Detailed report for best model
best_pred = trained_models[best_model][1]
print(f"\nClassification Report — {best_model}:")
print(classification_report(y_test, best_pred, target_names=["Down", "Up"]))

# ─────────────────────────────────────────────
# 6. Charts
# ─────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#c9d1d9",
    "text.color":       "#c9d1d9",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "grid.color":       "#21262d",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
})

COLORS = ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff"]

# Chart A: ROC Curves
fig, ax = plt.subplots(figsize=(8, 6))
for i, (name, (model, pred, prob)) in enumerate(trained_models.items()):
    fpr, tpr, _ = roc_curve(y_test, prob)
    auc = roc_auc_score(y_test, prob)
    ax.plot(fpr, tpr, color=COLORS[i], linewidth=2, label=f"{name} (AUC={auc:.3f})")

ax.plot([0, 1], [0, 1], "w--", linewidth=0.8, alpha=0.5, label="Random")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curves — All Models", fontsize=13)
ax.legend(loc="lower right", fontsize=9)
ax.grid(True)
plt.tight_layout()
plt.savefig("charts/07_roc_curves.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nSaved charts/07_roc_curves.png")

# Chart B: Feature Importance (Random Forest)
rf_model = trained_models["Random Forest"][0]
importances = pd.Series(rf_model.feature_importances_, index=FEATURES).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(9, 7))
colors = ["#3fb950" if v > importances.median() else "#58a6ff" for v in importances]
ax.barh(importances.index, importances.values, color=colors)
ax.set_title("Random Forest — Feature Importances", fontsize=13)
ax.set_xlabel("Importance Score")
ax.grid(True, axis="x")
plt.tight_layout()
plt.savefig("charts/08_feature_importance.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved charts/08_feature_importance.png")

# Chart C: Confusion Matrices (2x2 grid)
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes = axes.flatten()
for i, (name, (model, pred, prob)) in enumerate(trained_models.items()):
    cm = confusion_matrix(y_test, pred)
    im = axes[i].imshow(cm, cmap="Blues")
    axes[i].set_title(name, fontsize=10)
    axes[i].set_xticks([0, 1]); axes[i].set_xticklabels(["Down", "Up"])
    axes[i].set_yticks([0, 1]); axes[i].set_yticklabels(["Down", "Up"])
    axes[i].set_xlabel("Predicted"); axes[i].set_ylabel("Actual")
    for r in range(2):
        for c in range(2):
            axes[i].text(c, r, str(cm[r, c]), ha="center", va="center",
                         color="white", fontsize=13, fontweight="bold")

fig.suptitle("Confusion Matrices — All Models", fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig("charts/09_confusion_matrices.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved charts/09_confusion_matrices.png")

# Chart D: Model Accuracy Comparison Bar Chart
fig, ax = plt.subplots(figsize=(9, 5))
model_names = list(results.keys())
test_accs   = [results[m]["Test Accuracy"] for m in model_names]
roc_aucs    = [results[m]["ROC-AUC"] for m in model_names]

x = np.arange(len(model_names))
w = 0.35
ax.bar(x - w/2, test_accs, w, label="Test Accuracy", color="#58a6ff", alpha=0.9)
ax.bar(x + w/2, roc_aucs,  w, label="ROC-AUC",       color="#3fb950", alpha=0.9)
ax.set_xticks(x)
ax.set_xticklabels([m.replace(" ", "\n") for m in model_names], fontsize=9)
ax.set_ylim(0.4, 0.75)
ax.set_ylabel("Score")
ax.set_title("Model Performance Comparison", fontsize=13)
ax.legend()
ax.grid(True, axis="y")
plt.tight_layout()
plt.savefig("charts/10_model_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved charts/10_model_comparison.png")

print("\nML pipeline complete. All results and charts saved.")
