import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def train_and_save_model():
    # CSV file path
    csv_path = 'single_user_stress_dataset.csv'
    if not os.path.exists(csv_path):
        csv_path = '../single_user_stress_dataset.csv'
        
    df = pd.read_csv(csv_path)
    df = df.dropna()
    
    features = ['hr_bpm', 'rmssd_ms', 'sdnn_ms', 'pnn50_pct', 'sleep_hrs', 'water_ml_today', 'mood', 'hour_of_day']
    target = 'stress_score'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=150, random_state=42)
    model.fit(X_train, y_train)
    
    os.makedirs('backend', exist_ok=True)
    joblib.dump(model, 'backend/stress_model.pkl')
    print("✅ Model successfully train ho gaya aur save ho gaya!")

if __name__ == '__main__':
    train_and_save_model()