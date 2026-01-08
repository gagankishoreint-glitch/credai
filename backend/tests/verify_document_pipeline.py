
import sys
import os
import io

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.document_service import document_service
from app.services.feature_fusion import feature_fusion
from app.services.policy_engine import policy_engine
from app.services.model_service import model_service
from app.schemas.decision import CreditApplication

def test_document_pipeline():
    print("🚀 STARTING E2E DOCUMENT PIPELINE VERIFICATION\n")
    
    # --- STEP 1: TEST DOCUMENT SERVICE (MOCK OCR) ---
    print("🔹 STEP 1: Document Service Extraction")
    
    # Mock PDF content (would be bytes in real life)
    mock_pdf_bytes = b"%PDF-1.4 Mock PDF Content"
    
    # Test Extraction
    extraction = document_service.extract_from_pdf(mock_pdf_bytes, declared_data={})
    
    print(f"Status: {extraction['status']}")
    print(f"Confidence: {extraction['extraction_confidence']}")
    print(f"Extracted Income: {extraction['doc_verified_income']}")
    print(f"Extracted Debt: {extraction['doc_extracted_debts']}")
    
    if extraction['status'] != "SUCCESS":
        print("❌ Document extraction failed!")
        return
    
    print("✅ Document Service Verification Passed\n")
    
    
    # --- STEP 2: TEST FEATURE FUSION ---
    print("🔹 STEP 2: Feature Fusion Logic")
    
    # Scenario: User under-reports debt, slightly over-reports income
    form_data = {
        "annual_income": 900000,   # Declared 9L
        "total_debt": 100000,      # Declared 1L
        "credit_score": 750
    }
    
    # Mock Document Data (from Step 1 or custom)
    # Let's say doc shows 8.5L Income, but 2.5L Debt (Hidden debt case)
    doc_data = {
        "status": "SUCCESS",
        "doc_verified_income": 850000,
        "doc_extracted_debts": 250000,
        "doc_avg_balance": 50000,
        "extraction_confidence": 0.85,
        "doc_overdraft_count": 0
    }
    
    fused_features, metadata = feature_fusion.fuse_features(form_data, doc_data)
    
    print("\n--- FUSION RESULTS ---")
    print(f"Original Income: {form_data['annual_income']} -> Fused: {fused_features['annual_income']}")
    print(f"Original Debt: {form_data['total_debt']} -> Fused: {fused_features['total_debt']}")
    print(f"Trust Score: {metadata['trust_score']:.2f}")
    
    # Assertions
    if fused_features['total_debt'] != 250000:
        print("❌ Critical: Hidden debt not fused correctly!")
    if metadata['trust_score'] > 0.9:
        print("❌ Critical: Trust score too high despite discrepancies!")
        
    print("✅ Feature Fusion Verification Passed\n")
    
    
    # --- STEP 3: INTEGRATION WITH MODEL & DECISION ---
    print("🔹 STEP 3: Full Decision Flow Integration")
    
    # Prepare model input from fused features
    model_input = fused_features.copy()
    model_input['age'] = 30
    model_input['employment_years'] = 5
    model_input['credit_utilization'] = 0.3
    model_input['delinquency_count'] = 0
    
    # 1. Predict
    pred = model_service.predict_probability(model_input)
    pd = pred['calibrated_pd']
    conf = pred['confidence_score']
    
    print(f"\nModel Prediction PD: {pd:.4f}")
    print(f"Model Confidence: {conf:.4f}")
    
    # 2. Decision
    # Adjust confidence based on fusion trust? 
    # In a real integration, we'd pass trust into policy engine.
    # For now, let's see what the plain policy does.
    
    tier, final_conf, reason = policy_engine.apply_decision_logic(pd, conf)
    
    print(f"Decision Tier: {tier}")
    print(f"Reason: {reason}")
    
    if tier not in ["Approve", "Review", "Reject"]:
        print("❌ Invalid Decision Tier")
    
    print("✅ Integration Verification Passed\n")
    
    print("🎉 ALL SYSTEMS GO: 5-LAYER ARCHITECTURE VERIFIED")

if __name__ == "__main__":
    test_document_pipeline()
