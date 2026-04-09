import subprocess
import os
import sys

def run_cmd(cmd, description):
    print(f"\n--- [TEST] {description} ---")
    print(f"Executing: {cmd}")
    try:
        # Using sys.executable to ensure we use the same python environment
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[TEST ERROR] Command failed with exit code {e.returncode}")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py_exe = sys.executable
    
    print("========================================")
    print("   AI SYSTEM END-TO-END TEST START      ")
    print("========================================")

    # 1. Reset History
    script_populate = os.path.join(base_dir, "prediction_model", "scripts", "populate_history.py")
    if not run_cmd([py_exe, script_populate], "Populating History (Baseline Reset)"):
        return

    # 2. Inject Scenario
    script_scenario = os.path.join(base_dir, "prediction_model", "scripts", "generate_scenarios.py")
    if not run_cmd([py_exe, script_scenario, "--scenario", "outage"], "Injecting 'Outage' Scenario"):
        return

    # 3. Running Model
    script_main = os.path.join(base_dir, "prediction_model", "main.py")
    # Since main.py uses xlwings, we might need to be careful if Excel is not available 
    # but the script has fallbacks.
    if not run_cmd([py_exe, script_main], "Running Main Model Orchestrator"):
        return

    # 4. Running Evaluation
    script_eval = os.path.join(base_dir, "prediction_model", "src", "evaluate_model.py")
    if not run_cmd([py_exe, script_eval, "--history"], "Running Evaluation (Metrics Check)"):
        return

    print("\n========================================")
    print("   AI SYSTEM TEST COMPLETED SUCCESS     ")
    print("========================================")

if __name__ == "__main__":
    main()
