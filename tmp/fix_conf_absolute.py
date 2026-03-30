import os
path = 'prediction_model/data/xlwings.conf'
# Use absolute paths for absolute stability on Windows
interpreter = r'C:\Users\abiod\Documents\scratch\scratch\venv\Scripts\python.exe'
pythonpath = r'C:\Users\abiod\Documents\scratch\scratch'

with open(path, 'wb') as f:
    # We write exactly two lines as expected by the xlwings.bas Input loop
    line1 = f'"Interpreter","{interpreter}"\r\n'.encode('ascii')
    line2 = f'"PYTHONPATH","{pythonpath}"'.encode('ascii')
    f.write(line1 + line2)

print(f"Successfully wrote xlwings.conf with absolute paths.")
print(f"Interpreter: {interpreter}")
print(f"PYTHONPATH: {pythonpath}")
