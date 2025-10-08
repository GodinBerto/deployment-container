import os
import subprocess
import sys

def main():
    print("🚀 Starting Flask app (dev mode)...")

    # Ensure venv exists
    if not os.path.exists("venv"):
        print("🧩 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])

    # Use the venv Python
    venv_python = os.path.join("venv", "Scripts", "python.exe")

    # Install dependencies if needed
    if os.path.exists("requirements.txt"):
        print("📦 Installing dependencies...")
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])

    # Run Flask app
    print("🔥 Running app...")
    os.environ["FLASK_ENV"] = "development"
    subprocess.run([venv_python, "app.py"])

if __name__ == "__main__":
    main()
