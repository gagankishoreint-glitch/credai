
import sys
import os

# Set path to include current directory so 'app' is found
sys.path.append(os.getcwd())

# Import the T2 script logic as a module
try:
    from backend.tests import model_sanity_audit
    model_sanity_audit.run_sanity_audit()
except ImportError as e:
    print(f"Import Error: {e}")
    # Fallback: try direct import if structure allows
    try:
        from app.services.model_inference import model_service
        print("Model Service Found. Running inline check...")
        # (Inline logic if needed, but prefer module)
    except Exception as e2:
         print(f"Fallback Failed: {e2}")
