"""
Script to inspect the base_platform.py file for issues.
"""
import os
import sys
from pathlib import Path

def read_file_lines(file_path):
    """Read and return the lines of a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def check_for_issues(lines):
    """Check for common issues in the file content."""
    issues = []
    
    for i, line in enumerate(lines, 1):
        # Check for unclosed quotes or parentheses
        if line.count('"') % 2 != 0:
            issues.append(f"Line {i}: Unclosed double quote")
        if line.count("'") % 2 != 0:
            issues.append(f"Line {i}: Unclosed single quote")
        if line.count('(') != line.count(')'):
            issues.append(f"Line {i}: Unmatched parentheses")
        if line.count('[') != line.count(']'):
            issues.append(f"Line {i}: Unmatched square brackets")
        if line.count('{') != line.count('}'):
            issues.append(f"Line {i}: Unmatched curly braces")
    
    return issues

def main():
    """Main function to inspect the base_platform.py file."""
    print("=== Inspecting base_platform.py ===\n")
    
    # Path to the base_platform.py file
    base_platform_path = Path("automation_stack/social_media/base_platform.py")
    
    if not base_platform_path.exists():
        print(f"❌ File not found: {base_platform_path}")
        return 1
    
    print(f"Reading file: {base_platform_path}")
    
    try:
        # Read the file content
        lines = read_file_lines(base_platform_path)
        print(f"✅ Successfully read {len(lines)} lines")
        
        # Check for common issues
        print("\nChecking for common issues...")
        issues = check_for_issues(lines)
        
        if issues:
            print("\n❌ Found the following issues:")
            for issue in issues:
                print(f"  - {issue}")
            
            # Print the relevant lines with line numbers
            print("\nRelevant lines:")
            for issue in issues:
                line_num = int(issue.split(":")[0].split()[-1])
                start = max(1, line_num - 2)
                end = min(len(lines), line_num + 2)
                
                print(f"\nAround line {line_num}:")
                for i in range(start, end + 1):
                    prefix = "--> " if i == line_num else "    "
                    print(f"{prefix}{i}: {lines[i-1].rstrip()}")
        else:
            print("✅ No common issues found in the file")
        
        # Print the first 10 and last 10 lines for manual inspection
        print("\nFirst 10 lines:")
        for i, line in enumerate(lines[:10], 1):
            print(f"{i}: {line.rstrip()}")
        
        print("\nLast 10 lines:")
        for i, line in enumerate(lines[-10:], len(lines) - 9):
            print(f"{i}: {line.rstrip()}")
        
    except Exception as e:
        print(f"❌ Error inspecting file: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
