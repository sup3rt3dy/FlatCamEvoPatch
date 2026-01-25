#!/usr/bin/env python3
"""
Verify which widget set_value() methods still need protection
"""

import re
from pathlib import Path

def check_widget_methods():
    """Check which set_value methods have exception handling"""
    print("=" * 70)
    print("Widget Safety Verification")
    print("=" * 70)
    
    gui_file = Path(r"C:\temp\flatcam_beta_broken\appGUI\GUIElements.py")
    
    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all class definitions and their set_value methods
    classes_to_check = [
        'FCCheckBox',
        'FCCheckBox2', 
        'FCEntry',
        'FCEntry2',
        'FCSpinner',
        'FCDoubleSpinner',
        'FCComboBox'
    ]
    
    print("\nChecking widget classes for set_value() exception handling:\n")
    
    for class_name in classes_to_check:
        # Find the class
        class_pattern = f'class {class_name}\\('
        class_idx = content.find(class_pattern)
        
        if class_idx < 0:
            print(f"  ⚠ {class_name}: CLASS NOT FOUND")
            continue
        
        # Find the next class
        next_class_idx = content.find('\nclass ', class_idx + 1)
        if next_class_idx < 0:
            next_class_idx = len(content)
        
        class_section = content[class_idx:next_class_idx]
        
        # Check if set_value exists
        if 'def set_value(' not in class_section:
            print(f"  - {class_name}: No set_value() method")
            continue
        
        # Check if it has try/except
        if 'try:' in class_section and 'RuntimeError' in class_section:
            print(f"  ✓ {class_name}: HAS exception handling")
        else:
            print(f"  ✗ {class_name}: NEEDS exception handling")
    
    return True

if __name__ == "__main__":
    check_widget_methods()