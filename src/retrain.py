import pandas as pd
import os
import shutil
import joblib

def retrain_model():
    print("Starting Model Retraining Process...")
    
    # 1. Load Historical Data
    try:
        df_hist = pd.read_csv("data/refined_credit_data.csv")
    except FileNotFoundError:
        print("Historical data not found.")
        return False
        
    # 2. Load Feedback Data
    feedback_file = "data/feedback_data.csv"
    if os.path.exists(feedback_file):
        df_feedback = pd.read_csv(feedback_file)
        print(f"Loaded {len(df_feedback)} user feedback records.")
        
        # Merge
        # Feedback data must have same columns. App needs to ensure this.
        # Check alignment
        missing_cols = set(df_hist.columns) - set(df_feedback.columns)
        if missing_cols:
            print(f"Warning: Feedback data missing columns: {missing_cols}. Filling with defaults.")
            for c in missing_cols:
                df_feedback[c] = 0 # Naive fill or smarter logic needed
        
        # Concat
        df_combined = pd.concat([df_hist, df_feedback], ignore_index=True)
    else:
        print("No feedback data found. Training on historical only.")
        df_combined = df_hist
        
    # 3. Save Combined Temp (optional, or just pass to training logic)
    # We will overwrite the main data file? No, risky. 
    # Better to save as "training_data.csv" which train.py uses.
    # For now, let's just trigger the existing pipelines on this dataframe?
    # But `preprocess.py` and `train.py` load from CSV.
    # So we will save a temp file and tell them to use it? 
    # Or just overwrite `refined_credit_data.csv`? 
    # Let's overwrite `refined_credit_data.csv` but backup first.
    
    shutil.copy("data/refined_credit_data.csv", "data/refined_credit_data.bak")
    df_combined.to_csv("data/refined_credit_data.csv", index=False)
    
    # 4. Trigger Pipeline
    # We call process_documents (unlikely new docs for feedback cases unless handled), 
    # Preprocess, and Train.
    print("Running Pipeline...")
    val = os.system("python src/preprocess.py")
    if val != 0: return False
    
    val = os.system("python src/train.py")
    if val != 0: return False
    
    print("Retraining Complete.")
    return True

if __name__ == "__main__":
    retrain_model()
