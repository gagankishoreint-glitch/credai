from fpdf import FPDF
import os
import random

def create_balance_sheet(filename, applicant_name, year):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Balance Sheet - {year}", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Company: {applicant_name}", ln=1, align='C')
    pdf.ln(10)
    
    assets = random.randint(100000, 5000000)
    liabilities = int(assets * random.uniform(0.3, 0.8))
    equity = assets - liabilities
    
    pdf.cell(200, 10, txt=f"Total Assets: ${assets:,.2f}", ln=1)
    pdf.cell(200, 10, txt=f"Total Liabilities: ${liabilities:,.2f}", ln=1)
    pdf.cell(200, 10, txt=f"Total Equity: ${equity:,.2f}", ln=1)
    
    pdf.output(filename)

def create_cashflow(filename, applicant_name, year):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Cash Flow Statement - {year}", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Company: {applicant_name}", ln=1, align='C')
    pdf.ln(10)
    
    operating = random.randint(50000, 1000000)
    investing = -random.randint(10000, 200000)
    financing = random.randint(10000, 500000)
    net_change = operating + investing + financing
    
    pdf.cell(200, 10, txt=f"Net Cash from Operating Activities: ${operating:,.2f}", ln=1)
    pdf.cell(200, 10, txt=f"Net Cash from Investing Activities: ${investing:,.2f}", ln=1)
    pdf.cell(200, 10, txt=f"Net Cash from Financing Activities: ${financing:,.2f}", ln=1)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Net Increase in Cash: ${net_change:,.2f}", ln=1)
    
    pdf.output(filename)

# Generate for 5 applicants
for i in range(1, 6):
    app_id = f"applicant_{i:03d}"
    create_balance_sheet(f"dataset/financial_docs/{app_id}_balance_sheet.pdf", f"Tech Corp {i}", 2024)
    create_cashflow(f"dataset/financial_docs/{app_id}_cashflow.pdf", f"Tech Corp {i}", 2024)

print("PDFs generated successfully in dataset/financial_docs/")
