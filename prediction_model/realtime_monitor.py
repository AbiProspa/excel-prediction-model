import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from load_data import load_feedback_data
from nlp_engine import analyze_comments
from bayesian_model import calculate_probabilities
from risk_engine import assess_risk
from recommendation_engine import generate_recommendations
from export_results import export_to_excel

class ExcelFileHandler(FileSystemEventHandler):
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.last_modified = time.time()
        
    def on_modified(self, event):
        if event.src_path.endswith('.xlsx') and event.src_path == self.excel_path:
            current_time = time.time()
            if current_time - self.last_modified > 2:  # Debounce: wait 2 seconds
                self.last_modified = current_time
                print(f"\n[{time.strftime('%H:%M:%S')}] File changed detected. Running model...")
                self.run_model()
    
    def run_model(self):
        try:
            df = load_feedback_data(self.excel_path)
            if df.empty:
                print("No data loaded.")
                return
            
            df_nlp = analyze_comments(df)
            prob_df = calculate_probabilities(df_nlp)
            risk_df = assess_risk(prob_df)
            final_df = generate_recommendations(risk_df)
            export_to_excel(final_df, self.excel_path)
            
            print(f"✓ Model updated at {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Error running model: {e}")

def monitor_excel(excel_path):
    """Monitor Excel file for changes and run model automatically"""
    if not os.path.exists(excel_path):
        print(f"Error: File not found - {excel_path}")
        return
    
    print(f"Monitoring: {excel_path}")
    print("Watching for changes... (Press Ctrl+C to stop)")
    
    # Run once at start
    event_handler = ExcelFileHandler(excel_path)
    event_handler.run_model()
    
    # Start monitoring
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(excel_path), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitoring stopped.")
    observer.join()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, 'data', 'feedback.xlsx')
    
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    
    print(f"\nExcel file: {excel_path}")
    print(f"Sheet: Feedback_Data")
    print(f"Output: ModelOutput sheet\n")
    
    monitor_excel(excel_path)
