import os
import re
import pandas as pd
from pypdf import PdfReader

def extract_from_pdf(pdf_path):
    """
    Parses a PDF financial statement to extract reported income and assets.
    Returns: (income, assets) or (NaN, NaN) if not found.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # Regex to find money patterns like "Income: $50,000" or "50000 USD"
        # Simplify regex for the mock format we generated
        # Formats: "Income...: $X,XXX.XX", "INCOME...: X", etc.
        
        # Look for Income
        income_match = re.search(r"(?:Income|INCOME).*?[:\$-]?\s*([0-9,]+(?:\.[0-9]{2})?)", text)
        assets_match = re.search(r"(?:Assets|ASSETS|Worth).*?[:\$-]?\s*([0-9,]+(?:\.[0-9]{2})?)", text)
        
        income = float(income_match.group(1).replace(",", "")) if income_match else None
        assets = float(assets_match.group(1).replace(",", "")) if assets_match else None
        
        return income, assets
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None, None

def process_csv_statement(csv_path):
    """
    Parses a CSV bank statement to calculate monthly net cashflow.
    """
    try:
        df = pd.read_csv(csv_path)
        # Net sum of all amounts
        # In a real app, we'd group by month, but here we just take the mean monthly sum
        # We have 90 days (~3 months)
        total_cashflow = df["Amount"].sum()
        monthly_average = total_cashflow / 3.0
        return monthly_average
    except Exception as e:
        print(f"Error reading CSV {csv_path}: {e}")
        return None

def main():
    docs_dir = "data/raw_documents"
    if not os.path.exists(docs_dir):
        print("No documents found.")
        return

    features = []
    
    # Iterate over files in the directory
    # We expect naming convention AP_XXXXX_financials.pdf or AP_XXXXX_bank_stmt.csv
    
    files = os.listdir(docs_dir)
    applicant_ids = set()
    for f in files:
        # Extract APP_XXXXX
        match = re.match(r"(APP_\d+)", f)
        if match:
            applicant_ids.add(match.group(1))
            
    print(f"Processing documents for {len(applicant_ids)} applicants...")
    
    for aid in applicant_ids:
        pdf_path = os.path.join(docs_dir, f"{aid}_financials.pdf")
        csv_path = os.path.join(docs_dir, f"{aid}_bank_stmt.csv")
        
        verified_income = None
        assets_reported = None
        derived_cashflow = None
        
        if os.path.exists(pdf_path):
            verified_income, assets_reported = extract_from_pdf(pdf_path)
            
        if os.path.exists(csv_path):
            derived_cashflow = process_csv_statement(csv_path)
            
        features.append({
            "applicant_id": aid,
            "doc_verified_income": verified_income,
            "doc_assets_reported": assets_reported,
            "doc_derived_cashflow": derived_cashflow,
            "has_financial_stmts": 1 if (os.path.exists(pdf_path) or os.path.exists(csv_path)) else 0
        })
        
    df_features = pd.DataFrame(features)
    output_path = "data/document_features.csv"
    df_features.to_csv(output_path, index=False)
    print(f"Document features saved to {output_path}")
    print(df_features.head())

if __name__ == "__main__":
    main()
