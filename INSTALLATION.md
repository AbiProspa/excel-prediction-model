# Installation and Setup Guide for Excel Prediction Model

This guide details how to set up the Hybrid Adaptive AI model on a new Windows PC.

## Prerequisites

Before starting, ensure the new PC has the following installed:

1.  **Python 3.8 or newer**:
    *   Download from [python.org](https://www.python.org/downloads/).
    *   **IMPORTANT:** During installation, check the box **"Add Python to PATH"**.

2.  **Git (Optional but recommended)**:
    *   Download from [git-scm.com](https://git-scm.com/downloads).
    *   This allows you to clone the repository directly. If not using Git, you can copy the project files via USB or cloud storage.

3.  **Microsoft Excel**:
    *   Required to view the dashboard and run the VBA integration.

---

## Step 1: Transfer Project Files

### Option A: Clone from GitHub (If project is hosted)
Open a terminal (Command Prompt or PowerShell) and run:
```bash
git clone <repository_url>
cd <repository_folder>
```

### Option B: Copy Files Manually
1.  Copy the entire project folder to the new PC.
2.  Open a terminal inside the project folder.

---

## Step 2: Set Up Virtual Environment (Recommended)

It is best practice to use a virtual environment to avoid conflicts with other Python projects.

1.  Open Command Prompt or PowerShell in the project directory.
2.  Create the virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   **PowerShell**:
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   **Command Prompt**:
        ```cmd
        venv\Scripts\activate.bat
        ```
    *(If you see an error about execution policies in PowerShell, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` and try again.)*

---

## Step 3: Install Dependencies

With the virtual environment activated, install the required libraries using the existing requirements file.

Run the following command:
```bash
python -m pip install -r prediction_model/requirements.txt
```

**Note:** This will install:
*   `pandas` (Data processing)
*   `xlwings` (Excel integration)
*   `torch`, `transformers`, `scikit-learn` (AI Model)
*   `watchdog` (Real-time monitoring)
*   And other dependencies. This may take a few minutes.

---

## Step 4: Excel Configuration (Critical)

For the dashboard to communicate with Python, `xlwings` needs to be set up.

1.  **Trust VBA Object Model**:
    *   Open Excel.
    *   Go to **File > Options > Trust Center > Trust Center Settings > Macro Settings**.
    *   Check **"Trust access to the VBA project object model"**.
    *   Click OK.

2.  **Install xlwings Excel Add-in**:
    *   In your terminal (with venv activated), run:
        ```bash
        xlwings addin install
        ```

3.  **Configure Dashboard**:
    *   Open your Excel dashboard file (e.g., `prediction_model/data/feedback.xlsx`).
    *   If using the Template, ensure the `xlwings` references are added. You can run the provided setup helper script to attempt an auto-fix:
        ```bash
        python prediction_model/fix_setup.py
        ```
    *   If the script fails (often due to security settings), follow the manual instructions it prints.

---

## Step 5: Verify Installation

To ensure everything is working correctly:

1.  **Test the Model**:
    Run the main script to process existing data:
    ```bash
    python prediction_model/main.py
    ```
    If successful, it should read the Excel file and update the `ModelOutput` sheet without errors.

2.  **Test Real-Time Monitor**:
    Start the monitor:
    ```bash
    python prediction_model/realtime_monitor.py
    ```
    *   Keep this window open.
    *   Open your Excel file, make a change to the `FeedbackData` sheet, and Save (`Ctrl+S`).
    *   You should see activity in the terminal window indicating it detected the change and processed it.

---

## Summary of Commands

Here is the quick-start cheatsheet for a new PC:

```powershell
# 1. Create venv
python -m venv venv

# 2. Activate venv
.\venv\Scripts\Activate.ps1

# 3. Install libs
python -m pip install -r prediction_model/requirements.txt

# 4. Install Excel Addin
xlwings addin install

# 5. Run Monitor
python prediction_model/realtime_monitor.py
```
