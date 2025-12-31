import pandas as pd
import xgboost as xgb
import shap
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

def train():
    # Load Data
    try:
        df = pd.read_csv('credit_data_synthetic.csv')
    except FileNotFoundError:
        print("Data file not found. Run data_gen.py first.")
        return

    # Features & Target
    X = df.drop(['default_flag', 'business_type'], axis=1) # Dropping business_type for simplicity in this V1
    y = df['default_flag']

    # Train Stats
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train XGBoost
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    
    print(f"Model Trained. Accuracy: {acc:.2f}, AUC: {auc:.2f}")

    # Save Model
    joblib.dump(model, 'model.pkl')
    print("Model saved to model.pkl")

    # Save Feature Names
    joblib.dump(X.columns.tolist(), 'model_features.pkl')

if __name__ == "__main__":
    train()
