import subprocess
import sys
import os

# Переходим в корень проекта (где папка ui)
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

if os.name == 'nt':   # Windows
    venv_python = os.path.join('venv', 'Scripts', 'python.exe')
else:
    venv_python = os.path.join('venv', 'bin', 'python')

if os.path.exists(venv_python):
    streamlit_cmd = [venv_python, '-m', 'streamlit', 'run', 'ui/app.py']
else:
    streamlit_cmd = [sys.executable, '-m', 'streamlit', 'run', 'ui/app.py']

subprocess.call(streamlit_cmd)