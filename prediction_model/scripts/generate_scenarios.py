import pandas as pd
import os
import xlwings as xw
import argparse
from datetime import datetime, timedelta

def generate_scenario(scenario_type):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', 'Feedback_Dashboard_Template.xlsm')
    
    if scenario_type == 'outage':
        data = {
            'Date': [(datetime.now() - timedelta(hours=i)).strftime('%Y-%m-%d %H:%M') for i in range(5)],
            'Product': ['ATM', 'ATM', 'Online Banking', 'ATM', 'Service'],
            'Feedback Type': ['Availability', 'Availability', 'Login', 'Hardware', 'Support'],
            'Rating': [1, 1, 2, 1, 2],
            'Comment': [
                'The ATM is down and crashed again!', 
                'Cannot withdraw money, screen is black.', 
                'Login failed completely, getting error 500.', 
                'Card stuck in machine, it is broken.', 
                'Support line is busy for hours, terrible service.'
            ],
            'Status': ['Open'] * 5
        }
    elif scenario_type == 'stable':
        data = {
            'Date': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d %H:%M') for i in range(5)],
            'Product': ['App', 'POS', 'ATM', 'Loan Process', 'Service'],
            'Feedback Type': ['Performance', 'Success', 'UX', 'Speed', 'Helpfulness'],
            'Rating': [5, 5, 4, 5, 5],
            'Comment': [
                'Great app, very fast and smooth.', 
                'Payment went through instantly, thanks!', 
                'ATM was clean and worked well.', 
                'Loan approved in minutes, amazing speed.', 
                'The agent was very helpful and kind.'
            ],
            'Status': ['Closed'] * 5
        }
    else: # mixed
        data = {
            'Date': [(datetime.now() - timedelta(hours=i*2)).strftime('%Y-%m-%d %H:%M') for i in range(5)],
            'Product': ['ATM', 'App', 'POS', 'Loan Process', 'Online Banking'],
            'Feedback Type': ['Availability', 'UI', 'Success', 'Documentation', 'Login'],
            'Rating': [2, 4, 5, 3, 1],
            'Comment': [
                'ATM is slow and sometimes errors out.', 
                'App looks good but could be faster.', 
                'Perfect transaction.', 
                'The forms are a bit confusing.', 
                'I cannot log in, the system says fraud detected!'
            ],
            'Status': ['Open', 'Closed', 'Closed', 'Open', 'Open']
        }

    df = pd.DataFrame(data)
    
    print(f"Applying scenario: {scenario_type.upper()}")
    print(f"Target file: {file_path}")

    try:
        app = xw.App(visible=False)
        wb = app.books.open(file_path)
        
        sheet_name = 'Feedback_Data'
        if sheet_name not in [s.name for s in wb.sheets]:
            sht = wb.sheets.add(sheet_name)
        else:
            sht = wb.sheets[sheet_name]
            sht.clear_contents()
            
        sht.range("A1").value = df
        
        wb.save()
        wb.close()
        app.quit()
        print(f"✓ Scenario '{scenario_type}' injected successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")
        try: app.quit() 
        except: pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Test Scenarios for AI Model')
    parser.add_argument('--scenario', choices=['outage', 'stable', 'mixed'], default='mixed', help='Type of data to generate')
    args = parser.parse_args()
    generate_scenario(args.scenario)
