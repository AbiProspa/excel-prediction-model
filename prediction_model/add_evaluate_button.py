import xlwings as xw
import os
import sys

def add_button():
    print("Connecting to the Excel dashboard...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "data", "Feedback_Dashboard_Template.xlsm")
    
    try:
        # Try to connect to active book first, fallback to specific path
        try:
            wb = xw.books.active
            if not wb:
                raise Exception("No active book")
        except:
             print(f"Opening specific file: {excel_path}")
             wb = xw.Book(excel_path)
        
        print(f"Connected to: {wb.name}")
        
        # 2. Ensure xlwings VBA module is present
        # Locate xlwings.bas in the package directory
        xlwings_path = os.path.dirname(xw.__file__)
        bas_path = os.path.join(xlwings_path, 'xlwings.bas')
        
        if not os.path.exists(bas_path):
            print(f"❌ Could not find xlwings.bas at {bas_path}")
            return

        # Check if already imported
        try:
            found = False
            for comp in wb.api.VBProject.VBComponents:
                if comp.Name == "xlwings":
                    found = True
                    break
            
            if not found:
                print("Importing xlwings VBA module...")
                wb.api.VBProject.VBComponents.Import(bas_path)
                print("✓ xlwings VBA module imported.")
            else:
                print("✓ xlwings VBA module already present.")
        except Exception as e:
            print(f"⚠️ Could not import VBA module automatically: {e}")
            print("Please ensure 'Trust access to the VBA project object model' is enabled in Excel.")
            return

        # 3. Add the Button
        # The user specifically requested it on the 'Dashboard' sheet
        target_sheet = "Dashboard"
        if target_sheet not in [s.name for s in wb.sheets]:
             print(f"⚠️ Sheet '{target_sheet}' not found. Creating it...")
             sht = wb.sheets.add(target_sheet)
        else:
             sht = wb.sheets[target_sheet]
        
        # Check if button already exists to avoid duplicates
        existing_buttons = [shape.name for shape in sht.shapes]
        button_name = "EvaluateBtn"
        
        if button_name in existing_buttons:
            print(f"✓ Button '{button_name}' already exists. Re-linking macro...")
            btn = sht.shapes[button_name]
        else:
            print(f"Creating 'Evaluate' button on sheet '{target_sheet}'...")
            # Position: Row 1, Column H (approx)
            left = sht.range("H1").left
            top = sht.range("H1").top
            # Use the underlying COM API for robust button creation on Windows
            btn_api = sht.api.Buttons().Add(left + 10, top + 5, 100, 30)
            btn_api.Name = button_name
            btn_api.Caption = "Evaluate"
            # Get the xlwings Shape object for further manipulation if needed
            btn = sht.shapes[button_name]

        # Link to the Python script
        # The macro name in VBA is usually 'RunPython' followed by the code snippet
        # But we can use the Sample macro or a custom one.
        # xlwings-created VBA includes 'RunPython' which we can call.
        
        # We need a VBA wrapper to call the Python function
        vba_code = """
Sub RunModel()
    RunPython "import prediction_model.main as m; m.run_model_from_excel()"
    MsgBox "AI Dashboard Update Complete!", vbInformation, "Hybrid AI Model"
End Sub

Sub RunEvaluation()
    RunPython "import prediction_model.main as m; m.run_evaluation_from_excel()"
    MsgBox "Model Evaluation Complete!", vbInformation, "Hybrid AI Model"
End Sub
"""
        # Add the VBA wrapper to a new module
        try:
            module_name = "PredictionModelMacros"
            macro_found = False
            
            # Remove old module if exists to update code
            for comp in wb.api.VBProject.VBComponents:
                if comp.Name == module_name:
                    wb.api.VBProject.VBComponents.Remove(comp)
                    break
            
            new_mod = wb.api.VBProject.VBComponents.Add(1) # 1 = vbext_ct_StdModule
            new_mod.Name = module_name
            new_mod.CodeModule.AddFromString(vba_code)
            print(f"✓ VBA Macro 'RunEvaluation' added to module '{module_name}'.")
            
            # Assign macro to button
            btn.api.OnAction = "RunEvaluation"
            
            # Ensure the existing buttons are also correctly linked
            for s in dashboard.shapes:
                if "Run" in s.name:
                    s.api.OnAction = "RunModel"
                elif "Evaluate" in s.name and s.name != button_name:
                    s.api.OnAction = "RunEvaluation"
                    
            print("✓ Buttons linked to AI macros.")
            
        except Exception as e:
             print(f"⚠️ Could not add VBA macro code: {e}")

        wb.save()
        print("\n🎉 SETUP COMPLETE!")
        print("You can now go to Excel and click the 'Evaluate' button.")

    except Exception as e:
        print(f"❌ Error during button setup: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Excel is open with the dashboard file active.")
        print("2. Ensure 'Trust access to the VBA project object model' is enabled.")

if __name__ == "__main__":
    add_button()
