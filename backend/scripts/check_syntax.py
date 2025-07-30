"""
Script to check for syntax errors in Python files.
"""
import os
import sys
import ast
from pathlib import Path

def check_file(file_path):
    """Check a single Python file for syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error in {file_path}: {e.msg} at line {e.lineno}, offset {e.offset}"
    except Exception as e:
        return False, f"Error checking {file_path}: {str(e)}"

def main():
    """Check all Python files in the project for syntax errors."""
    print("=== Checking Python files for syntax errors ===\n")
    
    # Get all Python files in the project
    project_root = Path(__file__).parent
    python_files = list(project_root.rglob("*.py"))
    
    # Check each file
    all_ok = True
    for file_path in python_files:
        # Skip virtual environment and other excluded directories
        if any(part.startswith(('.', '_')) and part not in ['__init__.py'] for part in file_path.parts):
            continue
            
        print(f"Checking {file_path.relative_to(project_root)}...")
        success, message = check_file(file_path)
        
        if success:
            print("  ✅ No syntax errors")
        else:
            print(f"  ❌ {message}")
            all_ok = False
    
    if all_ok:
        print("\n✅ All Python files are syntactically correct")
    else:
        print("\n❌ Some Python files have syntax errors")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
