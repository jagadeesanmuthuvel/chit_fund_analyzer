import pytest
import subprocess
import time
import os
import sys
from playwright.sync_api import Page, expect

# Define the port
PORT = 8501
BASE_URL = f"http://localhost:{PORT}"

@pytest.fixture(scope="session")
def app_server():
    """
    Fixture to start the Streamlit app before tests and stop it after.
    """
    # Check if app is already running on the port
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('localhost', PORT)) == 0:
            print(f"App already running on port {PORT}")
            yield BASE_URL
            return

    print("Starting Streamlit app...")
    # Get the root directory of the project
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Command to run the app
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        os.path.join(root_dir, "streamlit_app", "main.py"),
        "--server.port", str(PORT),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]

    # Start the process
    process = subprocess.Popen(
        cmd,
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONPATH": root_dir}
    )

    # Wait for the app to start
    max_retries = 30
    for i in range(max_retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', PORT)) == 0:
                    print("App started successfully!")
                    break
        except:
            pass
        time.sleep(1)
        if i == max_retries - 1:
            process.terminate()
            raise RuntimeError("Streamlit app failed to start")

    yield BASE_URL

    # Cleanup
    print("Stopping Streamlit app...")
    process.terminate()
    process.wait()

@pytest.fixture(scope="function")
def page(context, app_server):
    """
    Fixture to provide a Playwright page navigated to the app.
    """
    page = context.new_page()
    page.goto(app_server)
    yield page
    page.close()
