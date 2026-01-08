import numpy as np
import pandas as pd

def calculate_psi(expected_array, actual_array, buckets=10):
    """
    Calculate the Population Stability Index (PSI) for a single feature or score.
    
    Args:
        expected_array: Training data (Baseline)
        actual_array: New production data (Current)
        buckets: Number of quantiles
        
    Returns:
        float: PSI value
    """
    def scale_range (input, min, max):
        input += -(np.min(input))
        input /= np.max(input) / (max - min)
        input += min
        return input

    # Handle breakpoints from Expected
    try:
        breakpoints = np.arange(0, buckets + 1) / (buckets) * 100
        breakpoints = np.percentile(expected_array, breakpoints)
    except:
        return 0.0

    # Calculate frequencies
    expected_percents = np.histogram(expected_array, breakpoints)[0] / len(expected_array)
    actual_percents = np.histogram(actual_array, breakpoints)[0] / len(actual_array)

    # Avoid zero division
    expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
    actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)

    # PSI Sum
    psi_values = (expected_percents - actual_percents) * np.log(expected_percents / actual_percents)
    psi = np.sum(psi_values)
    
    return psi

def check_drift(train_df, current_df, features):
    """
    Checks drift for all specified features.
    
    Returns:
        DataFrame: Feature | PSI | Status
    """
    report = []
    
    for feat in features:
        if feat in train_df.columns and feat in current_df.columns:
            psi = calculate_psi(train_df[feat], current_df[feat])
            
            status = "Green"
            if psi > 0.1: status = "Yellow"
            if psi > 0.2: status = "Red"
            
            report.append({
                "Feature": feat,
                "PSI": round(psi, 4),
                "Status": status
            })
            
    return pd.DataFrame(report).sort_values("PSI", ascending=False)
