# Streamlit Web Application

A comprehensive web interface for the Chit Fund Analyzer with real-time calculations, interactive visualizations, and scenario analysis.

## Features

### 🔧 **Interactive Configuration**
- Sidebar-based input form for all chit fund parameters
- Real-time validation and error handling
- Support for custom winner installment amounts
- Previous installments tracker

### 📊 **Real-time Analysis**
- Instant IRR calculations
- Prize amount computation
- Cashflow visualization
- Performance metrics dashboard

### 🔍 **Scenario Analysis**
- Compare multiple bid amounts simultaneously
- Interactive range selection (min/max bid amounts)
- Customizable number of scenarios
- Optimization for best returns

### 📈 **Rich Visualizations**
- **Cashflow Chart**: Bar chart showing inflows and outflows by period
- **IRR vs Bid Amount**: Line chart showing return trends
- **Prize Amount Analysis**: Bar chart showing prize amounts for different bids
- **IRR Distribution**: Histogram showing return distribution
- **Bid vs Prize Relationship**: Scatter plot with color-coded IRR values

### 🎯 **Intelligent Insights**
- Automated analysis of your investment strategy
- Personalized recommendations based on your configuration
- Risk and return trade-off analysis
- Best and worst case scenario identification

### 📄 **Export Capabilities**
- Download basic analysis as CSV
- Export scenario analysis results
- Generate comprehensive markdown reports
- Save configurations for future use

## Getting Started

### Prerequisites
- Python 3.13+
- Virtual environment with all dependencies installed

### Running the App

**Option 1: Using the launch script (Windows)**
```bash
run_app.bat
```

**Option 2: Using Python script (Cross-platform)**
```bash
python run_app.py
```

**Option 3: Direct Streamlit command**
```bash
# Using virtual environment
D:/side_projects/chit_fund_analyzer/.venv/Scripts/python.exe -m streamlit run streamlit_app.py

# Or if streamlit is in your PATH
streamlit run streamlit_app.py --server.port 8501
```

### Accessing the App
Once started, open your web browser and navigate to:
- **Local URL**: http://localhost:8501
- **Network URL**: Available for other devices on your network

## User Interface Guide

### Sidebar - Configuration Panel
1. **📊 Basic Parameters**
   - Total Installments (1-100)
   - Current Installment Number
   - Full Chit Value (₹)
   - Payment Frequency (Annual, Bi-annual, Quarterly, etc.)
   - Your Bid Amount (₹)

2. **💸 Previous Installments**
   - Enter amounts for each previous installment
   - Automatic validation against installment count

3. **⚙️ Advanced Options**
   - Custom winner installment amount
   - Override default calculations

### Main Panel - Results & Analysis

#### 🚀 Analysis Results
- **Prize Amount**: What you'll receive if you win
- **Annual IRR**: Your expected annual return rate
- **Winner Installment**: Amount you'll pay each period
- **Net Benefit**: Overall financial impact

#### 💰 Cashflow Visualization
Interactive bar chart showing:
- Red bars: Money going out (installments)
- Green bars: Money coming in (prize)
- Period-by-period breakdown

#### 🔍 Scenario Analysis
1. Set min/max bid range
2. Choose number of scenarios to analyze
3. View comprehensive visualizations:
   - IRR trends
   - Prize amount comparisons
   - Distribution analysis
   - Optimization results

#### 💡 Insights & Recommendations
- Automated analysis of your investment
- Risk assessment
- Strategic recommendations
- Performance categorization

## Sample Usage Workflow

1. **Setup**: Enter your chit fund details in the sidebar
2. **Basic Analysis**: Click "🚀 Analyze Chit Fund" to see results
3. **Scenario Planning**: Set bid range and run scenario analysis
4. **Analysis Review**: Review best and worst case scenarios from the range
5. **Decision Making**: Use insights to make informed choices
6. **Export**: Download results for record keeping

## Key Metrics Explained

### 📈 Annual IRR (Internal Rate of Return)
- **>15%**: 🟢 Excellent returns
- **10-15%**: 🟡 Good returns
- **5-10%**: 🟠 Average returns
- **<5%**: 🔴 Poor returns

### 🎯 Bid Strategy Analysis
- **Conservative Bidding** (<10% of chit value): Lower risk, moderate returns
- **Balanced Bidding** (10-30% of chit value): Optimal risk-return trade-off
- **Aggressive Bidding** (>30% of chit value): Higher risk, potential for better long-term returns

### ⏰ Timing Analysis
- **Early Winner** (First 30% of installments): Good liquidity, lower returns
- **Mid-term Winner** (30-70% of installments): Balanced approach
- **Late Winner** (Last 30% of installments): Higher returns due to time value

## Troubleshooting

### Common Issues

**1. Configuration Errors**
- Check that current installment ≤ total installments
- Ensure previous installments count matches current installment - 1
- Verify bid amount is less than full chit value

**2. Scenario Analysis Errors**
- Ensure max bid > min bid
- Check that bid amounts are reasonable compared to chit value
- Verify number of scenarios is between 3-50

**3. Display Issues**
- Refresh the browser if charts don't load
- Check browser console for JavaScript errors
- Ensure stable internet connection

### Performance Tips
- Use reasonable scenario counts (10-20) for better performance
- Avoid extreme bid ranges that might cause calculation errors
- Regular analysis updates don't require page refresh

## Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **Pydantic**: Data validation
- **Numpy Financial**: IRR calculations

### Architecture
```
streamlit_app.py
├── Configuration Input (Sidebar)
├── Analysis Engine (ChitFundAnalyzer)
├── Scenario Processing (ScenarioAnalyzer)
├── Visualization Layer (Plotly)
└── Export Functions (CSV/Markdown)
```

### Browser Compatibility
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Security & Privacy

- **No data persistence**: All calculations are done locally
- **No external API calls**: Everything runs on your machine
- **Privacy first**: Your financial data never leaves your computer

## Contributing

The Streamlit app is built with extensibility in mind:

1. **New visualizations**: Add to the `create_*_chart()` functions
2. **Enhanced insights**: Extend the `display_summary_insights()` function
3. **Additional exports**: Add new formats in `export_analysis()`
4. **UI improvements**: Modify the CSS in `add_custom_css()`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the main module documentation
3. Test with the provided sample configuration
4. Verify all dependencies are properly installed