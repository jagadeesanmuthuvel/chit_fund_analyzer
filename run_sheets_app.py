#!/usr/bin/env python3
"""
Quick start script for Chit Fund Analyzer with Google Sheets integration
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    """Main entry point for the application"""
    
    # Get the directory where this script is located
    app_dir = Path(__file__).parent.resolve()
    
    # Change to the app directory
    os.chdir(app_dir)
    
    print("🚀 Starting Chit Fund Analyzer with Google Sheets Integration...")
    print(f"📁 Working directory: {app_dir}")
    print("🌐 Open your browser and go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app_with_sheets.py", 
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
    
    except KeyboardInterrupt:
        print("\n👋 Shutting down Chit Fund Analyzer...")
    
    except FileNotFoundError:
        print("❌ Error: Streamlit not found. Please install requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()