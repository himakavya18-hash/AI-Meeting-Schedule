"""
Meeting Portal Runner
Starts the Django dev server and opens http://127.0.0.1:8000/ in the default web browser.
Run with: python run.py
"""
import os
import sys
import webbrowser
import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def main():
    python_exec = sys.executable
    # Prefer virtual environment python if available
    venv_python_win = BASE_DIR / 'venv' / 'Scripts' / 'python.exe'
    if venv_python_win.exists():
        python_exec = str(venv_python_win)

    print("=" * 60)
    print("  🚀 Starting AI Meeting Decision & Action Portal")
    print(f"  📂 Directory: {BASE_DIR}")
    print(f"  🐍 Python: {python_exec}")
    print("=" * 60)

    # Open browser after a brief pause
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:8000/")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Django development server
    try:
        subprocess.run([python_exec, "manage.py", "runserver", "8000"], cwd=str(BASE_DIR))
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")

if __name__ == '__main__':
    main()
