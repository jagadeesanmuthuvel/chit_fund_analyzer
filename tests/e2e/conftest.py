"""
Pytest configuration for E2E tests.
"""

import pytest
import subprocess
import time
import tempfile
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def test_db_path():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_chit_fund_db.xlsx"
    
    yield str(db_path)
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def streamlit_app(test_db_path):
    """Start Streamlit app for testing."""
    
    # Start Streamlit in background
    app_path = Path(__file__).parent.parent.parent / "streamlit_app" / "main.py"
    
    process = subprocess.Popen(
        [
            "python", "-m", "streamlit", "run", str(app_path),
            "--server.port", "8502",
            "--server.headless", "true"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    time.sleep(8)
    
    yield "http://localhost:8502"
    
    # Cleanup
    process.terminate()
    process.wait()


@pytest.fixture(scope="function")
def browser_context():
    """Create a browser context for each test."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        yield context
        
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(browser_context, streamlit_app):
    """Create a new page for each test."""
    page = browser_context.new_page()
    page.goto(streamlit_app)
    
    # Wait for page to load
    page.wait_for_load_state("networkidle")
    
    yield page
    
    page.close()
