import os
path = 'prediction_model/data/xlwings.conf'
with open(path, 'wb') as f:
    # VBA's Input # command fails if there are trailing newlines or blank lines.
    # We write exactly two lines without a final newline at the very end.
    f.write(b'"Interpreter","../../venv/Scripts/python.exe"\r\n"PYTHONPATH",".."')
print("Successfully wrote xlwings.conf without trailing newlines.")
