import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
from fpdf import FPDF
import os

def generate_report():
    print("Generating Reporting Artifacts...")
    
    # Load Metrics
    try:
        with open("model/training_metrics.json", "r") as f:
            metrics = json.load(f)
        with open("data/validation_log.json", "r") as f:
            validation = json.load(f)
        try:
            with open("data/bias_report.json", "r") as f:
                bias_audit = json.load(f)
        except FileNotFoundError:
            bias_audit = None
            print("Warning: Bias report not found.")
    except FileNotFoundError:
        print("Metrics file not found. Run train.py first.")
        return

    # Load SHAP Explainer
    try:
        explainer = joblib.load("model/shap_explainer.joblib")
        shap_values_test = np.load("model/shap_values_test.npy")
        X_test_proc = np.load("model/X_test_processed.npy")
    except:
        print("SHAP artifacts not found.")
        return

    # Generate SHAP Summary Plot
    plt.figure()
    shap.summary_plot(shap_values_test, X_test_proc, show=False)
    plt.savefig("model/shap_summary.png", bbox_inches='tight')
    plt.close()

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="AI Credit Model Audit Report", ln=1, align="C")
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt="1. Model Performance", ln=1, align="L")
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 8, txt=f"ROC-AUC Score: {metrics['roc_auc']:.4f}", ln=1)
    pdf.cell(200, 8, txt=f"Brier Score: {metrics['brier_score']:.4f}", ln=1)
    pdf.cell(200, 8, txt=f"Precision (Approve): {metrics['precision_approve']:.4f}", ln=1)
    
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="2. Data Integrity (Validation)", ln=1, align="L")
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 8, txt=f"Total Records: {validation['total_records']}", ln=1)
    pdf.cell(200, 8, txt=f"Default Rate: {validation['default_rate']:.2%}", ln=1)
    pdf.cell(200, 8, txt=f"Negative Income Errors: {validation['negative_income']}", ln=1)
    
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="3. Fairness & Bias Audit (Four-Fifths Rule)", ln=1, align="L")
    pdf.set_font("Arial", size=10)
    if bias_audit:
        pdf.cell(200, 8, txt=f"Age Group Bias (DIR): {bias_audit['age']['disparate_impact_ratio']} (Flagged: {bias_audit['age']['flagged']})", ln=1)
        pdf.cell(200, 8, txt=f"Marital Status Bias (DIR): {bias_audit['marital']['disparate_impact_ratio']} (Flagged: {bias_audit['marital']['flagged']})", ln=1)
    else:
        pdf.cell(200, 8, txt="Bias Audit Data Unavailable", ln=1)

    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="4. Model Stability (PSI) & Reliability", ln=1, align="L")
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 8, txt=f"Prediction PSI (Train vs Test): {metrics.get('prediction_psi', 'N/A'):.4f}", ln=1)
    
    if os.path.exists("model/calibration_curve.png"):
        pdf.ln(5)
        pdf.image("model/calibration_curve.png", x=10, w=100)
    
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="5. Global Feature Importance (SHAP)", ln=1, align="L")
    pdf.image("model/shap_summary.png", x=10, w=180)
    
    pdf.output("model/Audit_Report.pdf")
    print("Report saved to model/Audit_Report.pdf")

if __name__ == "__main__":
    generate_report()
