# Chit Fund Analyzer

A comprehensive, modular Python library for analyzing chit fund investments with IRR calculations and scenario analysis.

## Overview

This project provides tools to analyze chit fund investments by calculating Internal Rate of Return (IRR), comparing different bid amounts, and identifying optimal bidding strategies. The codebase follows clean code principles and SOLID design patterns for maintainability and extensibility.

## Features

- ✅ **IRR Calculation**: Accurate annual IRR computation for chit fund investments
- ✅ **Scenario Analysis**: Compare multiple bid amounts side-by-side
- ✅ **Optimal Bid Finder**: Automatically identify the best bidding strategy
- ✅ **Validation**: Built-in parameter validation and error handling
- ✅ **Extensible Design**: Easy to extend with new features and metrics
- ✅ **Clean Code**: Follows PEP 8, type hints, comprehensive documentation
- ✅ **Well Tested**: Unit tests with pytest for reliability

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from chit_fund_calculator import (
    ChitFundConfig, ChitFundCalculator, 
    ScenarioAnalyzer, ChitFrequency
)

# Configure chit fund
config = ChitFundConfig(
    total_installments=14,
    current_installment_number=4,
    full_chit_value=700000,
    chit_frequency_per_year=ChitFrequency.SEMI_ANNUAL.value,
    previous_installments=[42000, 40000, 40000, 43000],
    winner_installment_amount=50000
)

# Analyze scenarios
analyzer = ScenarioAnalyzer()
results = analyzer.analyze_scenarios(
    config=config,
    bid_range=(50000, 200000),
    bid_step=10000
)

# Find optimal bid
optimal = analyzer.find_optimal_bid(config=config)
print(f"Optimal bid: ₹{optimal['bid_amount']:,.0f}")
print(f"Annual IRR: {optimal['annual_irr']:.2f}%")
```

## Project Structure

```
chit_fund_analyzer/
├── chit_fund_calculator.py      # Core module with all classes
├── chit_intrest_cal.ipynb       # Interactive Jupyter notebook
├── test_chit_fund_calculator.py # Comprehensive unit tests
├── requirements.txt              # Python dependencies
├── USAGE_GUIDE.md               # Detailed usage documentation
└── README.md                     # This file
```

## Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)**: Comprehensive guide with examples, API reference, and extension patterns
- **Jupyter Notebook**: `chit_intrest_cal.ipynb` contains interactive examples

## Key Classes

### ChitFundConfig
Configuration dataclass with automatic validation for all parameters.

### ChitFundCalculator
Core calculation engine for prize amounts, cashflows, and IRR.

### ScenarioAnalyzer
Multi-scenario analysis tool for comparing different bid strategies.

### ReportGenerator
Utilities for formatting and exporting analysis results.

## Running Tests

```bash
# Run all tests
pytest test_chit_fund_calculator.py

# Run with coverage
pytest --cov=chit_fund_calculator test_chit_fund_calculator.py

# Run specific test class
pytest test_chit_fund_calculator.py::TestChitFundCalculator
```

## Example Output

```
================================================================================
                      BID AMOUNT SCENARIO ANALYSIS                      
================================================================================
 Bid Amount  Prize Received  Total Repayment  Net Interest Cost  Annual IRR (%)  Effective Interest (%)
     50,000         650,000          665,000             15,000           16.45                    2.31
    100,000         600,000          665,000             65,000           12.34                   10.83
    150,000         550,000          665,000            115,000            8.92                   20.91
    200,000         500,000          665,000            165,000            5.87                   33.00

================================================================================
                         OPTIMAL BID STRATEGY                          
================================================================================
Bid Amount: ₹50,000
Prize Received: ₹650,000
Annual IRR: 16.45%
Net Interest Cost: ₹15,000
```

## Future Enhancements

- 📊 Visualization with matplotlib/plotly
- 📈 Sensitivity analysis for parameter variations
- 📊 Risk metrics (standard deviation, VaR)
- 📅 Time-based analysis with actual dates
- 💰 Tax calculations and implications
- 🔄 Multi-winner scenarios
- 📱 Web interface for analysis

## Contributing

Contributions are welcome! Please ensure:
1. Code follows PEP 8 style guidelines
2. All functions have type hints and docstrings
3. Unit tests are included for new features
4. Documentation is updated

## License

This project is open source and available for educational and personal use.

## Author

Jagadeesan Muthuvel

## Acknowledgments

Built with clean code principles and SOLID design patterns for maintainability and extensibility.
