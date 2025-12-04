# Chit Fund Calculator - Usage Guide

## Overview

The Chit Fund Calculator is a modular, extensible Python library for analyzing chit fund investments, calculating Internal Rate of Return (IRR), and performing scenario analysis for different bid amounts.

## Architecture

The module follows clean code principles and SOLID design patterns:

```
chit_fund_calculator.py
├── ChitFrequency (Enum)           # Payment frequency options
├── ChitFundConfig (Dataclass)     # Configuration with validation
├── ChitFundResult (Dataclass)     # Analysis result container
├── ChitFundCalculator (Class)     # Core calculation logic
├── ScenarioAnalyzer (Class)       # Multi-scenario analysis
└── ReportGenerator (Class)        # Reporting utilities
```

## Quick Start

### 1. Basic Setup

```python
from chit_fund_calculator import (
    ChitFundConfig,
    ChitFundCalculator,
    ScenarioAnalyzer,
    ReportGenerator,
    ChitFrequency
)

# Configure your chit fund
config = ChitFundConfig(
    total_installments=14,
    current_installment_number=4,
    full_chit_value=700000,
    chit_frequency_per_year=ChitFrequency.SEMI_ANNUAL.value,
    previous_installments=[42000, 40000, 40000, 43000],
    winner_installment_amount=50000
)
```

### 2. Analyze a Single Bid Amount

```python
calculator = ChitFundCalculator()
result = calculator.analyze_single_bid(config, bid_amount=100000)

print(f"Annual IRR: {result.annual_irr * 100:.2f}%")
print(f"Prize Received: ₹{result.prize_amount:,.0f}")
```

### 3. Scenario Analysis

```python
analyzer = ScenarioAnalyzer()

# Analyze multiple bid amounts
scenario_results = analyzer.analyze_scenarios(
    config=config,
    bid_range=(50000, 210000),
    bid_step=10000
)

# Display results
report = ReportGenerator()
report.print_scenario_analysis(scenario_results)
```

### 4. Find Optimal Bid

```python
optimal = analyzer.find_optimal_bid(
    config=config,
    bid_range=(50000, 210000),
    bid_step=10000
)

report.print_optimal_strategy(optimal)
```

## Classes and Methods

### ChitFundConfig

Configuration container with automatic validation.

**Parameters:**
- `total_installments`: Total number of installments
- `current_installment_number`: When you plan to win
- `full_chit_value`: Total chit fund value
- `chit_frequency_per_year`: Payment frequency (use ChitFrequency enum)
- `previous_installments`: List of amounts already paid
- `winner_installment_amount`: Fixed amount after winning

**Validation:**
- Ensures all numeric values are positive
- Validates installment count matches configuration
- Checks frequency is valid

### ChitFundCalculator

Core calculation engine for chit fund analysis.

**Methods:**

#### `calculate_prize_amount(full_chit_value, bid_amount)`
Calculates prize = chit_value - bid_amount

#### `create_cashflows(...)`
Generates cashflow list for IRR calculation:
- Negative: Money paid (installments)
- Positive: Money received (prize)

#### `calculate_annual_irr(cashflows, frequency_per_year)`
Computes annualized Internal Rate of Return

#### `analyze_single_bid(config, bid_amount)`
Returns `ChitFundResult` with complete analysis

### ScenarioAnalyzer

Multi-scenario comparison tool.

**Methods:**

#### `analyze_scenarios(config, bid_amounts=None, bid_range=None, bid_step=10000)`
Analyze multiple bid amounts:
- `bid_amounts`: Specific list of bids to test
- `bid_range`: Tuple of (min, max) for range
- `bid_step`: Increment for range testing

Returns: pandas DataFrame with all scenarios

#### `find_optimal_bid(config, ...)`
Identifies best bid based on lowest IRR

Returns: Dictionary with optimal bid details

### ReportGenerator

Formatting and export utilities.

**Methods:**

#### `print_scenario_analysis(df, title)`
Pretty-print scenario comparison table

#### `print_optimal_strategy(optimal_result, title)`
Display optimal bid recommendation

#### `export_to_csv(df, filename)`
Export results to CSV file

## Advanced Usage

### Custom Bid Amounts

```python
# Test specific bid amounts
custom_bids = [75000, 100000, 125000, 150000]
results = analyzer.analyze_scenarios(
    config=config,
    bid_amounts=custom_bids
)
```

### Different Frequencies

```python
# Monthly chit fund
config_monthly = ChitFundConfig(
    total_installments=24,
    current_installment_number=6,
    full_chit_value=600000,
    chit_frequency_per_year=ChitFrequency.MONTHLY.value,
    previous_installments=[25000] * 5,
    winner_installment_amount=25000
)
```

### Export Results

```python
# Save analysis to CSV
report.export_to_csv(scenario_results, "my_analysis.csv")
```

### Access Raw Data

```python
# Get detailed result object
result = calculator.analyze_single_bid(config, 100000)

print(f"Cashflows: {result.cashflows}")
print(f"Net Interest: ₹{result.net_interest_cost:,.0f}")
print(f"Effective Rate: {result.effective_interest_rate * 100:.2f}%")
```

## Extensibility

The module is designed for easy extension:

### Adding New Metrics

```python
class ExtendedResult(ChitFundResult):
    """Extended result with additional metrics."""
    monthly_payment: float
    roi: float
```

### Custom Analyzers

```python
class CustomAnalyzer(ScenarioAnalyzer):
    """Analyzer with custom optimization logic."""
    
    def find_best_roi(self, config, ...):
        # Custom optimization logic
        pass
```

### New Report Formats

```python
class CustomReportGenerator(ReportGenerator):
    """Custom report formats."""
    
    @staticmethod
    def export_to_excel(df, filename):
        df.to_excel(filename, index=False)
```

## Error Handling

The module includes comprehensive error handling:

```python
try:
    config = ChitFundConfig(
        total_installments=-5,  # Invalid
        ...
    )
except ValueError as e:
    print(f"Configuration error: {e}")

try:
    result = calculator.analyze_single_bid(config, 800000)  # Bid > chit value
except ValueError as e:
    print(f"Calculation error: {e}")
```

## Best Practices

1. **Always validate configuration** - Use ChitFundConfig to ensure valid parameters
2. **Reuse instances** - Create calculator/analyzer once, use multiple times
3. **Handle exceptions** - Wrap calculations in try-except blocks
4. **Use enums** - Use ChitFrequency enum instead of magic numbers
5. **Export results** - Save scenario analysis for future reference

## Examples

See `chit_intrest_cal.ipynb` for complete working examples.

## Dependencies

- `numpy_financial`: IRR calculations
- `pandas`: Data manipulation and analysis
- `dataclasses`: Configuration and result containers
- `typing`: Type hints for better IDE support

## Future Extensions

Possible future enhancements:

1. **Visualization**: Add plotting capabilities for scenario comparison
2. **Sensitivity Analysis**: Test impact of parameter variations
3. **Risk Metrics**: Add standard deviation, VaR calculations
4. **Comparison Tools**: Compare multiple chit funds
5. **Time-based Analysis**: Consider actual dates vs. installment numbers
6. **Tax Calculations**: Include tax implications
7. **Multiple Winners**: Handle scenarios with multiple prize winners

## Contributing

When extending this module:
1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Include docstrings with parameter descriptions
4. Add validation for new parameters
5. Write unit tests for new functionality
6. Update this guide with new features
