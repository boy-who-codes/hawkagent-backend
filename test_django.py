import sys
import traceback
try:
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "check"])
except Exception as e:
    traceback.print_exc()
