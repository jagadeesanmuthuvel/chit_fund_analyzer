# Installation Guide

Dependencies are managed through `pyproject.toml` following modern Python packaging standards.

## Basic Installation

Install the package with core dependencies:

```bash
pip install -e .
```

or with uv:

```bash
uv pip install -e .
```

## Installation with Optional Dependencies

### Testing
Install with test dependencies (pytest, playwright):

```bash
pip install -e ".[test]"
```

### Development
Install with development tools (jupyter, matplotlib):

```bash
pip install -e ".[dev]"
```

### Production
Install with production servers (gunicorn, uvicorn):

```bash
pip install -e ".[production]"
```

### Combined
Install multiple dependency groups:

```bash
pip install -e ".[test,dev]"
```

## Core Dependencies

The following are installed by default:

- **Data Processing**: pandas, numpy, scipy
- **Financial Calculations**: numpy-financial
- **Web Framework**: streamlit, plotly
- **Data Validation**: pydantic
- **Google Sheets**: google-auth, gspread
- **Authentication**: streamlit-authenticator
- **Export**: openpyxl
- **Utilities**: click, toml

## Running the Application

After installation:

```bash
# Using the console script
chit-app

# Or directly with streamlit
streamlit run streamlit_app/main.py
```

## Running Tests

```bash
pytest tests/
```

## Notes

- `requirements.txt` is deprecated and kept only for reference
- All dependency management is now in `pyproject.toml`
- The package is installed in editable mode (`-e`) for development
