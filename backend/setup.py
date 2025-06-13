#!/usr/bin/env python3
"""
Setup script for CaseMatch Flask Backend
This script automates the installation and configuration of the backend environment.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_python_version():
    """Check if Python 3.8+ is available"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} found")
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📦 Virtual environment already exists")
        return True
    
    print("📦 Creating virtual environment...")
    success, stdout, stderr = run_command(f"{sys.executable} -m venv venv")
    
    if success:
        print("✅ Virtual environment created")
        return True
    else:
        print(f"❌ Failed to create virtual environment: {stderr}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📥 Installing Python dependencies...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip"
    
    # Upgrade pip first
    success, stdout, stderr = run_command(f"{pip_path} install --upgrade pip")
    if not success:
        print(f"⚠️  Warning: Could not upgrade pip: {stderr}")
    
    # Install requirements
    success, stdout, stderr = run_command(f"{pip_path} install -r requirements.txt")
    
    if success:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚙️  .env file already exists")
        return True
    
    if env_example.exists():
        print("⚙️  Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("✅ .env file created. Please update it with your SAS Viya credentials.")
        return True
    else:
        print("❌ .env.example not found")
        return False

def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_path = "venv/bin/python"
    
    # Test import of key modules
    test_command = f'{python_path} -c "import flask, saspy, sklearn, pandas, numpy; print(\'All modules imported successfully\')"'
    success, stdout, stderr = run_command(test_command)
    
    if success:
        print("✅ Installation test passed")
        return True
    else:
        print(f"❌ Installation test failed: {stderr}")
        return False

def print_next_steps():
    """Print instructions for next steps"""
    print("\n🎉 Setup complete! Next steps:")
    print("1. Update the .env file with your SAS Viya credentials")
    print("2. Ensure your SAS Viya server is accessible")
    print("3. Create the 'topic_vectors' table in your CAS environment")
    print("4. Start the backend server:")
    
    if os.name == 'nt':  # Windows
        print("   python run.py")
    else:  # Unix/Linux/macOS
        print("   python run.py")
    
    print("\n📋 Backend will be available at: http://localhost:5001")
    print("📋 Test the connection: http://localhost:5001/health")

def main():
    """Main setup function"""
    print("🚀 CaseMatch Flask Backend Setup")
    print("=" * 40)
    
    # Change to backend directory
    os.chdir(Path(__file__).parent)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("⚠️  Installation completed but tests failed. You may need to troubleshoot.")
    
    print_next_steps()

if __name__ == "__main__":
    main()