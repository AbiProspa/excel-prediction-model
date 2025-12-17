import xlwings as xw
import os
import sys

def fix_dashboard():
    print("Connecting to Excel...")
    try:
        # Get active book
        wb = xw.books.active
        print(f"Connected to: {wb.name}")
        
        # 1. Fix Naming (..xlsm -> .xlsm)
        target_name = "Feedback_Dashboard_Template.xlsm"
        current_dir = os.path.dirname(wb.fullname)
        target_path = os.path.join(current_dir, target_name)
        
        # Only save if name is different (ignoring case)
        if wb.name.lower() != target_name.lower():
            print(f"Renaming to {target_name}...")
            wb.save(target_path)
            print("✓ File renamed and saved.")
        else:
            print("✓ Filename is correct.")
            
        # 2. Import xlwings.bas
        # Locate xlwings package
        xlwings_path = os.path.dirname(xw.__file__)
        bas_path = os.path.join(xlwings_path, 'xlwings.bas')
        
        if not os.path.exists(bas_path):
            print(f"❌ Could not find xlwings.bas at {bas_path}")
            return

        print(f"Attempting to import xlwings module from: {bas_path}")
        
        try:
            # Check if already exists
            found = False
            for comp in wb.api.VBProject.VBComponents:
                if comp.Name == "xlwings":
                    found = True
                    break
            
            if found:
                 print("✓ xlwings module already present.")
            else:
                 wb.api.VBProject.VBComponents.Import(bas_path)
                 print("✓ xlwings module imported successfully!")
                 
            # Add reference to "RunPython" macro just in case? 
            # No, importing the module is enough.
                 
        except Exception as e:
            print("\n❌ FAILED to import VBA module automatically.")
            print("This is likely due to Excel security settings.")
            print("Please follow these manual steps:")
            print("1. In Excel, go to File > Options > Trust Center > Trust Center Settings > Macro Settings")
            print("2. Check 'Trust access to the VBA project object model'")
            print("3. Run this script again OR manually import the file:")
            print(f"   {bas_path}")
            print("   (Open VBA Editor Alt+F11 > File > Import File...)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        fix_dashboard()
    except Exception as e:
        print(f"Critical Error: {e}")
