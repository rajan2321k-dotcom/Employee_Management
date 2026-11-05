

import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from main import initialize_sample_data

if __name__ == "__main__":
    print("Initializing sample test data for Employee & Department Management System...")
    initialize_sample_data(prompt_user=False)

