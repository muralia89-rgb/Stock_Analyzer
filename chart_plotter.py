"""
Interactive chart plotter using Plotly
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class InteractiveChartPlotter:
    """Creates interactive stock charts with technical indicators"""
    
    def __init__(self, data, symbol):
        """
        Initialize chart plotter
        
        Args:
            data (pd.DataFrame): Historical price data (OHLCV)
            symbol (str): Stock symbol
        """
        self.data = data.copy()
        self.symbol = symbol
    
    def calculate_indicators_for_chart(self):
        """Calculate all indicators for visualization"""
        # Moving Averages
        self.data['SMA_20'] = self.data['Close'].rolling(window=20).mean()
        self.data['SMA_50'] = self.data['Close'].rolling(window=50).mean()
        self.data['SMA_200'] = self.data['Close'].rolling(window=200).mean()
        self.data['EMA_12'] = self.data['Close'].ewm(span=12, adjust=False).mean()
        self.data['EMA_26'] = self.data['Close'].ewm(span=26, adjust=False).mean()
        
        # Bollinger Bands
        sma_20 = self.data['Close'].rolling(window=20).mean()
        std_20 = self.data['Close'].rolling(window=20).std()
        self.data['BB_Upper'] = sma_20 + (std_20 * 2)
        self.data['BB_Lower'] = sma_20 - (std_20 * 2)
        self.data['BB_Middle'] = sma_20
        
        # RSI
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        self.data['MACD'] = self.data['EMA_12'] - self.data['EMA_26']
        self.data['MACD_Signal'] = self.data['MACD'].ewm(span=9, adjust=False).mean()
        self.data['MACD_Hist'] = self.data['MACD'] - self.data['MACD_Signal']
        
        # Volume MA
        self.data['Volume_MA'] = self.data['Volume'].rolling(window=20).mean()
    
    def create_candlestick_chart(self, show_indicators=None):
        """
        Create interactive candlestick chart with optional indicators
        
        Args:
            show_indicators (list): List of indicators to show
                Options: 'sma', 'ema', 'bollinger', 'rsi', 'macd', 'volume'
        
        Returns:
            plotly.graph_objects.Figure: Interactive chart
        """
        if show_indicators is None:
            show_indicators = ['sma', 'volume']
        
        # Calculate indicators
        self.calculate_indicators_for_chart()
        
        # Determine number of subplots
        num_rows = 1
        row_heights = [0.7]
        specs = [[{"secondary_y": False}]]
        
        if 'rsi' in show_indicators:
            num_rows += 1
            row_heights.append(0.15)
            specs.append([{"secondary_y": False}])
        
        if 'macd' in show_indicators:
            num_rows += 1
            row_heights.append(0.15)
            specs.append([{"secondary_y": False}])
        
        if 'volume' in show_indicators:
            num_rows += 1
            row_heights.append(0.15)
            specs.append([{"secondary_y": False}])
        
        # Create subplots
        fig = make_subplots(
            rows=num_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            specs=specs
        )
        
        # Main candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )
        
        # Add Moving Averages
        if 'sma' in show_indicators:
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['SMA_20'],
                    name='SMA 20',
                    line=dict(color='orange', width=1)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['SMA_50'],
                    name='SMA 50',
                    line=dict(color='blue', width=1)
                ),
                row=1, col=1
            )
            
            if len(self.data) >= 200:
                fig.add_trace(
                    go.Scatter(
                        x=self.data.index,
                        y=self.data['SMA_200'],
                        name='SMA 200',
                        line=dict(color='red', width=1)
                    ),
                    row=1, col=1
                )
        
        # Add EMAs
        if 'ema' in show_indicators:
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['EMA_12'],
                    name='EMA 12',
                    line=dict(color='purple', width=1, dash='dot')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['EMA_26'],
                    name='EMA 26',
                    line=dict(color='brown', width=1, dash='dot')
                ),
                row=1, col=1
            )
        
        # Add Bollinger Bands
        if 'bollinger' in show_indicators:
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['BB_Upper'],
                    name='BB Upper',
                    line=dict(color='gray', width=1, dash='dash'),
                    showlegend=True
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['BB_Lower'],
                    name='BB Lower',
                    line=dict(color='gray', width=1, dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(128, 128, 128, 0.1)',
                    showlegend=True
                ),
                row=1, col=1
            )
        
        # RSI subplot
        current_row = 2
        if 'rsi' in show_indicators:
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['RSI'],
                    name='RSI',
                    line=dict(color='purple', width=2)
                ),
                row=current_row, col=1
            )
            
            # Add RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="Overbought (70)", 
                         row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         annotation_text="Oversold (30)", 
                         row=current_row, col=1)
            
            fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1)
            current_row += 1
        
        # MACD subplot
        if 'macd' in show_indicators:
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['MACD'],
                    name='MACD',
                    line=dict(color='blue', width=2)
                ),
                row=current_row, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['MACD_Signal'],
                    name='Signal',
                    line=dict(color='orange', width=2)
                ),
                row=current_row, col=1
            )
            
            # MACD Histogram
            colors = ['red' if val < 0 else 'green' for val in self.data['MACD_Hist']]
            fig.add_trace(
                go.Bar(
                    x=self.data.index,
                    y=self.data['MACD_Hist'],
                    name='Histogram',
                    marker_color=colors,
                    opacity=0.3
                ),
                row=current_row, col=1
            )
            
            fig.update_yaxes(title_text="MACD", row=current_row, col=1)
            current_row += 1
        
        # Volume subplot
        if 'volume' in show_indicators:
            colors = ['red' if self.data['Close'].iloc[i] < self.data['Open'].iloc[i] 
                     else 'green' for i in range(len(self.data))]
            
            fig.add_trace(
                go.Bar(
                    x=self.data.index,
                    y=self.data['Volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.5
                ),
                row=current_row, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data['Volume_MA'],
                    name='Volume MA',
                    line=dict(color='orange', width=2)
                ),
                row=current_row, col=1
            )
            
            fig.update_yaxes(title_text="Volume", row=current_row, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'{self.symbol} - Interactive Price Chart',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            height=800,
            hovermode='x unified',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Add range selector buttons
        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=2, label="2Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ]),
                bgcolor="lightgray",
                activecolor="gray"
            ),
            rangeslider=dict(visible=False),
            type="date"
        )
        
        return fig
    
    def create_comparison_chart(self, timeframes=['1M', '3M', '6M', '1Y']):
        """
        Create side-by-side comparison charts for different timeframes
        
        Args:
            timeframes (list): List of timeframes to show
        
        Returns:
            dict: Dictionary of figures for each timeframe
        """
        charts = {}
        
        for tf in timeframes:
            # Filter data based on timeframe
            if tf == '1M':
                days = 30
            elif tf == '3M':
                days = 90
            elif tf == '6M':
                days = 180
            elif tf == '1Y':
                days = 365
            else:
                days = len(self.data)
            
            data_subset = self.data.tail(days)
            
            # Create simple candlestick for comparison
            fig = go.Figure(data=[
                go.Candlestick(
                    x=data_subset.index,
                    open=data_subset['Open'],
                    high=data_subset['High'],
                    low=data_subset['Low'],
                    close=data_subset['Close'],
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                )
            ])
            
            fig.update_layout(
                title=f'{tf} View',
                xaxis_title='Date',
                yaxis_title='Price',
                height=300,
                template='plotly_white',
                showlegend=False
            )
            
            charts[tf] = fig
        
        return charts
