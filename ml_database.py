"""
ML prediction tracking and continuous learning system
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class MLDatabase:
    """Stores ML predictions and tracks performance"""
    
    def __init__(self, db_path='ml_predictions.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.create_tables()
    
    def create_tables(self):
        """Create database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                prediction_date DATE NOT NULL,
                target_date DATE NOT NULL,
                model_name TEXT NOT NULL,
                prediction_type TEXT,
                predicted_value REAL,
                predicted_direction TEXT,
                confidence REAL,
                current_price REAL,
                holding_style TEXT,
                prediction_days INTEGER,
                additional_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Actual outcomes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER,
                symbol TEXT NOT NULL,
                target_date DATE NOT NULL,
                actual_price REAL,
                actual_direction TEXT,
                prediction_correct BOOLEAN,
                price_difference REAL,
                percentage_error REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id)
            )
        ''')
        
        # Model performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                symbol TEXT,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy REAL,
                avg_price_error REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_prediction(self, symbol, model_name, prediction_data):
        """Store a new prediction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        prediction_date = datetime.now().date()
        target_date = prediction_date + timedelta(days=prediction_data.get('days_ahead', 5))
        
        cursor.execute('''
            INSERT INTO predictions (
                symbol, prediction_date, target_date, model_name,
                prediction_type, predicted_value, predicted_direction,
                confidence, current_price, holding_style, prediction_days,
                additional_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            prediction_date,
            target_date,
            model_name,
            prediction_data.get('type', 'price'),
            prediction_data.get('predicted_price') or prediction_data.get('predicted_return'),
            prediction_data.get('direction') or prediction_data.get('signal'),
            prediction_data.get('confidence', 0.5),
            prediction_data.get('current_price'),
            prediction_data.get('holding_style', 'swing'),
            prediction_data.get('days_ahead', 5),
            json.dumps(prediction_data)
        ))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return prediction_id
    
    def record_outcome(self, symbol, target_date, actual_price):
        """Record actual outcome and calculate accuracy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find predictions for this symbol and date
        cursor.execute('''
            SELECT id, model_name, predicted_value, predicted_direction,
                   current_price, prediction_type
            FROM predictions
            WHERE symbol = ? AND target_date = ?
            AND id NOT IN (SELECT prediction_id FROM outcomes WHERE prediction_id IS NOT NULL)
        ''', (symbol, target_date))
        
        predictions = cursor.fetchall()
        
        for pred in predictions:
            pred_id, model_name, predicted_value, predicted_direction, current_price, pred_type = pred
            
            # Calculate accuracy
            if pred_type == 'price':
                price_diff = actual_price - predicted_value
                pct_error = abs(price_diff / actual_price) * 100
            else:
                price_diff = actual_price - current_price
                pct_error = abs(price_diff / actual_price) * 100
            
            # Determine if direction was correct
            actual_direction = 'UP' if actual_price > current_price else 'DOWN'
            direction_correct = (predicted_direction == actual_direction)
            
            # Store outcome
            cursor.execute('''
                INSERT INTO outcomes (
                    prediction_id, symbol, target_date, actual_price,
                    actual_direction, prediction_correct, price_difference,
                    percentage_error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pred_id, symbol, target_date, actual_price,
                actual_direction, direction_correct, price_diff, pct_error
            ))
            
            # Update model performance
            self._update_model_performance(model_name, symbol, direction_correct, pct_error)
        
        conn.commit()
        conn.close()
    
    def _update_model_performance(self, model_name, symbol, correct, pct_error):
        """Update model performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute('''
            SELECT id, total_predictions, correct_predictions, avg_price_error
            FROM model_performance
            WHERE model_name = ? AND symbol = ?
        ''', (model_name, symbol))
        
        result = cursor.fetchone()
        
        if result:
            perf_id, total, correct_count, avg_error = result
            
            new_total = total + 1
            new_correct = correct_count + (1 if correct else 0)
            new_accuracy = (new_correct / new_total) * 100
            new_avg_error = ((avg_error * total) + pct_error) / new_total
            
            cursor.execute('''
                UPDATE model_performance
                SET total_predictions = ?, correct_predictions = ?,
                    accuracy = ?, avg_price_error = ?, last_updated = ?
                WHERE id = ?
            ''', (new_total, new_correct, new_accuracy, new_avg_error, datetime.now(), perf_id))
        else:
            cursor.execute('''
                INSERT INTO model_performance (
                    model_name, symbol, total_predictions, correct_predictions,
                    accuracy, avg_price_error
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                model_name, symbol, 1, 1 if correct else 0,
                100 if correct else 0, pct_error
            ))
        
        conn.commit()
        conn.close()
    
    def get_model_accuracy(self, model_name, symbol=None):
        """Get model accuracy statistics"""
        conn = sqlite3.connect(self.db_path)
        
        if symbol:
            query = '''
                SELECT accuracy, avg_price_error, total_predictions, correct_predictions
                FROM model_performance
                WHERE model_name = ? AND symbol = ?
            '''
            params = (model_name, symbol)
        else:
            query = '''
                SELECT AVG(accuracy), AVG(avg_price_error), 
                       SUM(total_predictions), SUM(correct_predictions)
                FROM model_performance
                WHERE model_name = ?
            '''
            params = (model_name,)
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return {
                'accuracy': result[0],
                'avg_error': result[1],
                'total_predictions': result[2],
                'correct_predictions': result[3]
            }
        return None
    
    def get_recent_predictions(self, symbol, days=30):
        """Get recent predictions for a symbol"""
        conn = sqlite3.connect(self.db_path)
        
        start_date = datetime.now().date() - timedelta(days=days)
        
        query = '''
            SELECT p.*, o.actual_price, o.prediction_correct, o.percentage_error
            FROM predictions p
            LEFT JOIN outcomes o ON p.id = o.prediction_id
            WHERE p.symbol = ? AND p.prediction_date >= ?
            ORDER BY p.prediction_date DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(symbol, start_date))
        conn.close()
        
        return df
    
    def check_due_predictions(self):
        """Check predictions that are due for outcome recording"""
        conn = sqlite3.connect(self.db_path)
        
        today = datetime.now().date()
        
        query = '''
            SELECT DISTINCT symbol, target_date
            FROM predictions
            WHERE target_date <= ? 
            AND id NOT IN (SELECT prediction_id FROM outcomes WHERE prediction_id IS NOT NULL)
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (today,))
        due_predictions = cursor.fetchall()
        conn.close()
        
        return due_predictions
    
    def get_learning_progress(self, model_name, symbol):
        """Get model learning progress over time"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                DATE(p.prediction_date) as date,
                COUNT(*) as total,
                SUM(CASE WHEN o.prediction_correct = 1 THEN 1 ELSE 0 END) as correct,
                AVG(o.percentage_error) as avg_error
            FROM predictions p
            JOIN outcomes o ON p.id = o.prediction_id
            WHERE p.model_name = ? AND p.symbol = ?
            GROUP BY DATE(p.prediction_date)
            ORDER BY date
        '''
        
        df = pd.read_sql_query(query, conn, params=(model_name, symbol))
        
        if not df.empty:
            df['accuracy'] = (df['correct'] / df['total']) * 100
        
        conn.close()
        return df
