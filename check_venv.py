import django
import sys
import os

with open('venv_version.txt', 'w') as f:
    f.write(f"Django Version: {django.get_version()}\n")
    f.write(f"Python Executable: {sys.executable}\n")
    f.write(f"Python Version: {sys.version}\n")
