import sys
import os
# Apunta a la carpeta app/ donde está app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app

handler = app