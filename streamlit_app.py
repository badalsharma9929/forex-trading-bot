"""
Forex Trading Bot - Streamlit App Entry Point
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from monitoring.dashboard import main

if __name__ == "__main__":
    main()
