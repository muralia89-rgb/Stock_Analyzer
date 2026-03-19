"""
Technical analysis module - calculates technical indicators
"""
import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    """Performs technical analysis on stock price data"""
    
    def __init__(self, price_data, holding_term='month'):
        """
        Initialize with historical price data
        
        Args:
            price_data (pandas.DataFrame): Historical OHLCV data
            holding_term (str): 'week', 'month', or 'long_term'
        """
        self.data = price_data.copy()
        self.holding_term = holding_term
        self.signals = {}
        
        # Set periods based on holding term
        if holding_term == 'week':
            self.rsi_period = 7
            self.macd_fast = 8
            self.macd_slow = 17
            self.macd_signal = 6
            self.sma_short = 10
            self.sma_medium = 20
            self.sma_long = 50
            self.volume_period = 10
            self.bb_period = 10
        elif holding_term == 'month':
            self.rsi_period = 14
            self.macd_fast = 12
            self.macd_slow = 26
            self.macd_signal = 9
            self.sma_short = 20
            self.sma_medium = 50
            self.sma_long = 100
            self.volume_period = 20
            self.bb_period = 20
        else:  # long_term
            self.rsi_period = 21
            self.macd_fast = 16
            self.macd_slow = 35
            self.macd_signal = 12
            self.sma_short = 50
            self.sma_medium = 100
            self.sma_long = 200
            self.volume_period = 30
            self.bb_period = 30
    
    def calculate_rsi(self):
        """
        Calculate Relative Strength Index (RSI)
        
        Returns:
            dict: RSI value and signal
        """
        try:
            period = self.rsi_period
            
            delta = self.data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            # Get RSI from 1 period ago for trend
            prev_rsi = rsi.iloc[-2] if len(rsi) > 1 else current_rsi
            
            # Determine signal with dynamic thresholds
            if self.holding_term == 'week':
                oversold = 25
                overbought = 75
            elif self.holding_term == 'month':
                oversold = 30
                overbought = 70
            else:  # long_term
                oversold = 28
                overbought = 72
            
            # Determine signal
            if current_rsi < oversold:
                signal = 'BUY'
                strength = 'oversold'
            elif current_rsi > overbought:
                signal = 'SELL'
                strength = 'overbought'
            elif current_rsi < (oversold + 10):
                signal = 'BUY'
                strength = 'slightly_oversold'
            elif current_rsi > (overbought - 10):
                signal = 'SELL'
                strength = 'slightly_overbought'
            else:
                signal = 'HOLD'
                strength = 'neutral'
            
            # Add trend direction
            trend = "rising" if current_rsi > prev_rsi else "falling"
            
            return {
                'indicator': 'RSI',
                'value': round(current_rsi, 2),
                'period': period,
                'signal': signal,
                'strength': strength,
                'trend': trend,
                'description': f'RSI({period}) is {round(current_rsi, 2)} - {strength} and {trend}'
            }
        except Exception as e:
            return {'indicator': 'RSI', 'error': str(e), 'signal': 'HOLD'}
    
    def calculate_macd(self):
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Returns:
            dict: MACD values and signal
        """
        try:
            fast = self.macd_fast
            slow = self.macd_slow
            signal_period = self.macd_signal
            
            exp1 = self.data['Close'].ewm(span=fast, adjust=False).mean()
            exp2 = self.data['Close'].ewm(span=slow, adjust=False).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal_period, adjust=False).mean()
            histogram = macd - signal_line
            
            # Check for crossovers
            current_macd = macd.iloc[-1]
            current_signal = signal_line.iloc[-1]
            prev_macd = macd.iloc[-2]
            prev_signal = signal_line.iloc[-2]
            
            if current_macd > current_signal and prev_macd <= prev_signal:
                signal = 'BUY'
                signal_type = 'bullish_crossover'
            elif current_macd < current_signal and prev_macd >= prev_signal:
                signal = 'SELL'
                signal_type = 'bearish_crossover'
            elif current_macd > current_signal:
                signal = 'BUY'
                signal_type = 'bullish'
            elif current_macd < current_signal:
                signal = 'SELL'
                signal_type = 'bearish'
            else:
                signal = 'HOLD'
                signal_type = 'neutral'
            
            return {
                'indicator': 'MACD',
                'macd': round(current_macd, 2),
                'signal_line': round(current_signal, 2),
                'histogram': round(histogram.iloc[-1], 2),
                'signal': signal,
                'type': signal_type,
                'periods': f'{fast}/{slow}/{signal_period}',
                'description': f'MACD({fast},{slow},{signal_period}) showing {signal_type}'
            }
        except Exception as e:
            return {'indicator': 'MACD', 'error': str(e), 'signal': 'HOLD'}
    
    def calculate_moving_averages(self):
        """
        Calculate Simple and Exponential Moving Averages
        
        Returns:
            dict: Moving average values and signals
        """
        try:
            sma_short = self.data['Close'].rolling(window=self.sma_short).mean()
            sma_medium = self.data['Close'].rolling(window=self.sma_medium).mean()
            
            # Only calculate long MA if we have enough data
            if len(self.data) >= self.sma_long:
                sma_long = self.data['Close'].rolling(window=self.sma_long).mean()
                has_long = True
            else:
                sma_long = None
                has_long = False
            
            ema_12 = self.data['Close'].ewm(span=12, adjust=False).mean()
            
            current_price = self.data['Close'].iloc[-1]
            
            signals = []
            
            # Price vs short-term SMA
            if current_price > sma_short.iloc[-1]:
                signals.append('BUY')
            else:
                signals.append('SELL')
            
            # Golden Cross / Death Cross (medium vs long)
            if has_long:
                if sma_medium.iloc[-1] > sma_long.iloc[-1]:
                    signals.append('BUY')
                else:
                    signals.append('SELL')
            
            # Short vs Medium
            if sma_short.iloc[-1] > sma_medium.iloc[-1]:
                signals.append('BUY')
            else:
                signals.append('SELL')
            
            buy_count = signals.count('BUY')
            sell_count = signals.count('SELL')
            
            if buy_count > sell_count:
                final_signal = 'BUY'
            elif sell_count > buy_count:
                final_signal = 'SELL'
            else:
                final_signal = 'HOLD'
            
            result = {
                'indicator': 'Moving_Averages',
                f'sma_{self.sma_short}': round(sma_short.iloc[-1], 2),
                f'sma_{self.sma_medium}': round(sma_medium.iloc[-1], 2),
                'current_price': round(current_price, 2),
                'signal': final_signal,
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'periods': f'{self.sma_short}/{self.sma_medium}',
                'description': f'{buy_count} bullish, {sell_count} bearish MA signals'
            }
            
            if has_long:
                result[f'sma_{self.sma_long}'] = round(sma_long.iloc[-1], 2)
            
            return result
        except Exception as e:
            return {'indicator': 'Moving_Averages', 'error': str(e), 'signal': 'HOLD'}
    
    def calculate_volume_analysis(self):
        """
        Analyze volume trends
        
        Returns:
            dict: Volume analysis and signal
        """
        try:
            period = self.volume_period
            avg_volume = self.data['Volume'].rolling(window=period).mean()
            current_volume = self.data['Volume'].iloc[-1]
            
            volume_ratio = current_volume / avg_volume.iloc[-1]
            
            # Adjust thresholds based on holding term
            if self.holding_term == 'week':
                very_high = 2.5
                high = 1.8
                low = 0.5
            elif self.holding_term == 'month':
                very_high = 2.0
                high = 1.5
                low = 0.5
            else:  # long_term
                very_high = 1.8
                high = 1.3
                low = 0.6
            
            if volume_ratio > very_high:
                signal = 'STRONG'
                strength = 'very_high'
            elif volume_ratio > high:
                signal = 'STRONG'
                strength = 'high'
            elif volume_ratio < low:
                signal = 'WEAK'
                strength = 'low'
            else:
                signal = 'NORMAL'
                strength = 'average'
            
            return {
                'indicator': 'Volume',
                'current_volume': int(current_volume),
                'avg_volume': int(avg_volume.iloc[-1]),
                'ratio': round(volume_ratio, 2),
                'period': period,
                'signal': signal,
                'strength': strength,
                'description': f'Volume({period}d avg) is {strength} ({round(volume_ratio, 2)}x average)'
            }
        except Exception as e:
            return {'indicator': 'Volume', 'error': str(e), 'signal': 'NORMAL'}
    
    def calculate_bollinger_bands(self):
        """
        Calculate Bollinger Bands
        
        Returns:
            dict: Bollinger Bands values and signal
        """
        try:
            period = self.bb_period
            std_dev = 2
            
            sma = self.data['Close'].rolling(window=period).mean()
            std = self.data['Close'].rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            current_price = self.data['Close'].iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            current_sma = sma.iloc[-1]
            
            # Calculate percentage position
            bb_range = current_upper - current_lower
            price_position = (current_price - current_lower) / bb_range * 100
            
            # Determine position
            if current_price >= current_upper:
                signal = 'SELL'
                position = 'at_upper_band'
            elif current_price <= current_lower:
                signal = 'BUY'
                position = 'at_lower_band'
            elif price_position > 70:
                signal = 'SELL'
                position = 'near_upper'
            elif price_position < 30:
                signal = 'BUY'
                position = 'near_lower'
            elif current_price > current_sma:
                signal = 'HOLD'
                position = 'above_middle'
            else:
                signal = 'HOLD'
                position = 'below_middle'
            
            return {
                'indicator': 'Bollinger_Bands',
                'upper_band': round(current_upper, 2),
                'middle_band': round(current_sma, 2),
                'lower_band': round(current_lower, 2),
                'current_price': round(current_price, 2),
                'position_pct': round(price_position, 1),
                'period': period,
                'signal': signal,
                'position': position,
                'description': f'BB({period}): Price {position} ({round(price_position, 1)}%)'
            }
        except Exception as e:
            return {'indicator': 'Bollinger_Bands', 'error': str(e), 'signal': 'HOLD'}
    
    def get_all_technical_signals(self):
        """
        Calculate all technical indicators
        
        Returns:
            list: List of all technical indicator signals
        """
        signals = [
            self.calculate_rsi(),
            self.calculate_macd(),
            self.calculate_moving_averages(),
            self.calculate_volume_analysis(),
            self.calculate_bollinger_bands()
        ]
        
        return [s for s in signals if 'error' not in s]
