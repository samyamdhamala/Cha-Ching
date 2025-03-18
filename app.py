# app.py - Main Application Entry Point with File-Based Storage
import sys
from auth import Authentication
from expenses import ExpenseTracker
from file_manager import load_data, save_data
from models import User, Expense, Category
from file_manager import hash_password


def create_admin(auth):
    data = load_data()

    for user in data["users"]:
        if user["username"] == "admin":
            # If admin password is in plain text, hash it
            if len(user["password"]) != 64:  # SHA-256 hashes are always 64 characters long
                print("[!] Admin password found in plain text. Converting to hash...")
                user["password"] = hash_password(user["password"])  # Convert to hash
                save_data(data)
                print("[✔] Admin password has been secured.")
            return

    # If no admin exists, create one with a hashed password
    print("[i] No admin found. Creating a new one...")
    admin_user = {
        "user_id": 1,
        "username": "admin",
        "password": hash_password("adminpass"),  # Store hashed password
        "role": "admin"
    }
    data["users"].append(admin_user)
    save_data(data)
    print("[✔] Admin account created with hashed password.")


def main_menu(auth):
    while True:
        print("\n=== Main Menu ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            auth.register(username, password)
        elif choice == "2":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            if auth.login(username, password):
                return auth.get_current_user()
        elif choice == "3":
            print("Exiting... Goodbye!")
            sys.exit(0)
        else:
            print("[!] Invalid choice.")


def admin_menu():
    data = load_data()
    data["categories"] = {int(k): v for k, v in data.get("categories", {}).items()}  # Ensure keys are integers

    while True:
        print("\n=== Admin Menu ===")
        print("1. Create Category")
        print("2. View Categories")
        print("3. Edit Category")
        print("4. Delete Category")
        print("5. Logout")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            name = input("Enter new category name: ").strip()
            if name:
                category_id = max(data["categories"].keys(), default=0) + 1  # Ensure unique category IDs
                new_cat = Category(name=name, user_id=1, category_id=category_id)
                data["categories"][category_id] = vars(new_cat)
                save_data(data)
                print("[+] Category created.")

        elif choice == "2":
            print("\nAvailable Categories:")
            for cat_id, cat in data["categories"].items():
                print(f"{cat_id}: {cat['name']}")

        elif choice == "3":
            print("\nAvailable Categories:")
            for cat_id, cat in data["categories"].items():
                print(f"{cat_id}: {cat['name']}")
            try:
                cat_id = int(input("Enter category ID to edit: ").strip())
                if cat_id in data["categories"]:
                    new_name = input("Enter new category name: ").strip()
                    data["categories"][cat_id]["name"] = new_name
                    save_data(data)
                    print("[+] Category updated.")
                else:
                    print("[!] Invalid Category ID.")
            except ValueError:
                print("[!] Invalid input. Please enter a number.")

        elif choice == "4":
            print("\nAvailable Categories:")
            for cat_id, cat in data["categories"].items():
                print(f"{cat_id}: {cat['name']}")
            try:
                cat_id = int(input("Enter category ID to delete: ").strip())
                if cat_id in data["categories"]:
                    del data["categories"][cat_id]
                    save_data(data)
                    print("[+] Category deleted.")
                else:
                    print("[!] Invalid Category ID.")
            except ValueError:
                print("[!] Invalid input. Please enter a number.")

        elif choice == "5":
            print("Logging out...")
            break
        else:
            print("[!] Invalid choice.")


def user_menu(auth, user_trackers):
    user = auth.get_current_user()
    if user.user_id not in user_trackers:
        user_trackers[user.user_id] = ExpenseTracker(user)
    tracker = user_trackers[user.user_id]

    while True:
        print("\n=== User Menu ===")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. Set Budget")
        print("6. View Summary")
        print("7. Logout")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            tracker.add_expense()
        elif choice == "2":
            tracker.list_expenses()
        elif choice == "3":
            tracker.edit_expense()
        elif choice == "4":
            tracker.delete_expense()
        elif choice == "5":
            period = input("Enter budget period (YYYY-MM): ").strip()
            try:
                amount = float(input("Enter budget amount: ").strip())
                tracker.set_budget(period, amount)
            except ValueError:
                print("[!] Invalid budget amount. Please enter a numeric value.")
        elif choice == "6":
            tracker.view_summary()
        elif choice == "7":
            print("[-] Logging out...")
            auth.logout()
            break
        else:
            print("[!] Invalid choice. Please select a valid option.")



def run_app():
    auth = Authentication()
    create_admin(auth)
    user_trackers = {}
    while True:
        user = main_menu(auth)
        if user.role == "admin":
            admin_menu()
        else:
            user_menu(auth, user_trackers)


if __name__ == "__main__":
    run_app()
