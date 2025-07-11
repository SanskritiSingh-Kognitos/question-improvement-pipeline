#!/usr/bin/env python3
"""
Setup script for Question Improvement Pipeline Web Application
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_files():
    """Check if essential files are present."""
    essential_files = [
        "app.py",
        "simple_question_tester.py", 
        "metrics3.py",
        "local_polisher.py",
        "questions.csv",
        "templates/index.html",
        "templates/metrics.html",
        "templates/improve.html",
        "templates/templates.html",
        "templates/pipeline.html",
        "templates/demo.html"
    ]
    
    print("\n📁 Checking essential files...")
    missing_files = []
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} essential files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All essential files present")
    return True

def test_imports():
    """Test if all modules can be imported."""
    print("\n🧪 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError:
        print("❌ Flask not available")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError:
        print("❌ Pandas not available")
        return False
    
    try:
        import nltk
        print("✅ NLTK imported successfully")
    except ImportError:
        print("❌ NLTK not available")
        return False
    
    try:
        import textblob
        print("✅ TextBlob imported successfully")
    except ImportError:
        print("❌ TextBlob not available")
        return False
    
    try:
        from simple_question_tester import PROMPT_TEMPLATES
        print("✅ Core application modules imported successfully")
    except ImportError as e:
        print(f"❌ Error importing core modules: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Question Improvement Pipeline Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check files
    if not check_files():
        print("\n⚠️  Please ensure all essential files are present before running the application")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n⚠️  Some dependencies may not be properly installed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run: python app.py")
    print("   2. Open: http://localhost:5001")
    print("   3. Optional: Install Ollama for AI polishing features")
    print("\n📖 See README.md for detailed instructions")

if __name__ == "__main__":
    main() 