# Chit Fund Analyzer

A Python package for analyzing chit fund investments with robust validation, type safety, and comprehensive analysis capabilities.

## Features

- 🔒 **Type Safety**: Uses Pydantic for robust data validation and type checking
- 🏗️ **Clean Architecture**: Well-structured code with separated concerns
- 🔧 **Extensible Design**: Easy to add new analysis methods and validation rules
- ⚠️ **Error Handling**: Comprehensive error handling with custom exceptions
- 🐍 **Modern Python**: Uses modern Python features and best practices
- 📊 **Comprehensive Analysis**: IRR calculations, scenario analysis, and optimization

## Installation

This package requires Python 3.13+ and the following dependencies:

```bash
# Install dependencies using uv (recommended)
uv add pydantic numpy-financial pandas openpyxl

# Or using pip
pip install pydantic numpy-financial pandas openpyxl
```

## Quick Start

```python
from chit_fund_analyzer import ChitFundConfig, ChitFundAnalyzer
from decimal import Decimal

# Create configuration with automatic validation
config = ChitFundConfig(
    total_installments=14,
    current_installment_number=5,
    full_chit_value=Decimal('700000'),
    chit_frequency_per_year=2,  # Bi-annual payments
    previous_installments=[
        Decimal('42000'), Decimal('40000'), 
        Decimal('40000'), Decimal('43000')
    ],
    bid_amount=Decimal('100000')
)

# Perform analysis
analyzer = ChitFundAnalyzer(config)
result = analyzer.analyze()

# Display results
print(f"Prize Amount: ₹{result.prize_amount:,.2f}")
print(f"Annual IRR: {result.annual_irr:.2%}")
```

## Core Components

### 1. ChitFundConfig
Pydantic model for configuration with built-in validation:
- Validates installment counts and sequences
- Ensures bid amounts are reasonable
- Provides type safety for all inputs
- Supports custom winner installment amounts

### 2. ChitFundAnalyzer
Main analysis engine:
- Calculates prize amounts
- Generates cashflow arrays
- Computes IRR (Internal Rate of Return)
- Provides formatted results

### 3. ScenarioAnalyzer
Advanced analysis capabilities:
- Multiple bid scenario analysis
- Optimization for target IRR
- Payment frequency comparisons
- Export to pandas DataFrames

## Example: Scenario Analysis

```python
from chit_fund_analyzer import ScenarioAnalyzer
from decimal import Decimal

# Create scenario analyzer
scenario_analyzer = ScenarioAnalyzer(config)

# Analyze multiple bid amounts
bid_amounts = [Decimal(str(x)) for x in [80000, 100000, 120000]]
scenarios = scenario_analyzer.analyze_bid_scenarios(bid_amounts)

# Create DataFrame for easy viewing
df = scenario_analyzer.create_scenario_dataframe(scenarios)
print(df)
```

## Example: Find Optimal Bid

```python
# Find bid amount that maximizes IRR
optimal = scenario_analyzer.find_optimal_bid(
    bid_range=(80000, 150000),
    step_size=Decimal('2000')
)

print(f"Optimal bid: ₹{optimal['optimal_bid_amount']:,.0f}")
print(f"Expected IRR: {optimal['optimal_annual_irr_formatted']}")
```

## Validation Features

The package includes comprehensive input validation:

```python
# This will raise a validation error
try:
    invalid_config = ChitFundConfig(
        total_installments=10,
        current_installment_number=15,  # > total_installments!
        full_chit_value=Decimal('500000'),
        chit_frequency_per_year=12,
        previous_installments=[],
        bid_amount=Decimal('50000')
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

## Module Structure

```
chit_fund_analyzer/
├── __init__.py          # Package initialization and exports
├── models.py           # Pydantic models and validation
├── analyzer.py         # Core analysis functionality
├── scenario.py         # Scenario analysis and optimization
├── utils.py           # Utility functions and formatters
└── exceptions.py      # Custom exception classes
```

## Advanced Usage

### Custom Winner Installment
```python
config = ChitFundConfig(
    # ... other parameters ...
    winner_installment_amount=Decimal('45000')  # Custom amount
)
```

### Frequency Comparison
```python
# Compare same bid across different payment frequencies
comparison = scenario_analyzer.compare_frequencies(
    bid_amount=Decimal('100000'),
    frequencies=[1, 2, 4, 12]  # Annual, bi-annual, quarterly, monthly
)
```

### Export to Excel
```python
from chit_fund_analyzer.utils import export_to_excel

# Export multiple analysis results
export_data = {
    'Base Analysis': base_df,
    'Scenarios': scenario_df,
    'Frequency Analysis': frequency_df
}
export_to_excel(export_data, 'chit_analysis.xlsx')
```

## Testing

Run the included test script to verify installation:

```bash
python test_module.py
```

## Demo Notebook

For comprehensive examples and interactive analysis, see:
- `chit_fund_analyzer_demo.ipynb` - Complete walkthrough with examples

## Contributing

The package is designed for extensibility:

1. **Add new validators**: Extend validation logic in `models.py`
2. **New analysis methods**: Add methods to `analyzer.py`
3. **Custom scenarios**: Extend `scenario.py` with new analysis types
4. **Utility functions**: Add helpers to `utils.py`
5. **Custom exceptions**: Define specific errors in `exceptions.py`

## Error Handling

The package provides specific exceptions for different error types:
- `ChitFundAnalysisError`: General analysis errors
- `ValidationError`: Input validation failures
- `CalculationError`: Mathematical calculation issues
- `ConfigurationError`: Configuration problems

## Requirements

- Python 3.13+
- pydantic 2.x
- numpy-financial
- pandas
- openpyxl (for Excel export)

## License

This project is open source and available under the MIT License.