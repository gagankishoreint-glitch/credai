import os
import random
import pandas as pd
from fpdf import FPDF

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_pdf_statement(applicant_id, income, assets):
    """Generates a mock PDF financial statement."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Financial Statement 2024", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Applicant ID: {applicant_id}", ln=1, align="L")
    pdf.cell(200, 10, txt=f"Date: 2025-01-01", ln=1, align="L")
    pdf.ln(10)
    
    # Randomly format the text to make parsing slightly "realistic"
    formats = [
        f"Verified Annual Income: ${income:,.2f}",
        f"TOTAL INCOME per ANNUM: {income}",
        f"Income (Yearly): {income} USD"
    ]
    income_text = random.choice(formats)
    
    asset_formats = [
        f"Total Assets Reported: ${assets:,.2f}",
        f"ASSETS: {assets}",
        f"Net Worth/Assets: {assets} USD"
    ]
    asset_text = random.choice(asset_formats)
    
    pdf.cell(200, 10, txt=income_text, ln=1)
    pdf.cell(200, 10, txt=asset_text, ln=1)
    
    pdf.output(f"data/raw_documents/{applicant_id}_financials.pdf")

def generate_csv_statement(applicant_id):
    """Generates a mock CSV bank statement."""
    # Simulate 3 months of transactions
    dates = pd.date_range(end="2025-01-01", periods=90)
    
    data = []
    for date in dates:
        # Income or Expense
        if random.random() < 0.2: # 20% chance of income
            amount = random.uniform(1000, 5000)
            desc = "Deposit / Salary"
        else:
            amount = -random.uniform(50, 500)
            desc = random.choice(["Grocery", "Utilities", "Rent", "Dining", "Subscription"])
            
        data.append({
            "Date": date,
            "Description": desc,
            "Amount": amount
        })
    
    df = pd.DataFrame(data)
    df.to_csv(f"data/raw_documents/{applicant_id}_bank_stmt.csv", index=False)

def main():
    ensure_dir("data/raw_documents")
    
    # Load the base data to get IDs
    try:
        df = pd.read_csv("data/refined_credit_data.csv")
    except FileNotFoundError:
        print("Please run generate_refined_data.py first.")
        return

    # Generate documents for a subset of users (e.g., first 50 for testing speed)
    # in a real scenario, we might do all, but PDF gen is slow.
    subset_ids = df["applicant_id"].head(20).tolist()
    
    print(f"Generating documents for {len(subset_ids)} applicants...")
    
    for aid in subset_ids:
        # Get ground truth income to simulate consistency (or inconsistency)
        user_row = df[df["applicant_id"] == aid].iloc[0]
        ground_income = user_row["annual_income"]
        
        # Add some noise to reported income
        reported_income = ground_income * random.uniform(0.9, 1.1)
        reported_assets = ground_income * random.uniform(0.5, 5.0) # crude proxy
        
        generate_pdf_statement(aid, reported_income, reported_assets)
        generate_csv_statement(aid)
        
    print("Mock documents generated successfully in data/raw_documents/")

if __name__ == "__main__":
    main()
