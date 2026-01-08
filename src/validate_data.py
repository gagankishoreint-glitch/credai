import pandas as pd
import json

def validate_data(filepath="data/refined_credit_data.csv"):
    print("Running Data Validation...")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print("Data file not found.")
        return False

    report = {
        "total_records": int(len(df)),
        "missing_values": df.isnull().sum().astype(int).to_dict(),
        "negative_income": int((df["annual_income"] < 0).sum()),
        "debt_exceeds_assets": int((df["total_debt"] > df["assets_total"]).sum()),
        "possible_duplicates": int(df.duplicated(subset=["applicant_id"]).sum()),
        "default_rate": float(df["default_flag"].mean())
    }
    
    # Logic Checks
    if report["negative_income"] > 0:
        print("WARNING: Negative income detected.")
        
    if report["possible_duplicates"] > 0:
        print("CRITICAL: Duplicate Applicant IDs found.")
        
    print(f"Validation Report: {json.dumps(report, indent=2)}")
    
    # Save log
    with open("data/validation_log.json", "w") as f:
        json.dump(report, f, indent=2)
        
    return True

if __name__ == "__main__":
    validate_data()
