# Utility Scripts

This directory contains utility scripts for development and deployment:

## Scripts

### `run_app.py`
Simple script to run the Streamlit application.

Usage:
```bash
python scripts/run_app.py
```

### `COMMANDS.ps1`
PowerShell commands for common development tasks.

### `show_test_results.ps1`
PowerShell script to display test results.

Usage:
```powershell
.\scripts\show_test_results.ps1
```

## Running the Application

### Recommended Method
Use uv to run the application:
```bash
uv run python -m streamlit run streamlit_app/main.py
```

### Alternative Methods
1. Using the run script:
   ```bash
   python scripts/run_app.py
   ```

2. Direct streamlit command:
   ```bash
   streamlit run streamlit_app/main.py
   ```

## Testing

Run the test suite:
```bash
uv run python -m pytest tests/
```

Run specific test:
```bash
uv run python -m pytest tests/e2e/test_user_flow.py -v
```
