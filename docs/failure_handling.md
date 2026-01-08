# Failure Taxonomy & Safe Fallback Rules (Prompt 11)

## 1. Failure Taxonomy
Identifying scenarios where the AI model must yield to human judgment or default to safety.

| Failure Mode | Trigger Condition | System Response |
| :--- | :--- | :--- |
| **Safety Knockout** | Credit Score < 600 OR DTI > 50% | **Hard Reject**. No inference run. Reasons logged. |
| **Data Discrepancy** | Reported Income > 20% diff vs Verified | **Flag for Review**. Model Score Penalty. (Code: `WARN_INC_MISMATCH`) |
| **Thin File** | < 2 Tradelines OR < 3 years history | **Low Confidence Band**. Max approval cap lowered. |
| **Model Uncertainty** | Prediction Confidence < 0.60 | **Yellow Flag**. "Gray Zone - Human Review Required". |
| **API Error** | Timeout or 500 Error | **System Error Fallback**. Status: `ERROR`. Safe Default: `Review`. |

## 2. Safe Fallback Rules (Policy Engine)
When the model cannot be trusted, the Policy Engine enforces the following "Defense in Depth":

### A. The "Do No Harm" Rule
If valid feature data is missing (NaN) for key fields (`income`, `debt`), the system defaults to:
- **Imputation strategy**: Worst-case (e.g., zero income, max debt).
- **Decision**: `REVIEW` (Never `APPROVE` on missing data).

### B. Contradictory Information
**Situation**: Document parser says "Unemployed" but Application says "Employed".
**Reaction**:
- Trusted Source priority: Document > Application.
- **Action**: Overwrite `employment_status` with Document value.
- **Alert**: `FRAUD_RISK_CONTRADICTION`.

### C. Out-of-Distribution (OOD)
**Situation**: Applicant is from a region or industry not seen in training (e.g. "Crypto Mining").
**Detection**: `Unseen Category` in Label Encoder.
**Reaction**:
- All OOD inputs are routed to **Manual Underwriting**.
- Auto-Approval is **DISABLED** for this application.
