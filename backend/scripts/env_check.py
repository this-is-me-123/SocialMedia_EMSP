"""
Environment check script with detailed output.
"""
import sys
import os
import platform
import importlib

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, '='))
    print("=" * 80)

def check_python_version():
    """Check Python version and related info."""
    print_header("PYTHON ENVIRONMENT")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.path}")

def check_imports():
    """Check if required packages can be imported."""
    print_header("REQUIRED PACKAGES")
    packages = [
        'Pillow',  # For image processing
        'requests',  # For HTTP requests
        'python-dotenv',  # For .env file handling
        'schedule',  # For scheduling
        'typing',  # For type hints
        'logging',  # For logging
        'pathlib',  # For path handling
        'abc',  # For abstract base classes
        'datetime',  # For date/time handling
    ]
    
    for pkg in packages:
        try:
            mod = importlib.import_module(pkg.split('-')[0] if '-' in pkg else pkg)
            print(f"✅ {pkg:20} {getattr(mod, '__version__', 'version not available')}")
        except ImportError:
            print(f"❌ {pkg:20} NOT INSTALLED")

def check_file_system():
    """Check file system access."""
    print_header("FILE SYSTEM ACCESS")
    
    # Check current directory contents
    print("\nCurrent directory contents:")
    try:
        for item in os.listdir('.'):
            if os.path.isfile(item):
                print(f"📄 {item}")
            elif os.path.isdir(item):
                print(f"📁 {item}/")
    except Exception as e:
        print(f"❌ Error listing directory: {e}")
    
    # Check automation_stack directory
    print("\nChecking automation_stack directory:")
    try:
        if os.path.exists('automation_stack'):
            print("✅ automation_stack/ exists")
            if os.path.isdir('automation_stack'):
                print("✅ automation_stack/ is a directory")
                print("Contents:", os.listdir('automation_stack'))
            else:
                print("❌ automation_stack/ is not a directory")
        else:
            print("❌ automation_stack/ does not exist")
    except Exception as e:
        print(f"❌ Error checking automation_stack/: {e}")

def main():
    """Run all checks."""
    check_python_version()
    check_imports()
    check_file_system()
    
    print_header("ENVIRONMENT CHECK COMPLETE")
    print("\nIf you see any ❌, those items need attention.")

if __name__ == "__main__":
    main()
