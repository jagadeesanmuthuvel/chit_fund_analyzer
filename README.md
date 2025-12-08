---
title: Chit Fund Analyzer
emoji: 🏢
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

# Chit Fund Analyzer

A Python package for analyzing chit fund investments with robust validation, type safety, and comprehensive analysis capabilities.

## Features

- 🔒 **Type Safety**: Uses Pydantic for robust data validation and type checking
- 🏗️ **Clean Architecture**: Well-structured code with separated concerns
- 🔧 **Extensible Design**: Easy to add new analysis methods and validation rules
- ⚠️ **Error Handling**: Comprehensive error handling with custom exceptions
- 🐍 **Modern Python**: Uses modern Python features and best practices
- 📊 **Comprehensive Analysis**: IRR calculations, scenario analysis, and comparisons

## Installation

### Local Installation

This package requires Python 3.13+ and uses `pyproject.toml` for dependency management:

```bash
# Install with pip
pip install -e .

# Or using uv (recommended)
uv pip install -e .

# With optional dependencies
pip install -e ".[dev,test]"
```

See [docs/INSTALL.md](docs/INSTALL.md) for detailed installation instructions.

### Container Deployment (Docker/Podman)

The application supports both **Docker** and **Podman**.

**Using Makefile (Linux/Mac)**:
```bash
make runtime          # Show detected runtime
make up               # Start container
make down             # Stop container
make logs             # View logs
```

**Direct Commands (All platforms)**:
```bash
# Docker
docker-compose -f docker/docker-compose.yml up -d
docker-compose -f docker/docker-compose.yml down

# Podman
podman compose -f docker/docker-compose.yml up -d
podman compose -f docker/docker-compose.yml down
```

Access at: **http://localhost:8501**

**Documentation**:
- **[docs/PODMAN.md](docs/PODMAN.md)** - Podman-specific guide
- **[docs/DOCKER_QUICKSTART.md](docs/DOCKER_QUICKSTART.md)** - Quick start
- **[docs/DOCKER.md](docs/DOCKER.md)** - Full deployment guide

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

## Example: Find Best Scenario

```python
# Generate multiple bid amounts and analyze the range
from chit_fund_analyzer.utils import generate_bid_range

bid_amounts = generate_bid_range(min_bid=80000, max_bid=150000, num_scenarios=10)
scenarios = scenario_analyzer.analyze_bid_scenarios(bid_amounts)

# Find best and worst scenarios manually
best_scenario = max(scenarios, key=lambda s: s.annual_irr)
worst_scenario = min(scenarios, key=lambda s: s.annual_irr)

print(f"Best case - Bid: ₹{best_scenario.bid_amount:,.0f}, IRR: {best_scenario.annual_irr:.2%}")
print(f"Worst case - Bid: ₹{worst_scenario.bid_amount:,.0f}, IRR: {worst_scenario.annual_irr:.2%}")
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

## Web Application

### Streamlit Web Interface 🌐

A comprehensive web application with interactive analysis and visualizations:

```bash
# Run the web app
python run_app.py

# Or directly with streamlit
streamlit run streamlit_app.py
```

**Features:**
- 🔧 **Interactive Configuration**: Web form for all parameters
- 📊 **Real-time Analysis**: Instant IRR calculations and results
- 📈 **Rich Visualizations**: Interactive charts and graphs
- 🔍 **Scenario Analysis**: Compare multiple bid amounts
- 💡 **Smart Insights**: Automated recommendations
- 📄 **Export**: Download results in multiple formats

Access at: http://localhost:8501

### Demo Notebook

For comprehensive examples and programmatic usage, see:
- `chit_fund_analyzer_demo.ipynb` - Complete walkthrough with examples
- `STREAMLIT_README.md` - Detailed web app documentation

### New Streamlit UI (advanced workflow)

The `streamlit_app/` package hosts a multi-stage Streamlit experience that persists data to Google Sheets:

```bash
uv run streamlit run streamlit_app/main.py
```

It requires a valid `oauth_credentials.json` (installed app client). Tokens are cached in encrypted cookies to avoid repeated prompts.

#### End-to-End Playwright Tests

Pre-baked refresh tokens allow fully automated tests without interacting with the OAuth popup:

```bash
# install optional dependencies
uv pip install '.[e2e]'

# set env variables (see docs/streamlit_app_plan.md §11)
export CHIT_APP_AUTH_MODE=refresh_token
uv run playwright test
```

Refer to `docs/streamlit_app_plan.md` for the detailed SOP covering credential capture and CI integration.

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

## Deployment

### Docker Deployment

The application is fully containerized and production-ready:

**Quick Start**:
```bash
# Production
docker-compose up -d

# Development with hot reload
docker-compose --profile dev up -d
```

**Features**:
- Simple, optimized Dockerfile
- Production-ready configuration
- Health checks and monitoring
- Resource limits and security hardening
- CI/CD with GitHub Actions

See comprehensive deployment guides:
- [docs/DOCKER_QUICKSTART.md](docs/DOCKER_QUICKSTART.md) - Quick start guide
- [docs/DOCKER.md](docs/DOCKER.md) - Complete deployment documentation

### Local Deployment

```bash
# Install dependencies
pip install -e ".[production]"

# Run with Streamlit
streamlit run streamlit_app/main.py

# Or use the helper script
python scripts/run_app.py
```

## Requirements

- Python 3.13+
- See [pyproject.toml](pyproject.toml) for complete dependency list

### Core Dependencies
- pydantic 2.x - Data validation
- numpy-financial - IRR calculations
- pandas - Data processing
- streamlit - Web interface
- plotly - Visualizations

### Optional Dependencies
- `[test]` - pytest, playwright for testing
- `[dev]` - jupyter, matplotlib for development
- `[production]` - gunicorn, uvicorn for production servers

## Documentation

- [README.md](README.md) - This file
- [docs/INSTALL.md](docs/INSTALL.md) - Installation guide
- [docs/DOCKER.md](docs/DOCKER.md) - Docker deployment guide
- [docs/DOCKER_QUICKSTART.md](docs/DOCKER_QUICKSTART.md) - Docker quick start
- [documentation/](documentation/) - Additional documentation

## License

This project is open source and available under the MIT License.
