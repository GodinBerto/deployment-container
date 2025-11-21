import os
import subprocess
import sys

def main():
    print("🚀 Starting Flask app (dev mode)...")

    # Ensure venv exists
    if not os.path.exists("venv"):
        print("🧩 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])

    print("✅ Virtual environment is ready.")
    
    # Use the venv Python
    venv_python = os.path.join("venv", "Scripts", "python.exe")

    # Install dependencies if needed
    if os.path.exists("requirements.txt"):
        print("📦 Installing dependencies...")
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("❌ Cannot proceed without dependencies.")
        return
    
    if not os.path.exists(".env"):
        print("📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_APP=app.py\n")
        print("✅ .env file created with Flask config.")

    # Run Flask app
    print("🔥 Running app...")
    
    os.environ["FLASK_ENV"] = os.getenv("FLASK_ENV", "development")
    os.environ["FLASK_APP"] = os.getenv("FLASK_APP", "app.py")
    os.environ["FLASK_DEBUG"] = "1"
    
    try:
        subprocess.run([venv_python, "-m", "flask", "run", "--no-reload"])
    except KeyboardInterrupt:
            print("\n🛑 Server stopped by user. Exiting cleanly...")
    
    # cmd = input("\nPress Ctrl+R + Enter to rerun, or just Enter to quit: ")
    # if cmd.strip().lower() != "r":
    #     print("👋 Exiting.")
    #     break
    
if __name__ == "__main__":
    main()
    
