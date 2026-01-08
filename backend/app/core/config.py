import os

class Settings:
    PROJECT_NAME: str = "AI Credit Decision Engine"
    API_V1_STR: str = "/api/v1"
    
    # Model Paths (Absolute for safety in this env)
    BASE_DIR = "k:/credit-ai-model"
    MODEL_PATH = os.path.join(BASE_DIR, "model", "credit_risk_model.joblib")
    PREPROCESSOR_PATH = os.path.join(BASE_DIR, "model", "preprocessor.joblib")

settings = Settings()
