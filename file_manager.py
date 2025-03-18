# file_manager.py - Handles File-Based I/O with User-Specific Storage & Logging
import json
import os
import logging
from hashlib import sha256

DATA_FILE = "data.json"
LOG_FILE = "app.log"

# Initialize logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": [], "expenses": {}, "categories": {}, "budgets": {}}, f)

def load_data():
    """Loads data from the JSON file. Logs if an error occurs."""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return {"users": [], "expenses": {}, "categories": {}, "budgets": {}}

def save_data(data):
    """Saves data to the JSON file. Logs success or failure."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        logging.info("Data saved successfully.")
    except Exception as e:
        logging.error(f"Error saving data: {e}")

def hash_password(password):
    """Encrypts the password using SHA-256."""
    return sha256(password.encode()).hexdigest()

def verify_password(stored_password, input_password):
    """Verifies the hashed password."""
    return stored_password == hash_password(input_password)

