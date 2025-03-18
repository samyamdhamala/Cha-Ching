# app.py - Main Application Entry Point with File-Based Storage
import sys
from auth import Authentication
from expenses import ExpenseTracker
from file_manager import load_data, save_data
from models import User, Expense, Category

def create_admin(auth):
    if not any(user.username == "admin" for user in auth.users):
        auth.register("admin", "adminpass", role="admin")
        print("[i] Admin account created.")

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
    categories = [Category(**cat) for cat in data["categories"]]

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
                new_cat = Category(name)
                categories.append(new_cat)
                data["categories"].append(vars(new_cat))
                save_data(data)
                print("[+] Category created.")
        elif choice == "2":
            print("\nAvailable Categories:")
            for cat in categories:
                print(cat)
        elif choice == "3":
            print("\nAvailable Categories:")
            for idx, cat in enumerate(categories, start=1):
                print(f"{idx}. {cat.name}")
            try:
                cat_index = int(input("Enter category number to edit: ")) - 1
                new_name = input("Enter new category name: ").strip()
                categories[cat_index].name = new_name
                data["categories"][cat_index]["name"] = new_name
                save_data(data)
                print("[+] Category updated.")
            except (IndexError, ValueError):
                print("[!] Invalid selection.")
        elif choice == "4":
            print("\nAvailable Categories:")
            for idx, cat in enumerate(categories, start=1):
                print(f"{idx}. {cat.name}")
            try:
                cat_index = int(input("Enter category number to delete: ")) - 1
                del categories[cat_index]
                del data["categories"][cat_index]
                save_data(data)
                print("[+] Category deleted.")
            except (IndexError, ValueError):
                print("[!] Invalid selection.")
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
        print("3. Set Budget")
        print("4. View Summary")
        print("5. Logout")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            amount = float(input("Enter expense amount: ").strip())
            category = input("Enter category: ").strip()
            description = input("Enter description: ").strip()
            tracker.add_expense(Expense(amount, category, description, user.user_id))
        elif choice == "2":
            tracker.list_expenses()
        elif choice == "3":
            period = input("Enter budget period (YYYY-MM): ").strip()
            amount = float(input("Enter budget amount: ").strip())
            tracker.set_budget(period, amount)
        elif choice == "4":
            tracker.view_summary()
        elif choice == "5":
            auth.logout()
            break

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
