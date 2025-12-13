import pandas as pd
import os

def create_dummy_data():
    data = {
        'Date': ['2023-10-01', '2023-10-01', '2023-10-02', '2023-10-02', '2023-10-03'],
        'Product': ['ATM', 'POS', 'Mobile App', 'ATM', 'POS'],
        'Feedback Type': ['Availability', 'Transaction Success', 'Satisfaction', 'Availability', 'Transaction Success'],
        'Rating': [1, 4, 5, 2, 3],
        'Comment': ['The machine is down again', 'Transaction failed multiple times', 'Great app, very fast', 'Network down', 'Slow processing'],
        'Status': ['Open', 'Closed', 'Closed', 'Open', 'Open']
    }
    df = pd.read_json(pd.DataFrame(data).to_json()) # Ensure clean types
    
    # Create directory if it doesn't exist
    os.makedirs('prediction_model/data', exist_ok=True)
    
    file_path = 'prediction_model/data/feedback.xlsx'
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='FeedbackData', index=False)
    print(f"Created {file_path}")

if __name__ == "__main__":
    create_dummy_data()
