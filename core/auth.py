# auth.py - Handles User Authentication with Password Encryption
import itertools
import logging
import datetime
from core.models import User
from core.file_manager import load_data, save_data, hash_password, verify_password

class Authentication:
    def __init__(self):
        """Initializes the authentication system and loads user data."""
        try:
            data = load_data()
            self.users = [User(**user) for user in data.get("users", [])]
            if self.users:
                max_id = max(user.user_id for user in self.users)
                User._id_counter = itertools.count(max_id + 1)
        except Exception as e:
            logging.error(f"Failed to load user data: {e}")
            self.users = []
        self.current_user = None

    def register(self, username: str, password: str, role: str = "user"):
        """Registers a new user, ensuring the username is unique."""
        if any(user.username == username for user in self.users):
            logging.warning(f"Registration failed: Username '{username}' already exists.")
            print("[!] Username already exists. Choose another one.")
            return None

        try:
            new_user = User(username, hash_password(password), role)
            self.users.append(new_user)

            data = load_data()
            data["users"].append(vars(new_user))
            save_data(data)

            logging.info(f"User '{username}' registered successfully.")
            print("[+] Registration successful:", new_user)
            return new_user
        except Exception as e:
            logging.error(f"Error during registration: {e}")
            print("[!] Failed to register user.")
            return None

    def login(self, username: str, password: str) -> bool:
        """Logs in a user if the username and password match."""
        for user in self.users:
            if user.username == username:
                try:
                    if verify_password(user.password, password):  # <-- ✅ Correct order
                        self.current_user = user
                        logging.info(f"User '{username}' logged in.")
                        print("[+] Login successful.")
                        return True
                except Exception as e:
                    logging.warning(f"Password verification failed: {e}")
                    return False

        logging.warning(f"Login failed for username '{username}'.")
        print("[!] Invalid username or password.")
        return False

    def logout(self):
        """Logs out the current user."""
        if self.current_user:
            logging.info(f"User '{self.current_user.username}' logged out.")
            print(f"[-] User '{self.current_user.username}' logged out.")
        self.current_user = None

    def get_current_user(self):
        """Returns the currently logged-in user."""
        return self.current_user
