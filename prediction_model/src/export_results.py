import xlwings as xw
import pandas as pd
import os

def export_to_excel(df, filepath, sheet_name='ModelOutput'):
    """
    Exports the dataframe to the specified sheet in the Excel file.
    
    Args:
        df (pd.DataFrame): DataFrame to export.
        filepath (str): Path to the Excel file.
        sheet_name (str): Name of the sheet to export to. Default is 'ModelOutput'.
    """
    if df.empty:
        print("No data to export.")
        return

    try:
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return

        app = xw.App(visible=False)
        wb = app.books.open(filepath)
        
        # Check if sheet exists, if not create it
        sheet_names = [sheet.name for sheet in wb.sheets]
        if sheet_name in sheet_names:
            sheet = wb.sheets[sheet_name]
            sheet.clear() # Clear existing data
        else:
            sheet = wb.sheets.add(sheet_name)
            
        # Write data
        sheet.range('A1').options(index=False).value = df
        
        wb.save()
        wb.close()
        app.quit()
        print(f"Successfully exported results to {sheet_name} in {filepath}")
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        try:
            if 'app' in locals():
                app.quit()
        except:
            pass
