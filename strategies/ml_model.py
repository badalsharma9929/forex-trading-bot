"""
ML Model Module
Random Forest -> XGBoost -> LSTM pipeline
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

SKLEARN_AVAILABLE = True
XGBOOST_AVAILABLE = True
TF_AVAILABLE = True

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import xgboost as xgb
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
except ImportError:
    TF_AVAILABLE = False


class MLTradingModel:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML model"""
        feature_df = df.copy()
        
        self.feature_columns = [
            "rsi_14", "macd_line", "macd_signal", "macd_histogram",
            "bb_upper", "bb_lower", "bb_position",
            "ema_12", "ema_26", "sma_20", "sma_50", "sma_200",
            "adx", "stoch_k", "stoch_d", "cci", "atr",
            "returns", "volatility"
        ]
        
        feature_df = feature_df.dropna(subset=self.feature_columns)
        
        feature_df["target"] = (feature_df["close"].shift(-1) > feature_df["close"]).astype(int)
        
        feature_df = feature_df.dropna(subset=["target"])
        
        self.feature_columns.append("target")
        
        return feature_df
    
    def create_lstm_dataset(self, df: pd.DataFrame, look_back: int = 20) -> Tuple:
        """Create sequences for LSTM"""
        features = df[self.feature_columns[:-1]].values
        target = df["target"].values
        
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        X, y = [], []
        for i in range(look_back, len(features_scaled)):
            X.append(features_scaled[i-look_back:i])
            y.append(target[i])
        
        return np.array(X), np.array(y), scaler
    
    def train_random_forest(self, df: pd.DataFrame) -> Dict:
        """Train Random Forest model"""
        if not SKLEARN_AVAILABLE:
            return {"status": "sklearn not available"}
        
        feature_df = self.prepare_features(df)
        
        X = feature_df[self.feature_columns[:-1]]
        y = feature_df["target"]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        feature_importance = pd.DataFrame({
            "feature": X.columns,
            "importance": model.feature_importances_
        }).sort_values("importance", ascending=False)
        
        self.models["random_forest"] = model
        self.is_trained = True
        
        return {
            "status": "trained",
            "model": "Random Forest",
            "accuracy": round(accuracy, 4),
            "feature_importance": feature_importance.head(10).to_dict("records")
        }
    
    def train_xgboost(self, df: pd.DataFrame) -> Dict:
        """Train XGBoost model"""
        if not XGBOOST_AVAILABLE:
            return {"status": "xgboost not available"}
        
        feature_df = self.prepare_features(df)
        
        X = feature_df[self.feature_columns[:-1]]
        y = feature_df["target"]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric="logloss"
        )
        
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.models["xgboost"] = model
        self.is_trained = True
        
        return {
            "status": "trained",
            "model": "XGBoost",
            "accuracy": round(accuracy, 4)
        }
    
    def train_lstm(self, df: pd.DataFrame, look_back: int = 20) -> Dict:
        """Train LSTM model"""
        if not TF_AVAILABLE:
            return {"status": "tensorflow not available"}
        
        feature_df = self.prepare_features(df)
        
        X, y, scaler = self.create_lstm_dataset(feature_df, look_back)
        
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(look_back, X_train.shape[2])),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        history = model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0
        )
        
        _, accuracy = model.evaluate(X_test, y_test, verbose=0)
        
        self.models["lstm"] = model
        self.scalers["lstm"] = scaler
        self.is_trained = True
        
        return {
            "status": "trained",
            "model": "LSTM",
            "accuracy": round(accuracy, 4),
            "epochs": len(history.history['loss'])
        }
    
    def predict(self, df: pd.DataFrame, model_name: str = "random_forest") -> Dict:
        """Make prediction using trained model"""
        if not self.is_trained or model_name not in self.models:
            return self._generate_dummy_prediction()
        
        feature_df = self.prepare_features(df)
        
        if len(feature_df) == 0:
            return self._generate_dummy_prediction()
        
        latest = feature_df[self.feature_columns[:-1]].iloc[-1:].values
        
        if model_name == "random_forest":
            model = self.models["random_forest"]
            proba = model.predict_proba(latest)[0]
            pred = model.predict(latest)[0]
        elif model_name == "xgboost":
            model = self.models["xgboost"]
            proba = model.predict_proba(latest)[0]
            pred = model.predict(latest)[0]
        elif model_name == "lstm":
            model = self.models["lstm"]
            latest_scaled = self.scalers["lstm"].transform(latest)
            latest_reshaped = latest_scaled.reshape(1, 20, latest_scaled.shape[1])
            proba = model.predict(latest_reshaped, verbose=0)[0][0]
            pred = 1 if proba > 0.5 else 0
            proba = [1 - proba, proba]
        else:
            return self._generate_dummy_prediction()
        
        return {
            "prediction": int(pred),
            "label": "BULLISH" if pred == 1 else "BEARISH",
            "probability_bullish": round(proba[1] if len(proba) > 1 else proba[0], 4),
            "probability_bearish": round(proba[0] if len(proba) > 1 else 1 - proba[0], 4),
            "confidence": round(max(proba), 4),
            "model_used": model_name
        }
    
    def get_ensemble_prediction(self, df: pd.DataFrame) -> Dict:
        """Combine predictions from all models"""
        predictions = {}
        
        if "random_forest" in self.models:
            predictions["random_forest"] = self.predict(df, "random_forest")
        
        if "xgboost" in self.models:
            predictions["xgboost"] = self.predict(df, "xgboost")
        
        if not predictions:
            return self._generate_dummy_prediction()
        
        avg_prob_bullish = np.mean([p["probability_bullish"] for p in predictions.values()])
        
        final_pred = 1 if avg_prob_bullish > 0.5 else 0
        confidence = max(avg_prob_bullish, 1 - avg_prob_bullish)
        
        return {
            "prediction": final_pred,
            "label": "BULLISH" if final_pred == 1 else "BEARISH",
            "probability_bullish": round(avg_prob_bullish, 4),
            "probability_bearish": round(1 - avg_prob_bullish, 4),
            "confidence": round(confidence, 4),
            "model_predictions": predictions,
            "ensemble": True
        }
    
    def _generate_dummy_prediction(self) -> Dict:
        """Generate prediction when no model is trained"""
        prob = np.random.uniform(0.4, 0.6)
        pred = 1 if prob > 0.5 else 0
        
        return {
            "prediction": pred,
            "label": "BULLISH" if pred == 1 else "BEARISH",
            "probability_bullish": round(prob, 4),
            "probability_bearish": round(1 - prob, 4),
            "confidence": round(abs(prob - 0.5) * 2 + 0.5, 4),
            "model_used": "random",
            "note": "Dummy prediction - train models for real predictions"
        }


if __name__ == "__main__":
    from strategies.indicators import TechnicalIndicators
    import random
    from datetime import datetime, timedelta
    
    dates = [(datetime.now() - timedelta(hours=i)) for i in range(200, 0, -1)]
    base_price = 83.50
    
    data = {
        "timestamp": dates,
        "open": [base_price + random.uniform(-0.1, 0.1) for _ in range(200)],
        "high": [base_price + random.uniform(0, 0.2) for _ in range(200)],
        "low": [base_price - random.uniform(0, 0.2) for _ in range(200)],
        "close": [base_price + random.uniform(-0.15, 0.15) for _ in range(200)],
        "volume": [random.randint(1000, 10000) for _ in range(200)]
    }
    
    df = pd.DataFrame(data)
    df_with_indicators = TechnicalIndicators.calculate_all(df)
    
    ml_model = MLTradingModel()
    
    print("=== ML Model Training Test ===\n")
    
    if SKLEARN_AVAILABLE:
        rf_result = ml_model.train_random_forest(df_with_indicators)
        print(f"Random Forest: {rf_result}")
    
    if XGBOOST_AVAILABLE:
        xgb_result = ml_model.train_xgboost(df_with_indicators)
        print(f"XGBoost: {xgb_result}")
    
    print("\nEnsemble Prediction:")
    prediction = ml_model.get_ensemble_prediction(df_with_indicators)
    print(f"  Prediction: {prediction['label']}")
    print(f"  Confidence: {prediction['confidence']:.2%}")
    print(f"  Bullish Prob: {prediction['probability_bullish']:.2%}")
