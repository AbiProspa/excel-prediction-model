import os
import xlwings as xw


def ensure_xlwings_module(wb):
    xlwings_path = os.path.dirname(xw.__file__)
    bas_path = os.path.join(xlwings_path, "xlwings.bas")

    if not os.path.exists(bas_path):
        raise FileNotFoundError(f"Could not find xlwings.bas at {bas_path}")

    for comp in wb.api.VBProject.VBComponents:
        if comp.Name == "xlwings":
            print("[SUCCESS] xlwings VBA module already present.")
            return

    print("Importing xlwings VBA module...")
    wb.api.VBProject.VBComponents.Import(bas_path)
    print("[SUCCESS] xlwings VBA module imported.")


def install_macro_module(wb, project_root):
    module_name = "PredictionModelMacros"
    project_root = project_root.replace("\\", "\\\\")
    vba_code = f'''
Sub RunModel()
    RunPython "import sys; sys.path.insert(0, r""{project_root}"" ); import prediction_model.main as m; m.run_model_from_excel()"
    MsgBox "AI model run complete. New records should be logged to history.csv.", vbInformation, "Hybrid AI Model"
End Sub

Sub RunEvaluation()
    RunPython "import sys; sys.path.insert(0, r""{project_root}"" ); import prediction_model.main as m; m.run_evaluation_from_excel()"
    MsgBox "Model evaluation complete.", vbInformation, "Hybrid AI Model"
End Sub

Sub RunBenchmark()
    RunPython "import sys; sys.path.insert(0, r""{project_root}"" ); import prediction_model.main as m; m.run_benchmark_from_excel()"
    MsgBox "Benchmark comparison complete. See the Benchmark_Comparison sheet.", vbInformation, "Hybrid AI Model"
End Sub
'''

    for comp in wb.api.VBProject.VBComponents:
        if comp.Name == module_name:
            wb.api.VBProject.VBComponents.Remove(comp)
            break

    new_mod = wb.api.VBProject.VBComponents.Add(1)
    new_mod.Name = module_name
    new_mod.CodeModule.AddFromString(vba_code)
    print(f"[SUCCESS] VBA macros installed in module '{module_name}'.")


def upsert_button(sheet, name, caption, macro, cell, width=120):
    existing = {shape.name: shape for shape in sheet.shapes}
    left = sheet.range(cell).left
    top = sheet.range(cell).top

    if name in existing:
        btn = existing[name]
        print(f"[SUCCESS] Re-linking existing button '{caption}'.")
    else:
        print(f"Creating button '{caption}' on '{sheet.name}'...")
        btn_api = sheet.api.Buttons().Add(left, top, width, 32)
        btn_api.Name = name
        btn = sheet.shapes[name]

    btn.api.Caption = caption
    btn.api.OnAction = macro
    return btn


def add_buttons():
    print("Connecting to the Excel dashboard...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "data", "Feedback_Dashboard_Template.xlsm")

    try:
        try:
            wb = xw.books.active
            if wb is None:
                raise RuntimeError("No active workbook")
        except Exception:
            print(f"Opening workbook: {excel_path}")
            wb = xw.Book(excel_path)

        print(f"Connected to: {wb.name}")
        ensure_xlwings_module(wb)
        install_macro_module(wb, os.path.dirname(base_dir))

        target_sheet = "Dashboard"
        if target_sheet not in [s.name for s in wb.sheets]:
            sheet = wb.sheets.add(target_sheet, before=wb.sheets[0])
        else:
            sheet = wb.sheets[target_sheet]

        upsert_button(sheet, "RunModelBtn", "Run Model", "RunModel", "H1")
        upsert_button(sheet, "EvaluateBtn", "Evaluate", "RunEvaluation", "J1")
        upsert_button(sheet, "BenchmarkBtn", "Benchmark", "RunBenchmark", "L1")

        if "Benchmark_Comparison" not in [s.name for s in wb.sheets]:
            bench = wb.sheets.add("Benchmark_Comparison", after=wb.sheets[-1])
            bench.range("A1").value = "MODEL BENCHMARK COMPARISON"
            bench.range("A3").value = "Click the Benchmark button on the Dashboard sheet to generate this table."

        wb.save()
        print("\nSETUP COMPLETE")
        print("Dashboard buttons are ready: Run Model, Evaluate, Benchmark.")

    except Exception as e:
        print(f"Error during button setup: {e}")
        print("\nTroubleshooting:")
        print("1. Open the dashboard workbook in Excel, then run this script again.")
        print("2. Enable: File > Options > Trust Center > Macro Settings > Trust access to the VBA project object model.")
        print("3. Make sure macros are enabled for this workbook.")


if __name__ == "__main__":
    add_buttons()
