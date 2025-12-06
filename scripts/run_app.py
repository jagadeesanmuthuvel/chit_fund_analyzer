#!/usr/bin/env python
"""
Run script for Chit Fund Manager Streamlit app.

Usage:
    uv run python run_app.py
"""

import subprocess
import sys


def main():
    """Run the Streamlit application."""
    try:
        subprocess.run([
            "python", "-m", "streamlit", "run",
            "streamlit_app/main.py",
            "--server.port", "8501"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\nShutting down Chit Fund Manager...")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
