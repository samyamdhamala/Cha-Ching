# file_manager.py - Handles File-Based I/O with User-Specific Storage & Logging
import json
import os
import logging
from hashlib import sha256


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'data.json')
LOG_FILE = os.path.join(BASE_DIR, 'data', 'app.log')

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": [], "expenses": {}, "categories": {}, "budgets": {}}, f)

def load_data():
    """Loads data from the JSON file. Logs if an error occurs."""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Data file not found. Returning empty structure.")
    except json.JSONDecodeError:
        logging.error("Data file is corrupted. Returning empty structure.")
    except Exception as e:
        logging.exception("Unexpected error while loading data:")
    return {"users": [], "expenses": {}, "categories": {}, "budgets": {}}

def save_data(data):
    """Saves data to the JSON file. Logs success or failure."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        logging.info("Data saved successfully.")
    except IOError as e:
        logging.error(f"I/O error while saving data: {e}")
    except Exception:
        logging.exception("Unexpected error while saving data.")


def hash_password(password):
    """Encrypts the password using SHA-256."""
    return sha256(password.encode()).hexdigest()

def verify_password(stored_password, input_password):
    """Verifies the hashed password."""
    return stored_password == hash_password(input_password)

