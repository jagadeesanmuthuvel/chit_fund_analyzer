#!/usr/bin/env python
"""
Run script for Chit Fund Manager Streamlit app.

Usage:
    python scripts/run_app.py [port]
    
    Or from virtual environment:
    D:/side_projects/chit_fund_analyzer/.venv/Scripts/python.exe scripts/run_app.py [port]
    
Examples:
    python scripts/run_app.py          # Auto-find available port
    python scripts/run_app.py 8502     # Use specific port
"""

import subprocess
import sys
import socket
import argparse


def is_port_available(port):
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False


def find_available_port(start_port=8501, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return None


def main():
    """Rtreamlit application."""
    parser = argparse.ArgumentParser(description='Run Chit Fund Manager')
    parser.add_argument('port', type=int, nargs='?', help='Port number (default: auto-find)')
    args = parser.parse_args()
    
    # Determine port
    if args.port:
        port = args.port
        if not is_port_available(port):
            print(f"⚠️  Port {port} is already in use. Finding an available port...")
            port = find_available_port(port + 1)
            if port is None:
                print("❌ Could not find an available port. Please close other Streamlit instances.")
                sys.exit(1)
    else:
        port = find_available_port()
        if port is None:
            print("❌ Could not find an available port (tried 8501-8510).")
            print("💡 Try stopping other Streamlit instances or specify a different port:")
            print("   python scripts/run_app.py 8520")
            sys.exit(1)
    
    print(f"🚀 Starting Chit Fund Manager on port {port}...")
    print(f"📱 Access at: http://localhost:{port}")
    print()
    
    try:
        # Use the same Python executable that's running this script
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "streamlit_app/main.py",
            "--server.port", str(port),
            "--server.headless", "true"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Chit Fund Manager...")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running Streamlit app: {e}")
        print(f"💡 Try a different port: python scripts/run_app.py {port + 1}")
        sys.exit(1)


if __name__ == "__main__":
    main()
