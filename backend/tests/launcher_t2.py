
import sys
import os

# Explicitly add the 'backend' folder to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.services.model_inference import model_service
    # Re-import the audit logic logic from the other file, or just copy it here to be safe.
    # Let's import the function from model_sanity_audit
    from backend.tests import model_sanity_audit
    model_sanity_audit.run_sanity_audit()
except Exception as e:
    print(f"CRITICAL BOOT FAILURE: {e}")
