GitHub Copilot Instructions: Chit Fund Manager App

1. Project Context & Role

Role: Expert Python Streamlit Developer with a focus on Financial Applications and Data Integrity.
Goal: Build a robust, multi-stage Streamlit application for managing Chit Funds.
Phasing Strategy:

Version 1 (Current Scope): Use a Local Excel File as the database for rapid development and testing.

Version 2 (Future Scope): Migrate the backend to Google Sheets.

Constraint: The code structure (especially the Data Access Layer interfaces) must be designed so that switching from Excel to Google Sheets later requires minimal refactoring.

2. Technical Stack

Frontend: Streamlit, Streamlit AgGrid (for editable tables), Plotly (for charts).

Core Logic: chit_fund_analyzer (Local package - assume it is already installed/available in path).

Database (V1): Local Excel File (.xlsx) using pandas and openpyxl.

State Management: st.session_state.

Styling: Custom CSS for a professional financial dashboard look.

Testing: Playwright for Python (End-to-End Testing).

3. Directory Structure

Ensure the code is generated following this modular structure:

project_root/
├── chit_fund_analyzer/    # (Existing Package - DO NOT MODIFY)
│   ├── __init__.py
│   ├── models.py
│   ├── analyzer.py
│   ├── ...
├── streamlit_app/         # (Target Directory for App)
│   ├── __init__.py
│   ├── main.py            # Entry point
│   ├── auth.py            # Simple Local Auth (Mock for V1)
│   ├── db.py              # Excel DAL (Implements same interface as future GSheets)
│   ├── utils.py           # UI helpers
│   └── stages/
│       ├── __init__.py
│       ├── login.py       # Stage 0
│       ├── dashboard.py   # Stage 1 (Selection/Creation/Edit)
│       ├── installments.py# Stage 2 (Tracking)
│       └── analytics.py   # Stage 3 (Scenarios)
├── data/
│   └── chit_fund_db.xlsx  # Local Database File
├── tests/
│   └── e2e/               # Playwright Tests
│       ├── conftest.py
│       └── test_user_flow.py
├── .streamlit/
│   └── secrets.toml       # API Credentials (Empty for V1)
└── requirements.txt



4. Implementation Details by Module

A. Data Access Layer (streamlit_app/db.py)

Goal: abstract the file I/O so the UI doesn't know it's using Excel.

Class ChitFundDB:

Initialization: Accepts a file path (default: data/chit_fund_db.xlsx).

Schema Enforcement: On init, check if the file exists. If not, create it with two sheets: chits and installments and the correct headers.

Schema & Consistency (Preparing for V2):

Even though it is a local file, maintain the version column in the chits sheet.

Logic:

Read: Load the Excel file into Pandas DataFrames.

Write:

Load the file.

Perform the update (add row / edit cell).

Increment the version column for the modified Chit.

Save the file back to disk.

Note: Strict optimistic locking isn't needed for a single-user local file, but the version column must exist to support the data model.

Methods (Interface):

get_all_chits(): Returns list of dicts.

create_chit(metadata: dict): atomic append to chits sheet + bulk append to installments sheet.

update_chit_metadata(chit_id, metadata: dict): Update name, description, etc.

get_installments(chit_id): Return installments for specific ID.

update_installments(chit_id, updates: List[dict]): Update rows in installments sheet and save.

B. Authentication (streamlit_app/auth.py)

Context: OAuth is removed for V1.

Implementation: Implement a simple "Mock Auth" to preserve the application flow (Stage 0 -> Stage 1).

Logic:

Simple "Login" button.

Sets st.session_state['authenticated'] = True.

Sets st.session_state['user'] = 'local_admin'.

C. Stage Management (streamlit_app/main.py)

Use a robust state machine pattern.

st.session_state['current_stage'] determines which module from stages/ is rendered.

Navigation Sidebar: Only show stages accessible based on current context.

D. Stages

Stage 1: Dashboard (stages/dashboard.py)

Tab 1: Select / Edit Existing Chit:

Dropdown to select a Chit.

Edit Mode: Provide an "Edit Details" button that opens a form to update the Chit's Name, Description, or other metadata (excluding immutable fields like ID). Save changes via db.update_chit_metadata.

Selection loads data into st.session_state['selected_chit'] and advances stage.

Tab 2: Create New Chit:

Inputs: Restrict inputs to only the essentials required for ChitFundConfig:

Chit Name

Total Installments (int)

Full Chit Value (decimal)

Chit Frequency (per year)

First Installment Date

Note: Do not ask for previous_installments here. A new chit implies 0 previous installments.

Action: "Initialize Chit" button -> calls db.create_chit.

Stage 2: Installment Tracking (stages/installments.py)

Gatekeeper: If start_date > today, show a warning and offer to skip to Analysis.

Data Editor: Use st.data_editor (or AgGrid) for the installments table.

Business Logic & Reactive Formulas:

Field: Amount Paid (by a single non-winner candidate).

Reactive Trigger: When the user updates the Amount Paid, the system must immediately recalculate dependent fields.

Formula:
$$ \text{Amount Paid} = \frac{\text{Total Value} - \text{Discount}}{\text{Total Installments} - \text{Current Installment Number}} $$

Implementation: Ensure this formula is applied to auto-calculate/validate the Amount Paid field.

Analyzer Integration:

On every data change, reconstruct the ChitFundConfig object.

Call chit_fund_analyzer.analyzer.ChitFundAnalyzer.analyze() to get the latest Prize Amount and IRR.

Display these metrics in the UI (KPI Cards) immediately.

Validation:

Enforce: Amount Paid cannot be < 60% of winner installment (use ChitFundConfig validation logic).

Save: Commit changes to DB using db.update_installments.

Stage 3: Analysis (stages/analytics.py)

Use chit_fund_analyzer.scenario.ScenarioAnalyzer.

Inputs: Sliders for Bid Range, Number of Scenarios.

Outputs:

Line Chart: Bid Amount vs Annual IRR.

Table: Detailed Cashflow breakdown.

Export: "Download Report" button (Excel).

5. Coding Standards & Best Practices

Type Hinting: Use typing.List, typing.Dict, typing.Optional everywhere.

Error Handling: Wrap file I/O operations in try/except.

Docstrings: Google-style docstrings for all functions.

Configuration: Use pydantic models for UI form validation before sending data to the DB.

Performance: Cache DB reads using @st.cache_data. Clear cache on successful writes.

6. Testing Strategy (Mandatory)

Tool: Playwright (pytest-playwright).
Goal: Verify the complete user journey (E2E) without manual intervention.

Test Spec (tests/e2e/test_user_flow.py):

Setup:

Generate a fresh temporary Excel DB file.

Launch Streamlit app in headless mode.

Scenario:

Login: Click "Mock Login" button.

Stage 1 (Create): Fill "New Chit" form -> Submit. Verify success message.

Stage 1 (Select): Select the newly created Chit from dropdown.

Stage 2 (Update):

Navigate to Installment #1.

Edit "Amount Paid" .

Verify Reactive Update: Check if "Prize Amount"," "Discount", "Annual IRR Winner" KPI card updates dynamically.

Click "Save". Verify persistence in Excel.

Stage 3 (Analyze):

Click "Go to Analysis".

Move "Bid Range" slider.

Check if Chart element (st.plotly_chart) is present.

Note: Ensure requirements.txt includes pytest, pytest-playwright, and openpyxl.

7. Reference: chit_fund_analyzer Interface

Assume these classes exist and import them as needed:

from chit_fund_analyzer.models import ChitFundConfig, ChitFundAnalysisResult
from chit_fund_analyzer.analyzer import ChitFundAnalyzer
from chit_fund_analyzer.scenario import ScenarioAnalyzer

# Example Usage
config = ChitFundConfig(...)
analyzer = ChitFundAnalyzer(config)
result = analyzer.analyze() # returns ChitFundAnalysisResult
