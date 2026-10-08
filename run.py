import os
import sys
import subprocess
import shutil

def run():
    print("=================================================")
    print("   Wide World Importers - End-to-End Pipeline    ")
    print("=================================================")

    if not os.path.exists(".env"):
        print("Creating .env from .env.example...")
        shutil.copy(".env.example", ".env")

    print("\n[Step 1/4] Starting Docker containers (PostgreSQL)...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

    print("\n[Step 2/4] Setting up Python virtual environment...")
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # Determine the python executable inside the venv
    venv_python = os.path.join("venv", "bin", "python") if os.name != 'nt' else os.path.join("venv", "Scripts", "python.exe")
    
    print("Installing/verifying Python dependencies...")
    subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"], check=True)

    print("\n[Step 3/4] Downloading Kaggle dataset...")
    subprocess.run([venv_python, "src/download_data.py"], check=True)

    print("\n[Step 4/4] Running the Data Engineering Pipeline...")
    subprocess.run([venv_python, "src/pipeline.py"], check=True)

    print("\n=================================================")
    print("          PIPELINE EXECUTED SUCCESSFULLY!        ")
    print("=================================================")

if __name__ == "__main__":
    run()
