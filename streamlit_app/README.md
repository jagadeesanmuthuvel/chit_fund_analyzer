# Chit Fund Manager - Streamlit App

Quick reference guide for running the application.

## Running the App

### Using uv (recommended):
```powershell
uv run python -m streamlit run streamlit_app/main.py --server.port 8501
```

Or use the helper script:
```powershell
uv run python run_app.py
```

### Direct Python:
```powershell
python -m streamlit run streamlit_app/main.py
```

## Running Tests

### E2E Tests with Playwright:

First, install Playwright browsers:
```powershell
uv run playwright install chromium
```

Then run tests:
```powershell
uv run pytest tests/e2e/ -v
```

## Project Structure

```
streamlit_app/
├── __init__.py          # Package initialization
├── main.py              # Application entry point
├── auth.py              # Authentication (mock for V1)
├── db.py                # Excel database layer
├── utils.py             # UI utilities and helpers
└── stages/
    ├── __init__.py
    ├── login.py         # Stage 0: Login
    ├── dashboard.py     # Stage 1: Dashboard
    ├── installments.py  # Stage 2: Installment tracking
    └── analytics.py     # Stage 3: Scenario analysis
```

## Features

- ✅ Create and manage chit funds
- ✅ Track installments with reactive calculations
- ✅ Scenario analysis with visualizations
- ✅ Excel-based local storage
- ✅ Professional financial dashboard UI
- ✅ Real-time IRR calculations

## Database Location

The Excel database is created at:
```
data/chit_fund_db.xlsx
```

## Next Steps (V2)

- Migrate to Google Sheets backend
- Implement OAuth authentication
- Add multi-user support
