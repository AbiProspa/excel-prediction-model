import xlwings as xw
import pandas as pd
import os
from datetime import datetime

def export_to_excel(df, excel_path, sheet_name='Output'):
    """
    Exports the dataframe to the specified 'Output' sheet in the Excel file.
    Creates dashboard-ready output with formatting.
    
    Args:
        df (pd.DataFrame): DataFrame to export.
        excel_path (str): Path to the Excel file.
        sheet_name (str): Name of the sheet to export to. Default is 'Output'.
    """
    if df.empty:
        print("No data to export.")
        return

    print(f"Exporting results to {excel_path} [{sheet_name}]...")

    # Select and order the output columns as required
    output_columns = [
        'Feedback Type',
        'Average Rating',
        'Average Sentiment Score',  
        'Risk Level',
        'Top Issue Summary',
        'Recommendation',
        'Probability Score'
    ]
    
    # Filter to only include columns that exist in the dataframe
    existing_columns = [col for col in output_columns if col in df.columns]
    output_df = df[existing_columns].copy()
    
    # Add timestamp column
    output_df['Last Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Rename for dashboard clarity
    output_df = output_df.rename(columns={
        'Average Sentiment Score': 'Sentiment Score'
    })

    try:
        # Check if file exists
        if not os.path.exists(excel_path):
            print(f"Error: File not found at {excel_path}")
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        # Open Excel
        # Try to reuse existing app if running from Excel
        try:
            app = xw.apps.active
            if app is None:
                raise Exception("No active app")
            wb = app.books.active
            if wb is None or wb.fullname.lower() != excel_path.lower():
                # Different workbook, open the target one
                wb = app.books.open(excel_path)
        except:
            # Not running from Excel, create new instance
            app = xw.App(visible=False)
            wb = app.books.open(excel_path)
        
        # Check if sheet exists, if not create it
        sheet_names = [sheet.name for sheet in wb.sheets]
        if sheet_name in sheet_names:
            sheet = wb.sheets[sheet_name]
            sheet.clear_contents()  # Clear existing data but keep the sheet
        else:
            sheet = wb.sheets.add(sheet_name)
            
        # Write data starting at A1
        sheet.range('A1').value = output_df
        
        # Format headers (row 1) as bold
        header_range = sheet.range('A1').expand('right')
        header_range.font.bold = True
        header_range.color = (68, 114, 196)  # Blue header
        header_range.font.color = (255, 255, 255)  # White text
        
        # Auto-fit columns
        sheet.autofit('c')
        
        # Save and close
        wb.save()
        
        # Only quit if we created the app (not called from Excel)
        if app != xw.apps.active:
            wb.close()
            app.quit()
        
        print(f"✓ Successfully exported {len(output_df)} rows to '{sheet_name}' sheet.")
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        # Try to clean up
        try:
            if 'wb' in locals() and wb:
                wb.close()
            if 'app' in locals() and app and app != xw.apps.active:
                app.quit()
        except:
            pass
        raise

