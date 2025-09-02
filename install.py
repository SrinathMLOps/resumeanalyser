"""
Installation script for Resume Analyzer
Handles dependency installation step by step
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Resume Analyzer Installation Script")
    print("=" * 50)
    
    # Step 1: Upgrade pip and install build tools
    if not run_command("python -m pip install --upgrade pip setuptools wheel", "Upgrading pip and build tools"):
        print("⚠️  Continuing with existing pip version...")
    
    # Step 2: Install core dependencies one by one
    core_deps = [
        "python-dotenv",
        "numpy",
        "azure-core",
        "openai",
        "chainlit"
    ]
    
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️  Failed to install {dep}, you may need to install it manually")
    
    # Step 3: Install Azure Document Intelligence (might be tricky)
    print("\n🔄 Installing Azure Document Intelligence...")
    if not run_command("pip install azure-ai-documentintelligence", "Installing Azure Document Intelligence"):
        print("⚠️  Trying alternative installation method...")
        if not run_command("pip install --pre azure-ai-documentintelligence", "Installing Azure Document Intelligence (pre-release)"):
            print("❌ Could not install Azure Document Intelligence. You may need to install it manually.")
    
    print("\n" + "=" * 50)
    print("🎉 Installation completed!")
    print("\nNext steps:")
    print("1. Update your .env file with Azure credentials")
    print("2. Run: chainlit run chainlit_app.py -w")
    print("3. Open http://localhost:8000 in your browser")

if __name__ == "__main__":
    main()