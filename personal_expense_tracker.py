import datetime
import itertools
import sys


# ----------------------------
# User Class
# ----------------------------
class User:
    _id_counter = itertools.count(1)

    def __init__(self, username: str, password: str, budget: float):
        self.user_id = next(User._id_counter)
        self.username = username
        self.password = password
        self.budget = budget
        self.role = "user"  # default role

    def __str__(self):
        return (f"User(id={self.user_id}, username='{self.username}', "
                f"budget={self.budget}, role='{self.role}')")


# ----------------------------
# Expense Class
# ----------------------------
class Expense:
    _id_counter = itertools.count(1)

    def __init__(self, amount: float, category: str, description: str, date: str = None):
        self.expense_id = next(Expense._id_counter)
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date if date else datetime.datetime.now().strftime("%Y-%m-%d")

    def __str__(self):
        # Format the expense in a tabular row format.
        return f"{self.expense_id:<4}{self.date:<12}{self.category:<20}{self.amount:<10.2f}{self.description}"


# ----------------------------
# Category Class
# ----------------------------
class Category:
    _id_counter = itertools.count(1)

    def __init__(self, name: str):
        self.category_id = next(Category._id_counter)
        self.name = name

    def __str__(self):
        return f"{self.category_id}: {self.name}"


# ----------------------------
# Authentication Class
# ----------------------------
class Authentication:
    def __init__(self):
        self.users = {}  # keyed by username
        self.current_user = None

    def register(self, username: str, password: str, budget: float, role: str = "user"):
        if username in self.users:
            print("[!] Username already exists.")
            return None
        new_user = User(username, password, budget)
        new_user.role = role
        self.users[username] = new_user
        print("[+] Registration successful:", new_user)
        return new_user

    def login(self, username: str, password: str) -> bool:
        user = self.users.get(username)
        if user and user.password == password:
            self.current_user = user
            print("[+] Login successful:", user)
            return True
        else:
            print("[!] Invalid username or password.")
            return False

    def logout(self):
        if self.current_user:
            print(f"[-] User '{self.current_user.username}' logged out.")
        self.current_user = None

    def get_current_user(self):
        return self.current_user


# ----------------------------
# ExpenseTracker Class
# ----------------------------
class ExpenseTracker:
    def __init__(self, user: User):
        self.user = user
        self.expenses = []  # list of Expense objects

    def add_expense(self, expense: Expense):
        self.expenses.append(expense)
        print("[+] Expense added:", expense)

    def list_expenses(self):
        if not self.expenses:
            print("[i] No expenses recorded.")
            return
        header = f"{'ID':<4}{'Date':<12}{'Category':<20}{'Amount':<10}{'Description'}"
        print(header)
        print("-" * len(header))
        for exp in self.expenses:
            print(exp)

    def get_total_expenses(self):
        return sum(exp.amount for exp in self.expenses)

    def get_expenses_by_category(self):
        summary = {}
        for exp in self.expenses:
            summary[exp.category] = summary.get(exp.category, 0) + exp.amount
        return summary

    def view_summary(self):
        total = self.get_total_expenses()
        print("\n------ Expense Summary ------")
        print(f"Monthly Budget     : {self.user.budget:.2f}")
        print(f"Total Expenses     : {total:.2f}")
        print(f"Remaining Budget   : {self.user.budget - total:.2f}")
        print("\nExpenses by Category:")
        summary = self.get_expenses_by_category()
        if not summary:
            print("No expenses recorded.")
        else:
            for cat, amt in summary.items():
                print(f"  {cat:<20}: {amt:.2f}")
        if total > self.user.budget:
            print("[!] Warning: You have exceeded your monthly budget!")
        else:
            print("[i] You are within your budget.")


# ----------------------------
# ExpenseTrackerApp Class (Shell UI)
# ----------------------------
class ExpenseTrackerApp:
    def __init__(self):
        self.auth = Authentication()
        self.user_trackers = {}  # mapping: user_id -> ExpenseTracker
        self.categories = []  # global list of categories (created by admin)

        # Automatically create an admin account.
        admin = self.auth.register("admin", "adminpass", budget=0, role="admin")
        print("[i] Admin account created. Login with username 'admin' and password 'adminpass' to manage categories.")

    def run(self):
        while True:
            if not self.auth.get_current_user():
                self.main_menu()
            else:
                current_user = self.auth.get_current_user()
                if current_user.role == "admin":
                    self.admin_menu()
                else:
                    self.user_menu()

    # ---- Main Menu ----
    def main_menu(self):
        print("\n=== Main Menu ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            self.register_user()
        elif choice == "2":
            self.login_user()
        elif choice == "3":
            print("Exiting... Goodbye!")
            sys.exit(0)
        else:
            print("[!] Invalid choice.")

    def register_user(self):
        print("\n--- User Registration ---")
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        try:
            budget = float(input("Enter monthly budget: ").strip())
        except ValueError:
            print("[!] Invalid budget value.")
            return
        self.auth.register(username, password, budget, role="user")

    def login_user(self):
        print("\n--- User Login ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        self.auth.login(username, password)

    # ---- Admin Menu ----
    def admin_menu(self):
        print(f"\n=== Admin Menu (Logged in as: {self.auth.get_current_user().username}) ===")
        print("1. Create Category")
        print("2. View Categories")
        print("3. Logout")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            self.create_category()
        elif choice == "2":
            self.view_categories()
        elif choice == "3":
            self.auth.logout()
        else:
            print("[!] Invalid choice.")

    def create_category(self):
        name = input("Enter new category name: ").strip()
        if not name:
            print("[!] Category name cannot be empty.")
            return
        new_cat = Category(name)
        self.categories.append(new_cat)
        print("[+] Category created:", new_cat)

    def view_categories(self):
        print("\n--- Available Categories ---")
        if not self.categories:
            print("[i] No categories available. Create some first!")
            return
        for cat in self.categories:
            print(cat)

    # ---- User Menu ----
    def user_menu(self):
        current_username = self.auth.get_current_user().username
        print(f"\n=== User Menu (Logged in as: {current_username}) ===")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. View Summary")
        print("4. Logout")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            self.add_expense()
        elif choice == "2":
            self.view_expenses()
        elif choice == "3":
            self.view_summary()
        elif choice == "4":
            self.auth.logout()
        else:
            print("[!] Invalid choice.")

    def add_expense(self):
        current_user = self.auth.get_current_user()
        # Ensure an ExpenseTracker exists for the user.
        if current_user.user_id not in self.user_trackers:
            self.user_trackers[current_user.user_id] = ExpenseTracker(current_user)
        tracker = self.user_trackers[current_user.user_id]

        print("\n--- Add Expense ---")
        try:
            amount = float(input("Enter expense amount: ").strip())
        except ValueError:
            print("[!] Invalid amount.")
            return

        if not self.categories:
            print("[i] No categories available. Please ask the admin to create categories first.")
            return

        print("\nSelect a category from the list:")
        for cat in self.categories:
            print(cat)
        cat_id = input("Enter category id: ").strip()
        selected_category = None
        for cat in self.categories:
            if str(cat.category_id) == cat_id:
                selected_category = cat.name
                break
        if not selected_category:
            print("[!] Invalid category selection.")
            return

        description = input("Enter expense description: ").strip()
        date = input("Enter date (YYYY-MM-DD) [press enter for today]: ").strip()
        if not date:
            date = None

        expense = Expense(amount, selected_category, description, date)
        tracker.add_expense(expense)

    def view_expenses(self):
        current_user = self.auth.get_current_user()
        if current_user.user_id not in self.user_trackers:
            print("[i] No expenses recorded yet.")
            return
        print("\n--- Your Expenses ---")
        tracker = self.user_trackers[current_user.user_id]
        tracker.list_expenses()

    def view_summary(self):
        current_user = self.auth.get_current_user()
        if current_user.user_id not in self.user_trackers:
            print("[i] No expenses recorded yet.")
            return
        tracker = self.user_trackers[current_user.user_id]
        tracker.view_summary()


# ----------------------------
# Run the Application
# ----------------------------
if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.run()
