import subprocess
import sys

with open('final_check.log', 'w') as f:
    f.write("Starting check...\n")
    try:
        process = subprocess.Popen(
            [sys.executable, 'manage.py', 'check'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        f.write("STDOUT:\n")
        f.write(stdout)
        f.write("\nSTDERR:\n")
        f.write(stderr)
        f.write(f"\nExit code: {process.returncode}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
print("Check complete, see final_check.log")
