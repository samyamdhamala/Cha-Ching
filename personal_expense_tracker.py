import datetime
import itertools
import sys


# ----------------------------
# User Class
# ----------------------------
class User:
    _id_counter = itertools.count(1)  # Auto-incrementing ID for users

    def __init__(self, username: str, password: str):
        # Initialize a new user with a unique ID, username, and password
        self.user_id = next(User._id_counter)
        self.username = username
        self.password = password
        self.role = "user"  # Default role is "user"

    def __str__(self):
        # Return a human-readable string representation of the user
        return f"User(id={self.user_id}, username='{self.username}', role='{self.role}')"


# ----------------------------
# Expense Class
# ----------------------------
class Expense:
    _id_counter = itertools.count(1)  # Auto-incrementing ID for expenses

    def __init__(self, amount: float, category: str, description: str, date: str = None):
        # Initialize a new expense with a unique ID, amount, category, description, and date
        self.expense_id = next(Expense._id_counter)
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date if date else datetime.datetime.now().strftime("%Y-%m-%d")  # Default to today's date

    def __str__(self):
        # Return a formatted string for displaying the expense in a table-like format
        return f"{self.expense_id:<4}{self.date:<12}{self.category:<20}{self.amount:<10.2f}{self.description}"


# ----------------------------
# Category Class
# ----------------------------
class Category:
    _id_counter = itertools.count(1)  # Auto-incrementing ID for categories

    def __init__(self, name: str):
        # Initialize a new category with a unique ID and name
        self.category_id = next(Category._id_counter)
        self.name = name

    def __str__(self):
        # Return a human-readable string representation of the category
        return f"{self.category_id}: {self.name}"


# ----------------------------
# Budget Class
# ----------------------------
class Budget:
    def __init__(self, user_id: int, period: str, amount: float):
        # Initialize a new budget for a user, for a specific time period (e.g., "2023-10" for October 2023)
        self.user_id = user_id
        self.period = period  # Format: "YYYY-MM" for monthly, "YYYY-WW" for weekly
        self.amount = amount

    def __str__(self):
        # Return a human-readable string representation of the budget
        return f"Budget(user_id={self.user_id}, period={self.period}, amount={self.amount:.2f})"


# ----------------------------
# Authentication Class
# ----------------------------
class Authentication:
    def __init__(self):
        # Initialize the authentication system with an empty list of users and no current user
        self.users = []  # List to store all registered users
        self.current_user = None  # Track the currently logged-in user

    def register(self, username: str, password: str, role: str = "user"):
        # Register a new user if the username is unique
        if any(user.username == username for user in self.users):
            print("[!] Username already exists. Please choose a different username.")
            return None
        new_user = User(username, password)
        new_user.role = role
        self.users.append(new_user)  # Add the new user to the list
        print("[+] Registration successful:", new_user)
        return new_user

    def login(self, username: str, password: str) -> bool:
        # Log in a user if the username and password match
        for user in self.users:
            if user.username == username and user.password == password:
                self.current_user = user  # Set the current user
                print("[+] Login successful:", user)
                return True
        print("[!] Invalid username or password.")
        return False

    def logout(self):
        # Log out the current user
        if self.current_user:
            print(f"[-] User '{self.current_user.username}' logged out.")
        self.current_user = None  # Clear the current user

    def get_current_user(self):
        # Return the currently logged-in user
        return self.current_user


# ----------------------------
# ExpenseTracker Class
# ----------------------------
class ExpenseTracker:
    def __init__(self, user: User):
        # Initialize an expense tracker for a specific user
        self.user = user
        self.expenses = []  # List to store all expenses for the user
        self.budgets = []  # List to store budgets for the user

    def add_expense(self, expense: Expense):
        # Add a new expense to the user's expense list
        self.expenses.append(expense)
        print("[+] Expense added:", expense)

    def list_expenses(self):
        # Display all expenses in a table-like format
        if not self.expenses:
            print("[i] No expenses recorded.")
            return
        header = f"{'ID':<4}{'Date':<12}{'Category':<20}{'Amount':<10}{'Description'}"
        print(header)
        print("-" * len(header))
        for exp in self.expenses:
            print(exp)

    def get_total_expenses(self):
        # Calculate the total amount of all expenses
        return sum(exp.amount for exp in self.expenses)

    def get_expenses_by_category(self):
        # Summarize expenses by category
        summary = {}
        for exp in self.expenses:
            summary[exp.category] = summary.get(exp.category, 0) + exp.amount
        return summary

    def set_budget(self, period: str, amount: float):
        # Set or update a budget for a specific time period
        for budget in self.budgets:
            if budget.period == period:
                budget.amount = amount
                print("[+] Budget updated:", budget)
                return
        new_budget = Budget(self.user.user_id, period, amount)
        self.budgets.append(new_budget)
        print("[+] Budget set:", new_budget)

    def get_budget_for_period(self, period: str):
        # Get the budget for a specific time period
        for budget in self.budgets:
            if budget.period == period:
                return budget.amount
        return None  # No budget set for this period

    def view_summary(self):
        # Display a summary of the user's expenses and budget for the current period
        current_period = datetime.datetime.now().strftime("%Y-%m")  # Default to current month
        total = self.get_total_expenses()
        budget = self.get_budget_for_period(current_period)

        print("\n------ Expense Summary ------")
        if budget is not None:
            print(f"Budget for {current_period}: {budget:.2f}")
            print(f"Total Expenses     : {total:.2f}")
            print(f"Remaining Budget   : {budget - total:.2f}")
            if total > budget:
                print("[!] Warning: You have exceeded your budget!")
            else:
                print("[i] You are within your budget.")
        else:
            print(f"[i] No budget set for {current_period}.")
            print(f"Total Expenses     : {total:.2f}")

        print("\nExpenses by Category:")
        summary = self.get_expenses_by_category()
        if not summary:
            print("No expenses recorded.")
        else:
            for cat, amt in summary.items():
                print(f"  {cat:<20}: {amt:.2f}")


# ----------------------------
# ExpenseTrackerApp Class (Shell UI)
# ----------------------------
class ExpenseTrackerApp:
    def __init__(self):
        # Initialize the application with authentication, user trackers, and categories
        self.auth = Authentication()
        self.user_trackers = {}  # Map user IDs to their ExpenseTracker instances
        self.categories = []  # Global list of categories (created by admin)

        # Automatically create an admin account if it doesn't exist
        admin_exists = any(user.username == "admin" for user in self.auth.users)
        if not admin_exists:
            admin = self.auth.register("admin", "adminpass", role="admin")
            print("[i] Admin account created. Login with username 'admin' and password 'adminpass' to manage categories.")

    def run(self):
        # Main loop to run the application
        while True:
            if not self.auth.get_current_user():
                self.main_menu()  # Show the main menu if no user is logged in
            else:
                current_user = self.auth.get_current_user()
                if current_user.role == "admin":
                    self.admin_menu()  # Show the admin menu for admin users
                else:
                    self.user_menu()  # Show the user menu for regular users

    # ---- Main Menu ----
    def main_menu(self):
        # Display the main menu options
        print("\n" + "=" * 20)
        print("=== Main Menu ===")
        print("=" * 20)
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        print("-" * 20)
        choice = input("Enter choice: ").strip()
        if choice == "1":
            self.register_user()  # Register a new user
        elif choice == "2":
            self.login_user()  # Log in an existing user
        elif choice == "3":
            print("Exiting... Goodbye!")
            sys.exit(0)  # Exit the application
        else:
            print("[!] Invalid choice.")

    def register_user(self):
        # Handle user registration
        print("\n--- User Registration ---")
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        self.auth.register(username, password, role="user")

    def login_user(self):
        # Handle user login
        print("\n--- User Login ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        self.auth.login(username, password)

    # ---- Admin Menu ----
    def admin_menu(self):
        # Display the admin menu options
        print("\n" + "=" * 20)
        print(f"=== Admin Menu (Logged in as: {self.auth.get_current_user().username}) ===")
        print("=" * 20)
        print("1. Create Category")
        print("2. View Categories")
        print("3. Delete Category")
        print("4. Edit Category")
        print("5. Logout")
        print("-" * 20)
        choice = input("Enter choice: ").strip()
        if choice == "1":
            self.create_category()  # Create a new category
        elif choice == "2":
            self.view_categories()  # View all categories
        elif choice == "3":
            self.delete_category()  # Delete a category
        elif choice == "4":
            self.edit_category()  # Edit a category
        elif choice == "5":
            self.auth.logout()  # Log out the admin
        else:
            print("[!] Invalid choice.")

    def create_category(self):
        # Handle category creation
        name = input("Enter new category name: ").strip()
        if not name:
            print("[!] Category name cannot be empty.")
            return
        new_cat = Category(name)
        self.categories.append(new_cat)
        print("[+] Category created:", new_cat)

    def view_categories(self):
        # Display all available categories
        print("\n--- Available Categories ---")
        if not self.categories:
            print("[i] No categories available. Create some first!")
            return
        for cat in self.categories:
            print(cat)

    def delete_category(self):
        # Handle category deletion
        print("\n--- Delete Category ---")
        self.view_categories()
        cat_id = input("Enter category ID to delete: ").strip()
        for cat in self.categories:
            if str(cat.category_id) == cat_id:
                self.categories.remove(cat)
                print("[+] Category deleted.")
                return
        print("[!] Category not found.")

    def edit_category(self):
        # Handle category editing
        print("\n--- Edit Category ---")
        self.view_categories()
        cat_id = input("Enter category ID to edit: ").strip()
        for cat in self.categories:
            if str(cat.category_id) == cat_id:
                new_name = input("Enter new category name: ").strip()
                if not new_name:
                    print("[!] Category name cannot be empty.")
                    return
                cat.name = new_name
                print("[+] Category updated.")
                return
        print("[!] Category not found.")

    # ---- User Menu ----
    def user_menu(self):
        # Display the user menu options
        current_username = self.auth.get_current_user().username
        print("\n" + "=" * 20)
        print(f"=== User Menu (Logged in as: {current_username}) ===")
        print("=" * 20)
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Set Budget")
        print("4. View Summary")
        print("5. Logout")
        print("-" * 20)
        choice = input("Enter choice: ").strip()
        if choice == "1":
            self.add_expense()  # Add a new expense
        elif choice == "2":
            self.view_expenses()  # View all expenses
        elif choice == "3":
            self.set_budget()  # Set or update a budget
        elif choice == "4":
            self.view_summary()  # View expense summary
        elif choice == "5":
            self.auth.logout()  # Log out the user
        else:
            print("[!] Invalid choice.")

    def add_expense(self):
        # Handle adding a new expense
        current_user = self.auth.get_current_user()
        # Ensure an ExpenseTracker exists for the user
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
        if not description:
            print("[!] Description cannot be empty.")
            return

        date = input("Enter date (YYYY-MM-DD) [press enter for today]: ").strip()
        if not date:
            date = None

        expense = Expense(amount, selected_category, description, date)
        tracker.add_expense(expense)

    def view_expenses(self):
        # Display all expenses for the current user
        current_user = self.auth.get_current_user()
        if current_user.user_id not in self.user_trackers:
            print("[i] No expenses recorded yet.")
            return
        print("\n--- Your Expenses ---")
        tracker = self.user_trackers[current_user.user_id]
        tracker.list_expenses()

    def set_budget(self):
        # Handle setting or updating a budget
        current_user = self.auth.get_current_user()
        if current_user.user_id not in self.user_trackers:
            self.user_trackers[current_user.user_id] = ExpenseTracker(current_user)
        tracker = self.user_trackers[current_user.user_id]

        print("\n--- Set Budget ---")
        period = input("Enter budget period (YYYY-MM for monthly, YYYY-WW for weekly): ").strip()
        try:
            amount = float(input("Enter budget amount: ").strip())
        except ValueError:
            print("[!] Invalid amount.")
            return

        tracker.set_budget(period, amount)

    def view_summary(self):
        # Display the expense summary for the current user
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