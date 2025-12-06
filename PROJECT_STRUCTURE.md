# Chit Fund Analyzer - Project Structure

This document describes the organized project structure.

## Directory Layout

```
chit_fund_analyzer/
├── chit_fund_analyzer/          # Core analysis library
│   ├── analyzer.py              # Main analysis engine
│   ├── models.py                # Data models
│   ├── scenario.py              # Scenario analysis
│   ├── utils.py                 # Utility functions
│   └── exceptions.py            # Custom exceptions
│
├── streamlit_app/               # Streamlit web application
│   ├── main.py                  # Application entry point
│   ├── auth.py                  # Authentication module
│   ├── db.py                    # Database access layer
│   ├── utils.py                 # UI utility functions
│   └── stages/                  # Application stages
│       ├── login.py             # Login stage
│       ├── dashboard.py         # Dashboard (chit selection/creation)
│       ├── installments.py      # Installment tracking
│       └── analytics.py         # Scenario analysis
│
├── tests/                       # Test suite
│   └── e2e/                     # End-to-end tests
│       ├── conftest.py          # Test configuration
│       └── test_user_flow.py    # User flow tests
│
├── data/                        # Database files
│   └── chit_fund_db.xlsx        # Excel database
│
├── documentation/               # Project documentation
│   ├── DEPLOYMENT_COMPLETE.md
│   ├── E2E_TEST_REPORT.md
│   ├── TESTING_GUIDE.md
│   └── MANUAL_UI_TESTING_REPORT.md
│
├── scripts/                     # Utility scripts
│   ├── run_app.py              # Application launcher
│   ├── COMMANDS.ps1            # PowerShell commands
│   └── show_test_results.ps1   # Test results viewer
│
├── test_scripts/                # Development test scripts
│   └── test_*.py               # Various test utilities
│
├── test_artifacts/              # Test outputs
│   └── *.png, *.json           # Screenshots and reports
│
├── notebooks/                   # Jupyter notebooks
│   └── *.ipynb                 # Analysis demonstrations
│
├── docs/                        # API documentation
├── .github/                     # GitHub configuration
│   └── instructions/           # Copilot instructions
├── .streamlit/                  # Streamlit configuration
│
├── README.md                    # Main project README
├── pyproject.toml              # Project configuration
├── requirements.txt            # Python dependencies
└── uv.lock                     # UV lock file
```

## Key Components

### Core Library (`chit_fund_analyzer/`)
Contains the business logic for chit fund calculations and analysis.

### Web Application (`streamlit_app/`)
Streamlit-based UI for managing chit funds with stages:
1. Login (mock authentication)
2. Dashboard (create/select chits)
3. Installments (track payments, reactive calculations)
4. Analytics (scenario analysis)

### Testing
- `tests/` - Production tests using pytest and Playwright
- `test_scripts/` - Development/debugging test scripts
- `test_artifacts/` - Test outputs and screenshots

### Documentation
- `README.md` - Main project documentation
- `documentation/` - Detailed reports and guides
- `docs/` - API and technical documentation

### Scripts
Utility scripts for running the app and development tasks.

## Running the Application

```bash
# Using UV (recommended)
uv run python -m streamlit run streamlit_app/main.py

# Alternative
python scripts/run_app.py
```

## Running Tests

```bash
# All tests
uv run python -m pytest tests/ -v

# Specific test
uv run python -m pytest tests/e2e/test_user_flow.py::test_create_new_chit -v
```

## Development Workflow

1. Make changes to code
2. Run tests: `uv run python -m pytest tests/`
3. Test UI manually or use test scripts
4. Check documentation in `documentation/` for guidelines
5. Update README.md as needed
