# Streamlit Chit Fund App – Plan, Design & Implementation

## 1. Goals & Scope
- Build a responsive Streamlit app that wraps the `chit_fund_analyzer` package for real-world bidding workflows.
- Persist all chit metadata and installment data inside Google Sheets (`chit_fund_db`) using OAuth2.
- Guarantee ACID-like discipline (atomic sheet updates, consistent schemas, idempotent writes).
- Provide a 3-stage UX: entry/selection → installment updates → analytics & downloads.

## 2. High-Level Architecture
| Layer | Responsibility | Key Tech |
| --- | --- | --- |
| UI (Streamlit) | Multi-step wizard, charts, downloads | `streamlit`, `plotly`, `streamlit-authenticator` |
| Domain | Validation + analytics | `chit_fund_analyzer` models/analyzer/scenario |
| Data Access | Google Sheets CRUD with transactional semantics | `gspread`, `google-auth-oauthlib` |
| Storage | Single spreadsheet `chit_fund_db` with normalized tabs | Google Sheets workbook |

## 3. Authentication & Session Strategy
1. **OAuth Bootstrap Page**
   - Load credentials from `oauth_credentials.json`.
  - Use `google-auth-oauthlib.flow.Flow` to request scopes (`https://www.googleapis.com/auth/spreadsheets`, `drive.file`).
  - Exchange code → tokens; store tokens in `st.session_state["gsheets_creds"]` and serialize into browser cookies/local storage using `streamlit-cookies-manager` (or similar) to avoid repeated OAuth prompts.
2. **Token Persistence**
  - On load: check session state; else inspect cookie/local-storage payload; refresh if expired using refresh token.
   - Only show application stages when a valid credential object exists.

## 4. Google Sheets Data Model (ACID-Friendly)
- Workbook: `chit_fund_db` (create via Drive API if missing).
- Tabs:
  1. `chits` (one row per chit): `chit_id`, `name`, `description`, `method`, `full_chit_value`, `total_installments`, `frequency_per_year`, `first_installment_date`, `created_at`, `updated_at`.
  2. `installments`: `chit_id`, `installment_no`, `scheduled_date`, `amount_due`, `amount_paid`, `status`, `prize_amount`, `bid_winner_name`, `discount`, `annual_irr_winner`, `updated_at`.
  3. `analysis_cache` (optional) to store latest analysis snapshots for Excel export.
- **ACID approach**:
  - Wrap multi-row writes in `batch_update` calls to guarantee atomicity.
  - Include `version` column per chit; optimistic concurrency check before write.
  - Use Drive file-level permissions for durability; treat Google Sheets revision history as audit.
  - use proper primary keys (`chit_id`, `installment_no`) to avoid duplicates and validate integrity on every insert/update.
  - `prize_amount`, `discount`, and `annual_irr_winner` are stored per installment and recomputed whenever `amount_paid` changes so the sheet remains the source of truth.

## 5. Streamlit Stage Design
### Stage 0 – Auth Gate
- Component that displays OAuth prompt if credentials missing.
- Once authenticated, load workbook metadata (create if absent).

### Stage 1 – Entry / Selection
- Tabs: **New Chit** and **Existing Chit**.
- **New Chit Form**
  - Inputs: name, description (textarea), chit type (Method 1 default), total bid amount (`full_chit_value`), total installments, frequency per year, first installment date.
  - Validate via Pydantic `ChitFundConfig` derivative `ChitFundMetadataModel` (new class) to ensure cross-field logic.
  - On submit: write to `chits` tab, generate installment schedule rows (status `PENDING`).
- **Existing Chit Dropdown**
  - Fetch `name` + `chit_id` list from sheet.
  - Selecting chit loads metadata + installment history into session state for later stages.
  - If there are changes in the inputs, update the session state config accordingly and persist the updates to the Google Sheets DB file.

> **Gate:** Stage 2 only unlocks when the selected chit’s first installment date is ≤ today. Otherwise, display a notice directing users straight to Stage 3 so they can use the scenario planner before any payments exist.

### Stage 2 – Installment Update Table
- Display editable table (Streamlit Ag-Grid or `st.data_editor`) showing `installment_no`, `scheduled_date`, `amount_paid`, `status`, `prize_amount`, `bid_winner_name`, `discount`, `annual_irr_winner`; populate rows with existing Google Sheets data when available.
- `installment_no` is read-only; `scheduled_date` auto-derives from start date and frequency but can be adjusted slightly (with validation) for scheduling realities.
- `prize_amount`, `discount`, and `annual_irr_winner` are calculated via the analyzer each time the user edits `amount_paid` or related values so the sheet stays consistent; these columns are read-only projections in the UI.
- User edits `amount_paid`, `bid_winner_name`, and `status` (status auto flips to `paid` when `amount_paid` > 0, else `pending`).
- Enforce rule: entered `amount_paid` cannot be < 60% of winner installment (derived from analyzer config).
- On save: validate via Pydantic model `InstallmentUpdateModel`, then upsert rows in `installments` tab with batch update; refresh session state and sheet snapshot.

### Stage 3 – Analysis & Reports
- Inputs: bid amount, current installment number, optional winner installment override, scenario min/max bids + steps.
- Use `ChitFundConfig` built from sheet data + user overrides.
- Run `ChitFundAnalyzer.analyze()` for base case and `ScenarioAnalyzer.analyze_bid_scenarios()` for range.
- Visuals: line chart of IRR vs bid, table of cashflows, KPI cards (prize amount, annual IRR, period IRR).
- Downloads: `pandas.ExcelWriter` with formatting (via `openpyxl`) containing config, installments, scenarios.

## 6. Modularity & File Layout
```
streamlit_app/
├── __init__.py
├── main.py                # Streamlit entry
├── auth.py                # OAuth, token persistence helpers
├── data_access.py         # Google Sheets CRUD & ACID helpers
├── models.py              # Streamlit-specific Pydantic models
├── stages/
│   ├── stage0_auth.py
│   ├── stage1_entry.py
│   ├── stage2_installments.py
│   └── stage3_analysis.py
├── components.py          # Shared UI widgets (KPI cards, charts)
├── exporters.py           # Excel export + cache
└── state.py               # Session state utilities
```

## 7. Implementation Steps
1. **Set up package**: add `streamlit_app` module, update `pyproject.toml` optional dependencies if needed.
2. **Auth Layer**: implement OAuth helper that returns authorized `gspread.Client`; include credential caching.
3. **Workbook Bootstrap**: utility to find/create `chit_fund_db`, initialize tabs with headers if absent.
4. **Data Models**: create Pydantic schemas for chit metadata, installment rows, update payloads.
5. **Stage 1 UI**: build new chit form + selection flow; integrate with data layer writes and `ChitFundConfig` creation.
6. **Stage 2 UI**: implement editable table, validation, and persistence.
7. **Stage 3 UI**: wire analytics to `chit_fund_analyzer`, add charts, scenario sliders, Excel export.
8. **Token storage**: integrate cookie/local-storage persistence; add logout/reset option.
9. **Testing**:
   - Unit tests for data access helpers (mock `gspread`).
   - Streamlit component smoke tests via `pytest` + `streamlit.testing`.
   - Manual end-to-end test with demo spreadsheet.

## 8. Error Handling & UX
- Surface validation errors inline with Streamlit `st.error`.
- Wrap Google API errors in custom `SheetsDataError` with actionable messages.
- Provide retry buttons for transient network failures.
- Log key events (auth success, sheet creation, batch updates) for debugging.

## 9. Responsiveness & Styling
- Use Streamlit columns to keep forms mobile-friendly.
- Define consistent theme via `.streamlit/config.toml` (to be added) with font + color choices.
- Keep charts responsive with `use_container_width=True`.

## 10. Future Work Hooks
- Placeholder for "Method 2" calculation path.
- Optional caching layer (Redis/Streamlit Cache) for heavy scenario runs.
- Multi-user permissions by mapping Google account email to chit ownership.

## 11. End-to-End Testing SOP (Playwright + Pre-Baked OAuth Credentials)
### Goal
Automate the full Streamlit workflow (auth → Stage 1 → Stage 2 gate → Stage 3 analysis) in CI without manual Google login by reusing a stored refresh token.

### Prerequisites
- Dedicated Google Cloud project for testing with Sheets + Drive APIs enabled.
- OAuth client (desktop or web) with `https://www.googleapis.com/auth/spreadsheets` and `https://www.googleapis.com/auth/drive.file` scopes.
- A test Google account that owns the `chit_fund_db_e2e` spreadsheet (separate from production data).
- Playwright test runner configured in the repo (add under `tests/e2e`).

### One-Time Token Capture
1. Run the installed-app flow locally to obtain a refresh token:
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow

   flow = InstalledAppFlow.from_client_secrets_file(
       "oauth_credentials.json",
       scopes=[
           "https://www.googleapis.com/auth/spreadsheets",
           "https://www.googleapis.com/auth/drive.file",
       ],
   )
   creds = flow.run_local_server(port=0, prompt="consent")
   print("REFRESH_TOKEN=", creds.refresh_token)
   ```
2. Copy the printed `REFRESH_TOKEN` and store it securely (e.g., `.env.e2e`, CI secret, or GitHub Actions secret).

### App Test Mode Hook
- Add an environment flag (e.g., `CHIT_APP_AUTH_MODE=refresh_token`) so the Streamlit app bypasses the OAuth UI when present.
- In this mode, build credentials directly:
  ```python
  from google.oauth2.credentials import Credentials
  from google.auth.transport.requests import Request

  creds = Credentials(
      token=None,
      refresh_token=os.environ["GSHEETS_REFRESH_TOKEN"],
      client_id=os.environ["GSHEETS_CLIENT_ID"],
      client_secret=os.environ["GSHEETS_CLIENT_SECRET"],
      token_uri="https://oauth2.googleapis.com/token",
      scopes=[...],
  )
  creds.refresh(Request())
  gspread_client = gspread.authorize(creds)
  ```
- Ensure this path is only enabled for tests to keep production users on the regular OAuth flow.

### Environment Variables for Tests
```
CHIT_APP_AUTH_MODE=refresh_token
GSHEETS_CLIENT_ID=<oauth client id>
GSHEETS_CLIENT_SECRET=<oauth client secret>
GSHEETS_REFRESH_TOKEN=<pre-baked refresh token>
GSHEETS_TEST_SPREADSHEET=chit_fund_db_e2e
```
Store these in CI secrets or a `.env.e2e` excluded from version control.

### Playwright Test Flow
1. `uv run streamlit run streamlit_app/main.py --server.headless true` (or similar) with the env vars above.
2. In Playwright, wait for Stage 0 to detect that the app is already authenticated (no OAuth popup expected).
3. Script actions:
   - Stage 1: create a test chit, verify it appears in the dropdown.
   - Stage 2: if first installment date ≤ today, edit an installment and assert Google Sheet data updates (mock gspread or poll via API).
   - Stage 3: input bid/scenario ranges, confirm charts render and download link exists; optionally download and validate Excel.
4. Clean up by deleting the test chit rows (either via API call or teardown fixture) to keep the sheet deterministic.

### CI Integration
- Add a Playwright job that:
  1. Exports the secret env vars.
  2. Starts the Streamlit server in the background.
  3. Runs `playwright test` with retries for flaky network steps.
  4. Uploads screenshots/video artifacts on failure for debugging.

### Notes
- Never commit the refresh token; rotate it if there is any suspicion of leakage.
- Keep the test spreadsheet isolated so automated runs do not affect production finance data.
- For local debugging, supply the same env vars and run `playwright codegen http://localhost:8501` to capture selectors.
