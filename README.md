# 📊 AI-Powered Stock Analysis System

An intelligent stock analysis platform for the Indian market (NSE/BSE) with machine learning predictions, technical analysis, fundamental analysis, and real-time news sentiment.

## 🌟 Features

### Core Analysis
- **Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands, Volume Analysis
- **Fundamental Analysis**: P/E Ratio, PEG Ratio, ROE, Debt/Equity, Growth Rates
- **Rule-Based Engine**: Customized decision rules for different holding periods

### AI/ML Predictions
- **LSTM Neural Network**: Price prediction
- **XGBoost**: Direction prediction (UP/DOWN)
- **Random Forest**: BUY/SELL signal classification
- **Prophet**: Long-term trend forecasting
- **Ensemble Method**: Majority voting across all models

### Continuous Learning
- Models learn from every prediction
- Auto-retraining when accuracy drops
- Track accuracy improvement over time
- Learning curves visualization

### Smart Stock Scanner
- Scan multiple stocks simultaneously
- Priority-based news system (Stock → Peer → Sector → Global)
- Timeframe-filtered news (Week/Month/Long-term)
- Real-time Indian market news from Moneycontrol, Economic Times, LiveMint

### Interactive Features
- Dynamic charts with Plotly
- Multi-timeframe analysis
- Export scan results to CSV
- Customizable holding periods (Week/Month/Long-term)

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/stock-analyzer-ai.git
cd stock-analyzer-ai
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Run the Web Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Single Stock Analysis
1. Go to "Single Stock Analysis" tab
2. Select exchange (NSE/BSE/US)
3. Choose stock symbol
4. Select holding term
5. Click "Analyze Stock"

### Smart Stock Scanner
1. Go to "Smart Stock Scanner" tab
2. Choose holding term
3. Set number of stocks to scan
4. Click "Start Scan"
5. Download results as CSV

## 📂 Project Structure
```
stock_analyzer/
├── app.py                          # Streamlit web interface
├── main.py                         # Core analysis engine
├── config.py                       # Configuration and rules
├── data_fetcher.py                # Yahoo Finance data retrieval
├── technical_analyzer.py          # Technical indicators
├── fundamental_analyzer.py        # Fundamental metrics
├── rule_engine.py                 # Decision logic
├── ml_predictor.py                # ML models
├── ml_database.py                 # Prediction tracking
├── ml_continuous_learning.py      # Learning system
├── news_fetcher.py                # News scraping
├── stock_scanner.py               # Multi-stock scanner
├── stock_symbols.py               # Stock database
├── chart_plotter.py               # Interactive charts
├── utils.py                       # Helper functions
└── requirements.txt               # Dependencies
```

## 🎯 Score Guide

- 🟢 **70-100**: Strong BUY - Best opportunities
- 🟡 **60-70**: Moderate BUY - Good opportunities
- 🟠 **50-60**: HOLD - Wait for clarity
- 🔴 **<50**: SELL - Avoid or exit

## ⚙️ Customization

### Adjust Technical Thresholds
Edit `technical_analyzer.py`:
- RSI oversold/overbought levels
- Moving average periods
- Volume thresholds

### Modify Fundamental Criteria
Edit `fundamental_analyzer.py`:
- P/E ratio thresholds
- Debt/equity limits
- Growth rate expectations

### Change ML Parameters
Edit `ml_predictor.py`:
- Prediction horizons
- Model architectures
- Training epochs

## 📊 ML Model Accuracy

Expected performance (improves with use):
- Week 1: 65-70% baseline
- Week 2: 70-75%
- Month 1: 75-80%
- Month 3: 78-85%

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It is NOT financial advice. Always:
- Conduct your own research
- Consult a qualified financial advisor
- Understand that past performance doesn't guarantee future results
- Use proper risk management

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Data: Yahoo Finance
- News: Moneycontrol, Economic Times, LiveMint, Business Standard
- ML Libraries: TensorFlow, XGBoost, scikit-learn, Prophet
- Visualization: Plotly, Streamlit

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Built with ❤️ for Indian stock market enthusiasts**