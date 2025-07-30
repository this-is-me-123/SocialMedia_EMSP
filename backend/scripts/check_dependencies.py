"""
Script to check for required Python packages.
"""
import importlib
import sys
import subprocess

def check_package(package_name, pip_name=None):
    """Check if a package is installed and return its version."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'version not found')
        return True, version
    except ImportError:
        return False, None

def install_package(package_name):
    """Install a package using pip."""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

# List of required packages
REQUIRED_PACKAGES = [
    'Pillow',
    'moviepy',
    'python-dotenv',
    'requests',
    'schedule',
    'tweepy',
    'facebook-sdk',
    'pytz',
    'python-dateutil'
]

def main():
    print("Checking required packages...\n")
    
    all_installed = True
    for package in REQUIRED_PACKAGES:
        installed, version = check_package(package.lower().replace('-', '_'))
        status = "✅" if installed else "❌"
        print(f"{status} {package}: {version if installed else 'Not installed'}")
        
        if not installed:
            all_installed = False
    
    if not all_installed:
        print("\nSome required packages are missing. Would you like to install them? (y/n)")
        if input().lower() == 'y':
            for package in REQUIRED_PACKAGES:
                installed, _ = check_package(package.lower().replace('-', '_'))
                if not installed:
                    success = install_package(package)
                    if success:
                        print(f"✅ Successfully installed {package}")
                    else:
                        print(f"❌ Failed to install {package}")
    else:
        print("\n✅ All required packages are installed!")

if __name__ == "__main__":
    main()
