"""
Continuous learning system for ML models
"""
import joblib
import os
from datetime import datetime
from ml_predictor import MLStockPredictor
from ml_database import MLDatabase
import yfinance as yf

class ContinuousLearningSystem:
    """Manages continuous learning for ML models"""
    
    def __init__(self):
        self.db = MLDatabase()
        self.models_dir = 'saved_models'
        os.makedirs(self.models_dir, exist_ok=True)
    
    def make_prediction_and_store(self, symbol, data, holding_style='swing'):
        """Make prediction and store it for future tracking"""
        try:
            predictor = MLStockPredictor(data, holding_style=holding_style)
            results = predictor.ensemble_prediction()
            
            # Store each model's prediction
            for model_name, pred_data in results['predictions'].items():
                pred_id = self.db.store_prediction(symbol, model_name, pred_data)
                print(f"✓ Stored {model_name} prediction (ID: {pred_id})")
            
            return results
        except Exception as e:
            print(f"✗ Error in make_prediction_and_store: {str(e)}")
            return {
                'predictions': {},
                'ensemble': {
                    'recommendation': 'HOLD',
                    'confidence': 50,
                    'buy_votes': 0,
                    'sell_votes': 0,
                    'hold_votes': 1,
                    'total_models': 0
                }
            }
    
    def update_outcomes(self):
        """Check for due predictions and record actual outcomes"""
        try:
            due_predictions = self.db.check_due_predictions()
            
            print(f"\n🔍 Checking {len(due_predictions)} due predictions...")
            
            for symbol, target_date in due_predictions:
                try:
                    # Fetch actual price on target date
                    ticker = yf.Ticker(f"{symbol}.NS")
                    hist = ticker.history(start=target_date, end=target_date)
                    
                    if not hist.empty:
                        actual_price = hist['Close'].iloc[0]
                        self.db.record_outcome(symbol, target_date, actual_price)
                        print(f"✓ Recorded outcome for {symbol} on {target_date}: ₹{actual_price:.2f}")
                except Exception as e:
                    print(f"✗ Could not fetch outcome for {symbol}: {e}")
        except Exception as e:
            print(f"✗ Error in update_outcomes: {str(e)}")
    
    def get_model_statistics(self, model_name, symbol=None):
        """Get comprehensive model statistics"""
        try:
            stats = self.db.get_model_accuracy(model_name, symbol)
            
            if stats:
                return {
                    'model': model_name,
                    'accuracy': f"{stats['accuracy']:.2f}%",
                    'total_predictions': stats['total_predictions'],
                    'correct_predictions': stats['correct_predictions'],
                    'avg_error': f"{stats['avg_error']:.2f}%",
                    'is_improving': self._check_if_improving(model_name, symbol)
                }
            return None
        except Exception as e:
            print(f"✗ Error getting model statistics: {str(e)}")
            return None
    
    def _check_if_improving(self, model_name, symbol):
        """Check if model is improving over time"""
        try:
            progress = self.db.get_learning_progress(model_name, symbol)
            
            if len(progress) >= 10:
                # Compare first 5 vs last 5 predictions
                early_accuracy = progress['accuracy'].head(5).mean()
                recent_accuracy = progress['accuracy'].tail(5).mean()
                
                return recent_accuracy > early_accuracy
            
            return None  # Not enough data
        except Exception as e:
            print(f"✗ Error checking improvement: {str(e)}")
            return None
    
    def retrain_if_needed(self, symbol, data, holding_style='swing'):
        """Retrain model if performance drops below threshold"""
        try:
            models = ['xgboost', 'random_forest', 'lstm']
            
            for model_name in models:
                stats = self.db.get_model_accuracy(model_name, symbol)
                
                if stats and stats['accuracy'] < 60:  # Below 60% accuracy
                    print(f"⚠️ {model_name} accuracy is {stats['accuracy']:.1f}% - Retraining...")
                    
                    # Retrain model
                    predictor = MLStockPredictor(data, holding_style=holding_style)
                    
                    if model_name == 'xgboost':
                        predictor.train_xgboost()
                    elif model_name == 'random_forest':
                        predictor.train_random_forest()
                    elif model_name == 'lstm':
                        predictor.train_lstm()
                    
                    print(f"✓ {model_name} retrained")
        except Exception as e:
            print(f"✗ Error in retrain_if_needed: {str(e)}")
    
    def get_learning_curve(self, model_name, symbol):
        """Get learning curve data for visualization"""
        try:
            return self.db.get_learning_progress(model_name, symbol)
        except Exception as e:
            print(f"✗ Error getting learning curve: {str(e)}")
            import pandas as pd
            return pd.DataFrame()
