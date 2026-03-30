import pandas as pd
import os
import xlwings as xw

def create_dummy_data():
    data = {
        'Date': ['2023-10-01', '2023-10-01', '2023-10-02', '2023-10-02', '2023-10-03'],
        'Product': ['ATM', 'POS', 'Mobile App', 'ATM', 'POS'],
        'Feedback Type': ['Availability', 'Transaction Success', 'Satisfaction', 'Availability', 'Transaction Success'],
        'Rating': [1, 4, 5, 2, 3],
        'Comment': ['The machine is down again', 'Transaction failed multiple times', 'Great app, very fast', 'Network down', 'Slow processing'],
        'Status': ['Open', 'Closed', 'Closed', 'Open', 'Open']
    }
    df = pd.DataFrame(data)
    
    # Create directory if it doesn't exist
    os.makedirs('prediction_model/data', exist_ok=True)
    
    # Target the primary .xlsm template
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'prediction_model', 'data', 'Feedback_Dashboard_Template.xlsm')
    
    print(f"Writing synthetic data to {file_path} [Sheet: FeedbackData]...")
    
    try:
        # Use xlwings for robust xlsm handling
        app = xw.App(visible=False)
        wb = app.books.open(file_path)
        
        # Ensure sheet exists
        if 'Feedback_Data' not in [s.name for s in wb.sheets]:
            sht = wb.sheets.add('Feedback_Data')
        else:
            sht = wb.sheets['Feedback_Data']
            sht.clear_contents()
            
        # Write the dataframe
        sht.range("A1").value = df
        
        wb.save()
        wb.close()
        app.quit()
        print(f"✓ Data generation complete.")
    except Exception as e:
        print(f"❌ Error during data generation: {e}")
        try: app.quit() 
        except: pass

if __name__ == "__main__":
    create_dummy_data()
