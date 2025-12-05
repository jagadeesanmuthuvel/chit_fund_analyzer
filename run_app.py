#!/usr/bin/env python3
"""
Launch script for the Chit Fund Analyzer Streamlit app.

This script automatically launches the Streamlit app with the correct
Python environment and opens it in your default web browser.
"""

import subprocess
import sys
import webbrowser
import time
import os
from pathlib import Path


def find_streamlit_executable():
    """Find the streamlit executable in the virtual environment."""
    venv_path = Path(__file__).parent / ".venv"
    
    if sys.platform == "win32":
        streamlit_path = venv_path / "Scripts" / "streamlit.exe"
    else:
        streamlit_path = venv_path / "bin" / "streamlit"
    
    if streamlit_path.exists():
        return str(streamlit_path)
    
    # Fallback to global streamlit
    return "streamlit"


def main():
    """Launch the Streamlit app."""
    print("🚀 Starting Chit Fund Analyzer...")
    print("=" * 50)
    
    # Find streamlit executable
    streamlit_cmd = find_streamlit_executable()
    app_file = Path(__file__).parent / "streamlit_app.py"
    
    if not app_file.exists():
        print("❌ Error: streamlit_app.py not found!")
        sys.exit(1)
    
    # Prepare command
    cmd = [
        streamlit_cmd,
        "run",
        str(app_file),
        "--server.port", "8501",
        "--server.headless", "false"
    ]
    
    print("📱 App will be available at: http://localhost:8501")
    print("🔄 Starting server...")
    print()
    print("Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Start streamlit
        process = subprocess.Popen(cmd, cwd=Path(__file__).parent)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open("http://localhost:8501")
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping application...")
        if 'process' in locals():
            process.terminate()
    except FileNotFoundError:
        print(f"❌ Error: Streamlit not found at {streamlit_cmd}")
        print("Please ensure Streamlit is installed in your environment:")
        print("  pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()