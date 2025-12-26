"""
Data Preprocessing and Feature Engineering Pipeline
Prepares data for ML model training
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

def load_data(filepath='backend/ml_pipeline/data/business_credit_data.csv'):
    """Load the generated dataset"""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"✅ Loaded {len(df)} records")
    return df

def handle_missing_values(df):
    """Handle any missing values in the dataset"""
    print("\nChecking for missing values...")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"Found {missing.sum()} missing values")
        # For numerical columns, fill with median
        num_cols = df.select_dtypes(include=[np.number]).columns
        df[num_cols] = df[num_cols].fillna(df[num_cols].median())
        # For categorical columns, fill with mode
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            df[col] = df[col].fillna(df[col].mode()[0])
        print("✅ Missing values handled")
    else:
        print("✅ No missing values found")
    return df

def engineer_features(df):
    """Create derived features"""
    print("\nEngineering features...")
    
    # Loan to revenue ratio
    df['loan_to_revenue_ratio'] = df['loan_amount_requested'] / df['annual_revenue']
    
    # Cash flow adequacy (monthly cashflow relative to loan amount)
    df['cashflow_adequacy'] = (df['monthly_cashflow'] * 12) / df['loan_amount_requested']
    
    # Collateral coverage ratio
    df['collateral_coverage'] = df['collateral_value'] / df['loan_amount_requested']
    
    # Credit score category
    df['credit_score_category'] = pd.cut(df['credit_score'], 
                                          bins=[0, 580, 670, 740, 900],
                                          labels=['Poor', 'Fair', 'Good', 'Excellent'])
    
    # Business maturity (years in operation bins)
    df['business_maturity'] = pd.cut(df['years_in_operation'],
                                      bins=[-1, 2, 5, 10, 100],
                                      labels=['Startup', 'Young', 'Established', 'Mature'])
    
    print(f"✅ Created {5} new features")
    return df

def encode_categorical_variables(df, train=True, encoders=None):
    """Encode categorical variables"""
    print("\nEncoding categorical variables...")
    
    categorical_cols = ['business_type', 'repayment_history', 'credit_score_category', 'business_maturity']
    
    if train:
        encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            df[f'{col}_encoded'] = le.fit_transform(df[col])
            encoders[col] = le
        print(f"✅ Encoded {len(categorical_cols)} categorical columns")
        return df, encoders
    else:
        for col in categorical_cols:
            df[f'{col}_encoded'] = encoders[col].transform(df[col])
        return df

def normalize_features(df, train=True, scaler=None, exclude_cols=None):
    """Normalize numerical features"""
    print("\nNormalizing numerical features...")
    
    if exclude_cols is None:
        exclude_cols = ['applicant_id', 'default_flag']
    
    # Select numerical columns to scale
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    cols_to_scale = [col for col in numerical_cols if col not in exclude_cols and not col.endswith('_encoded')]
    
    if train:
        scaler = StandardScaler()
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
        print(f"✅ Normalized {len(cols_to_scale)} numerical columns")
        return df, scaler
    else:
        df[cols_to_scale] = scaler.transform(df[cols_to_scale])
        return df

def prepare_train_test_split(df, test_size=0.2, random_state=42):
    """Split data into train and test sets with stratification"""
    print("\nSplitting data into train and test sets...")
    
    # Separate features and target
    feature_cols = [col for col in df.columns if col not in ['applicant_id', 'default_flag', 
                                                               'business_type', 'repayment_history',
                                                               'credit_score_category', 'business_maturity']]
    
    X = df[feature_cols]
    y = df['default_flag']
    
    # Stratified split to maintain class balance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"✅ Train set: {len(X_train)} samples ({(y_train.sum()/len(y_train)*100):.2f}% default rate)")
    print(f"✅ Test set: {len(X_test)} samples ({(y_test.sum()/len(y_test)*100):.2f}% default rate)")
    
    return X_train, X_test, y_train, y_test, feature_cols

def save_artifacts(encoders, scaler, feature_cols, output_dir='backend/ml_pipeline/models'):
    """Save preprocessing artifacts for later use"""
    print("\nSaving preprocessing artifacts...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    joblib.dump(encoders, f'{output_dir}/label_encoders.pkl')
    joblib.dump(scaler, f'{output_dir}/scaler.pkl')
    joblib.dump(feature_cols, f'{output_dir}/feature_columns.pkl')
    
    print(f"✅ Artifacts saved to {output_dir}")

def preprocess_pipeline():
    """Main preprocessing pipeline"""
    print("="*60)
    print("CREDIT DATA PREPROCESSING PIPELINE")
    print("="*60)
    
    # Load data
    df = load_data()
    
    # Handle missing values
    df = handle_missing_values(df)
    
    # Engineer features
    df = engineer_features(df)
    
    # Encode categorical variables
    df, encoders = encode_categorical_variables(df, train=True)
    
    # Normalize features
    df, scaler = normalize_features(df, train=True, 
                                     exclude_cols=['applicant_id', 'default_flag'])
    
    # Train-test split
    X_train, X_test, y_train, y_test, feature_cols = prepare_train_test_split(df)
    
    # Save artifacts
    save_artifacts(encoders, scaler, feature_cols)
    
    # Save processed data
    print("\nSaving processed data...")
    X_train.to_csv('backend/ml_pipeline/data/X_train.csv', index=False)
    X_test.to_csv('backend/ml_pipeline/data/X_test.csv', index=False)
    y_train.to_csv('backend/ml_pipeline/data/y_train.csv', index=False)
    y_test.to_csv('backend/ml_pipeline/data/y_test.csv', index=False)
    
    print("\n" + "="*60)
    print("✨ PREPROCESSING COMPLETE!")
    print("="*60)
    
    return X_train, X_test, y_train, y_test, feature_cols

if __name__ == "__main__":
    preprocess_pipeline()
