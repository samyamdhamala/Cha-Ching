# file_manager.py - Handles File-Based I/O
import json
import os

DATA_FILE = "data.json"

# Initialize file if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": [], "expenses": [], "categories": [], "budgets": {}}, f)

def load_data():
    """Load data from the JSON file."""
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Save data to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
