"""
Script to view the content of base_platform.py
"""
import os

def main():
    """Main function to display the content of base_platform.py."""
    file_path = "automation_stack/social_media/base_platform.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"=== Content of {file_path} ===\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f.read())
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")

if __name__ == "__main__":
    main()
