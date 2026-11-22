"""MindBridge AI: Secure Multimodal AI Platform Launcher.

Usage:
    python app.py backend    # Starts the FastAPI REST API server (port 8000)
    python app.py frontend   # Starts the Streamlit Web Interface (port 8501)
    python app.py test       # Runs the automated pytest test suite
"""

import sys
import subprocess


def start_backend():
    print("🚀 Starting MindBridge AI FastAPI Backend on http://127.0.0.1:8000...")
    subprocess.run([sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])


def start_frontend():
    print("🌟 Starting MindBridge AI Streamlit Frontend on http://127.0.0.1:8501...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.headless", "true"])


def run_tests():
    print("🧪 Running MindBridge AI Automated Test Suite...")
    subprocess.run([sys.executable, "-m", "pytest", "backend/tests/", "-v"])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Available options: backend | frontend | test")
        return

    command = sys.argv[1].lower()
    if command in ("backend", "server", "api"):
        start_backend()
    elif command in ("frontend", "ui", "web"):
        start_frontend()
    elif command in ("test", "tests"):
        run_tests()
    else:
        print(f"Unknown command: '{command}'")
        print("Usage: python app.py [backend | frontend | test]")


if __name__ == "__main__":
    main()
