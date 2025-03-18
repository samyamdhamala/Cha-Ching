# auth.py - Handles User Authentication with File-Based Storage
import json
from file_manager import load_data, save_data
from models import User

class Authentication:
    def __init__(self):
        data = load_data()
        self.users = [User(**user) for user in data["users"]]  # Load users from file
        self.current_user = None

    def register(self, username: str, password: str, role: str = "user"):
        if any(user.username == username for user in self.users):
            print("[!] Username already exists. Choose another one.")
            return None

        new_user = User(username, password)
        new_user.role = role
        self.users.append(new_user)

        # Save users to file
        data = load_data()
        data["users"].append(vars(new_user))  # Convert object to dictionary
        save_data(data)

        print("[+] Registration successful:", new_user)
        return new_user

    def login(self, username: str, password: str) -> bool:
        for user in self.users:
            if user.username == username and user.password == password:
                self.current_user = user
                print("[+] Login successful:", user)
                return True
        print("[!] Invalid username or password.")
        return False

    def logout(self):
        if self.current_user:
            print(f"[-] User '{self.current_user.username}' logged out.")
        self.current_user = None

    def get_current_user(self):
        return self.current_user
