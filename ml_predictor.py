"""
Machine Learning prediction module for stock price forecasting
Optimized for swing trading and investing
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import xgboost as xgb
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

class MLStockPredictor:
    """ML-based stock price prediction for swing trading and investing"""
    
    def __init__(self, data, holding_style='swing', news_sentiment=None):
        """
        Initialize ML predictor
        
        Args:
            data (pd.DataFrame): Historical OHLCV data
            holding_style (str): 'swing' (2-10 days) or 'invest' (months)
            news_sentiment (dict): Sentiment analysis results
        """
        self.data = data.copy()
        self.holding_style = holding_style
        self.news_sentiment = news_sentiment or {'sentiment_score': 0}
        self.scaler = StandardScaler()
        
        # Set prediction horizon based on style
        if holding_style == 'swing':
            self.prediction_days = 5
            self.lookback_period = 20
        else:  # invest
            self.prediction_days = 30
            self.lookback_period = 60
    
    def create_features(self):
        """Create technical features for ML models"""
        df = self.data.copy()

        # Add sentiment score as a feature
        df['News_Sentiment'] = self.news_sentiment.get('sentiment_score', 0)
        
        # Price-based features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential moving averages
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Diff'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Volume features
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        # Momentum
        df['Momentum_5'] = df['Close'] - df['Close'].shift(5)
        df['Momentum_10'] = df['Close'] - df['Close'].shift(10)
        
        # Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        # Price position
        df['High_Low_Ratio'] = df['High'] / df['Low']
        df['Close_Open_Ratio'] = df['Close'] / df['Open']

        # Newly added
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))

        # 1. ADX (Average Directional Index) - Trend Strength
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()  # Average True Range

        # 2. Stochastic Oscillator
        low_14 = df['Low'].rolling(window=14).min()
        high_14 = df['High'].rolling(window=14).max()
        df['Stochastic_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
        df['Stochastic_D'] = df['Stochastic_K'].rolling(window=3).mean()

        # 3. Williams %R
        df['Williams_R'] = -100 * ((high_14 - df['Close']) / (high_14 - low_14))

        # 4. Rate of Change (ROC)
        df['ROC_5'] = ((df['Close'] - df['Close'].shift(5)) / df['Close'].shift(5)) * 100
        df['ROC_10'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100

        # 5. Money Flow Index (MFI) - Volume-weighted RSI
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
        
        positive_mf = positive_flow.rolling(window=14).sum()
        negative_mf = negative_flow.rolling(window=14).sum()
        
        mfi_ratio = positive_mf / negative_mf
        df['MFI'] = 100 - (100 / (1 + mfi_ratio))
        
        # 6. On-Balance Volume (OBV)
        df['OBV'] = (df['Volume'] * (~df['Close'].diff().le(0) * 2 - 1)).cumsum()
        df['OBV_MA'] = df['OBV'].rolling(window=20).mean()
        
        # 7. VWAP (Volume Weighted Average Price)
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        df['VWAP_Ratio'] = df['Close'] / df['VWAP']
        
        # 8. Ichimoku Cloud components
        nine_period_high = df['High'].rolling(window=9).max()
        nine_period_low = df['Low'].rolling(window=9).min()
        df['Tenkan_sen'] = (nine_period_high + nine_period_low) / 2
        
        period26_high = df['High'].rolling(window=26).max()
        period26_low = df['Low'].rolling(window=26).min()
        df['Kijun_sen'] = (period26_high + period26_low) / 2
        
        df['Senkou_Span_A'] = ((df['Tenkan_sen'] + df['Kijun_sen']) / 2).shift(26)
        
        # 9. Price Distance from Moving Averages
        df['Distance_SMA20'] = ((df['Close'] - df['SMA_20']) / df['SMA_20']) * 100
        df['Distance_SMA50'] = ((df['Close'] - df['SMA_50']) / df['SMA_50']) * 100
        
        # 10. Candlestick Patterns (simplified)
        df['Body_Size'] = abs(df['Close'] - df['Open'])
        df['Upper_Shadow'] = df['High'] - df[['Close', 'Open']].max(axis=1)
        df['Lower_Shadow'] = df[['Close', 'Open']].min(axis=1) - df['Low']
        df['Is_Doji'] = (df['Body_Size'] < (df['High'] - df['Low']) * 0.1).astype(int)
        
        # 11. Gap Analysis
        df['Gap'] = df['Open'] - df['Close'].shift(1)
        df['Gap_Percent'] = (df['Gap'] / df['Close'].shift(1)) * 100
        
        # 12. Volume Trends
        df['Volume_5D_Avg'] = df['Volume'].rolling(window=5).mean()
        df['Volume_20D_Avg'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Trend'] = df['Volume_5D_Avg'] / df['Volume_20D_Avg']
        
        # 13. Price Acceleration
        df['Price_Acceleration'] = df['Returns'].diff()
        
        # 14. Volatility Ratio
        df['High_Low_Range'] = ((df['High'] - df['Low']) / df['Close']) * 100
        df['Volatility_Ratio'] = df['Volatility'] / df['Volatility'].rolling(window=50).mean()  
        
        # Target variable
        df['Target'] = (df['Close'].shift(-self.prediction_days) > df['Close']).astype(int)
        df['Target_Return'] = df['Close'].shift(-self.prediction_days) / df['Close'] - 1
        
        df = df.dropna()
        
        return df
    
    def prepare_lstm_data(self, features_df):
        """Prepare data for LSTM model"""
        feature_columns = ['Close', 'Volume', 'SMA_20', 'RSI', 'MACD', 
                          'BB_Position', 'Volume_Ratio', 'Volatility']
        
        data = features_df[feature_columns].values
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(self.lookback_period, len(scaled_data) - self.prediction_days):
            X.append(scaled_data[i-self.lookback_period:i])
            y.append(scaled_data[i + self.prediction_days, 0])
        
        return np.array(X), np.array(y)
    
    def build_lstm_model(self, input_shape):
        """Build LSTM neural network"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train_lstm(self):
        """Train LSTM model for price prediction"""
        print(f"Training LSTM model for {self.prediction_days}-day prediction...")
        
        try:
            features_df = self.create_features()
            X, y = self.prepare_lstm_data(features_df)
            
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            model = self.build_lstm_model((X_train.shape[1], X_train.shape[2]))
            
            model.fit(X_train, y_train, 
                     batch_size=32, 
                     epochs=50, 
                     validation_data=(X_test, y_test),
                     verbose=0)
            
            last_sequence = X[-1:]
            prediction_scaled = model.predict(last_sequence, verbose=0)
            
            dummy = np.zeros((1, self.scaler.n_features_in_))
            dummy[0, 0] = prediction_scaled[0, 0]
            prediction = self.scaler.inverse_transform(dummy)[0, 0]
            
            current_price = self.data['Close'].iloc[-1]
            predicted_return = (prediction - current_price) / current_price
            
            return {
                'model': 'LSTM',
                'predicted_price': float(prediction),
                'current_price': float(current_price),
                'predicted_return': float(predicted_return),
                'days_ahead': int(self.prediction_days),
                'confidence': float(0.75),
                'holding_style': self.holding_style,
                'type': 'price'
            }
        except Exception as e:
            print(f"✗ LSTM error: {str(e)}")
            return None
    
    def train_xgboost(self):
        """Train XGBoost for directional prediction"""
        print(f"Training XGBoost model for {self.prediction_days}-day direction...")
        
        try:
            features_df = self.create_features()
            
            feature_columns = ['Returns', 'SMA_5', 'SMA_10', 'SMA_20', 'RSI', 
                              'MACD', 'MACD_Diff', 'BB_Position', 'Volume_Ratio',
                              'Momentum_5', 'Volatility', 'High_Low_Ratio']
            
            X = features_df[feature_columns].values
            y = features_df['Target'].values
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            
            last_features = X[-1:, :]
            prediction_proba = model.predict_proba(last_features)[0]
            prediction = model.predict(last_features)[0]
            
            feature_importance = dict(zip(feature_columns, model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            current_price = float(self.data['Close'].iloc[-1])
            
            return {
                'model': 'XGBoost',
                'direction': 'UP' if prediction == 1 else 'DOWN',
                'probability_up': float(prediction_proba[1]),
                'probability_down': float(prediction_proba[0]),
                'confidence': float(max(prediction_proba)),
                'days_ahead': int(self.prediction_days),
                'top_features': [(str(k), float(v)) for k, v in top_features],
                'current_price': current_price,
                'holding_style': self.holding_style,
                'type': 'direction'
            }
        except Exception as e:
            print(f"✗ XGBoost error: {str(e)}")
            return None
    
    def train_random_forest(self):
        """Train Random Forest for signal classification"""
        print(f"Training Random Forest for {self.prediction_days}-day signals...")
        
        try:
            features_df = self.create_features()
            
            feature_columns = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Signal',
                              'BB_Position', 'Volume_Ratio', 'Volatility', 
                              'Momentum_10', 'Close_Open_Ratio']
            
            X = features_df[feature_columns].values
            y = features_df['Target'].values
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            
            last_features = X[-1:, :]
            prediction_proba = model.predict_proba(last_features)[0]
            prediction = model.predict(last_features)[0]
            
            accuracy = model.score(X_test, y_test)
            current_price = float(self.data['Close'].iloc[-1])
            
            return {
                'model': 'Random Forest',
                'signal': 'BUY' if prediction == 1 else 'SELL',
                'probability_up': float(prediction_proba[1]),
                'probability_down': float(prediction_proba[0]),
                'confidence': float(max(prediction_proba)),
                'accuracy': float(accuracy),
                'days_ahead': int(self.prediction_days),
                'current_price': current_price,
                'holding_style': self.holding_style,
                'type': 'signal'
            }
        except Exception as e:
            print(f"✗ Random Forest error: {str(e)}")
            return None
    
    def train_prophet(self):
        """Train Prophet for long-term trend prediction"""
        print("Training Prophet for trend forecasting...")
        
        try:
            df = self.data[['Close']].reset_index()
            df.columns = ['ds', 'y']
            
            # Remove timezone
            if df['ds'].dtype == 'datetime64[ns, UTC]' or hasattr(df['ds'].dtype, 'tz'):
                df['ds'] = df['ds'].dt.tz_localize(None)
            
            df['ds'] = pd.to_datetime(df['ds'])
            
            model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05
            )
            
            model.fit(df)
            
            future = model.make_future_dataframe(periods=self.prediction_days)
            forecast = model.predict(future)
            
            current_price = self.data['Close'].iloc[-1]
            predicted_price = forecast['yhat'].iloc[-1]
            predicted_return = (predicted_price - current_price) / current_price
            
            trend = forecast['trend'].iloc[-1] - forecast['trend'].iloc[-30]
            trend_direction = 'UPTREND' if trend > 0 else 'DOWNTREND'
            
            return {
                'model': 'Prophet',
                'predicted_price': float(predicted_price),
                'current_price': float(current_price),
                'predicted_return': float(predicted_return),
                'trend': trend_direction,
                'trend_strength': abs(float(trend)),
                'days_ahead': int(self.prediction_days),
                'confidence': float(0.70),
                'holding_style': self.holding_style,
                'type': 'price'
            }
        except Exception as e:
            print(f"✗ Prophet error: {str(e)}")
            return None

    def train_gradient_boosting(self):
        """Train Gradient Boosting Classifier"""
        print(f"Training Gradient Boosting for {self.prediction_days}-day prediction...")
        
        try:
            from sklearn.ensemble import GradientBoostingClassifier
            
            features_df = self.create_features()
            
            feature_columns = ['Returns', 'SMA_20', 'RSI', 'MACD', 'BB_Position',
                              'Volume_Ratio', 'MFI', 'Stochastic_K', 'Williams_R',
                              'ROC_10', 'VWAP_Ratio', 'Distance_SMA20']
            
            X = features_df[feature_columns].values
            y = features_df['Target'].values
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            model = GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=4,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            
            last_features = X[-1:, :]
            prediction_proba = model.predict_proba(last_features)[0]
            prediction = model.predict(last_features)[0]
            
            accuracy = model.score(X_test, y_test)
            current_price = float(self.data['Close'].iloc[-1])
            
            return {
                'model': 'Gradient Boosting',
                'signal': 'BUY' if prediction == 1 else 'SELL',
                'probability_up': float(prediction_proba[1]),
                'probability_down': float(prediction_proba[0]),
                'confidence': float(max(prediction_proba)),
                'accuracy': float(accuracy),
                'days_ahead': int(self.prediction_days),
                'current_price': current_price,
                'holding_style': self.holding_style,
                'type': 'signal'
            }
        except Exception as e:
            print(f"✗ Gradient Boosting error: {str(e)}")
            return None

    def train_svm(self):
        """Train Support Vector Machine"""
        print(f"Training SVM for {self.prediction_days}-day prediction...")
        
        try:
            from sklearn.svm import SVC
            from sklearn.preprocessing import StandardScaler
            
            features_df = self.create_features()
            
            feature_columns = ['Returns', 'RSI', 'MACD', 'Stochastic_K',
                              'MFI', 'Volume_Ratio', 'Distance_SMA20', 'ATR']
            
            X = features_df[feature_columns].values
            y = features_df['Target'].values
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            model = SVC(
                kernel='rbf',
                C=1.0,
                probability=True,
                random_state=42
            )
            
            model.fit(X_train_scaled, y_train)
            
            last_features = scaler.transform(X[-1:, :])
            prediction_proba = model.predict_proba(last_features)[0]
            prediction = model.predict(last_features)[0]
            
            accuracy = model.score(X_test_scaled, y_test)
            current_price = float(self.data['Close'].iloc[-1])
            
            return {
                'model': 'SVM',
                'signal': 'BUY' if prediction == 1 else 'SELL',
                'probability_up': float(prediction_proba[1]),
                'probability_down': float(prediction_proba[0]),
                'confidence': float(max(prediction_proba)),
                'accuracy': float(accuracy),
                'days_ahead': int(self.prediction_days),
                'current_price': current_price,
                'holding_style': self.holding_style,
                'type': 'signal'
            }
        except Exception as e:
            print(f"✗ SVM error: {str(e)}")
            return None    
    
    def ensemble_prediction(self):
        """Combine all models for ensemble prediction"""
        print("\n🤖 Running ML Ensemble Prediction...")
        print("=" * 60)
        
        predictions = {}
        
        try:
            lstm_pred = self.train_lstm()
            if lstm_pred:
                predictions['lstm'] = lstm_pred
                print(f"✓ LSTM: Predicted ${lstm_pred['predicted_price']:.2f} "
                      f"({lstm_pred['predicted_return']*100:.2f}%)")
        except Exception as e:
            print(f"✗ LSTM failed: {str(e)}")
        
        try:
            xgb_pred = self.train_xgboost()
            if xgb_pred:
                predictions['xgboost'] = xgb_pred
                print(f"✓ XGBoost: {xgb_pred['direction']} "
                      f"(confidence: {xgb_pred['confidence']*100:.1f}%)")
        except Exception as e:
            print(f"✗ XGBoost failed: {str(e)}")
        
        try:
            rf_pred = self.train_random_forest()
            if rf_pred:
                predictions['random_forest'] = rf_pred
                print(f"✓ Random Forest: {rf_pred['signal']} "
                      f"(confidence: {rf_pred['confidence']*100:.1f}%)")
        except Exception as e:
            print(f"✗ Random Forest failed: {str(e)}")

        try:
            gb_pred = self.train_gradient_boosting()
            if gb_pred:
                predictions['gradient_boosting'] = gb_pred
                print(f"✓ Gradient Boosting: {gb_pred['signal']} "
                      f"(confidence: {gb_pred['confidence']*100:.1f}%)")
        except Exception as e:
            print(f"✗ Gradient Boosting failed: {str(e)}")
    
        try:
            svm_pred = self.train_svm()
            if svm_pred:
                predictions['svm'] = svm_pred
                print(f"✓ SVM: {svm_pred['signal']} "
                      f"(confidence: {svm_pred['confidence']*100:.1f}%)")
        except Exception as e:
            print(f"✗ SVM failed: {str(e)}")
        
        if self.holding_style == 'invest':
            try:
                prophet_pred = self.train_prophet()
                if prophet_pred:
                    predictions['prophet'] = prophet_pred
                    print(f"✓ Prophet: {prophet_pred['trend']} "
                          f"(${prophet_pred['predicted_price']:.2f})")
            except Exception as e:
                print(f"✗ Prophet failed: {str(e)}")
        
        ensemble = self.create_ensemble_signal(predictions)
        
        print("=" * 60)
        print(f"🎯 Ensemble Recommendation: {ensemble['recommendation']}")
        print(f"📊 Confidence: {ensemble['confidence']:.1f}%")
        print(f"🗳️ Votes: BUY={ensemble['buy_votes']}, SELL={ensemble['sell_votes']}, HOLD={ensemble['hold_votes']}")
        print("=" * 60 + "\n")
        
        return {
            'predictions': predictions,
            'ensemble': ensemble
        }
    
    def create_ensemble_signal(self, predictions):
        """Create final ensemble recommendation"""
        signals = []
        confidences = []
        
        if 'lstm' in predictions:
            pred_return = predictions['lstm']['predicted_return']
            if pred_return > 0.03:
                signals.append('BUY')
                confidences.append(predictions['lstm']['confidence'])
            elif pred_return < -0.03:
                signals.append('SELL')
                confidences.append(predictions['lstm']['confidence'])
            else:
                signals.append('HOLD')
                confidences.append(0.5)
        
        if 'xgboost' in predictions:
            if predictions['xgboost']['direction'] == 'UP':
                signals.append('BUY')
            else:
                signals.append('SELL')
            confidences.append(predictions['xgboost']['confidence'])
        
        if 'random_forest' in predictions:
            signals.append(predictions['random_forest']['signal'])
            confidences.append(predictions['random_forest']['confidence'])
        
        if 'prophet' in predictions and self.holding_style == 'invest':
            if predictions['prophet']['trend'] == 'UPTREND':
                signals.append('BUY')
            else:
                signals.append('SELL')
            confidences.append(predictions['prophet']['confidence'])
        
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        hold_count = signals.count('HOLD')
        
        if buy_count > sell_count and buy_count > hold_count:
            recommendation = 'BUY'
        elif sell_count > buy_count and sell_count > hold_count:
            recommendation = 'SELL'
        else:
            recommendation = 'HOLD'
        
        avg_confidence = float(np.mean(confidences) * 100) if confidences else 50.0
        
        return {
            'recommendation': recommendation,
            'confidence': avg_confidence,
            'buy_votes': int(buy_count),
            'sell_votes': int(sell_count),
            'hold_votes': int(hold_count),
            'total_models': int(len(signals))
        }
