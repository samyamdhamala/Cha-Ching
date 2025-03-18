# expenses.py - Manages Expenses & Budgets with File-Based Storage
import logging
import datetime  # 🔥 FIXED: Ensure datetime is imported globally
from file_manager import load_data, save_data
from models import Expense

class ExpenseTracker:
    def __init__(self, user):
        """Initializes expense tracking for a user."""
        self.user = user
        data = load_data()
        self.expenses = [Expense(**{k: v for k, v in exp.items() if k in Expense.__init__.__code__.co_varnames})
                         for exp in data["expenses"].get(str(user.user_id), [])]
        self.budgets = data["budgets"].get(str(user.user_id), {})

    def add_expense(self, expense: Expense = None):
        """Adds an expense either from user input or directly via an Expense object."""
        data = load_data()

        if expense is None:
            # ✅ Correct way to load category names
            categories = [cat["name"] for cat in data["categories"].values()]

            if not categories:
                print("[!] No categories available. Please ask the admin to create categories first.")
                return

            # Step 1: Select category
            print("\nAvailable Categories:")
            for i, cat in enumerate(categories, start=1):
                print(f"{i}. {cat}")
            try:
                category_index = int(input("Select category number: ").strip()) - 1
                category = categories[category_index]  # ✅ Now correctly refers to category names
            except (IndexError, ValueError):
                print("[!] Invalid category selection.")
                return

            # Step 2: Enter amount
            try:
                amount = float(input("Enter expense amount: ").strip())
            except ValueError:
                print("[!] Invalid amount. Please enter a numeric value.")
                return

            # Step 3: Enter description
            description = input("Enter description: ").strip()

            # Step 4: Enter Date (Ensuring the prompt always appears)
            date = None
            while date is None:
                date_input = input("Enter Date (YYYY-MM-DD) or press Enter for today's date: ").strip()
                if not date_input:
                    date = datetime.datetime.now().strftime("%Y-%m-%d")
                else:
                    try:
                        datetime.datetime.strptime(date_input, "%Y-%m-%d")  # Validate format
                        date = date_input
                    except ValueError:
                        print("[!] Invalid date format. Please enter in YYYY-MM-DD format.")

            # Create an Expense object with the correct category name
            expense = Expense(amount, category, description, self.user.user_id, date)

        # Save the new expense
        self.expenses.append(expense)
        if str(self.user.user_id) not in data["expenses"]:
            data["expenses"][str(self.user.user_id)] = []
        data["expenses"][str(self.user.user_id)].append(vars(expense))
        save_data(data)

        logging.info(f"Expense added for user '{self.user.username}': {vars(expense)}")
        print(f"[+] Expense added: {expense.date} {expense.category} {expense.amount:.2f} {expense.description}")

    def set_budget(self, period: str, amount: float):
        """Sets a budget for the user and saves it."""
        self.budgets[period] = amount

        data = load_data()
        if str(self.user.user_id) not in data["budgets"]:
            data["budgets"][str(self.user.user_id)] = {}
        data["budgets"][str(self.user.user_id)][period] = amount
        save_data(data)

        logging.info(f"Budget set for user '{self.user.username}' - {period}: {amount:.2f}")
        print(f"[+] Budget set for {period}: {amount:.2f}")

    def get_budget_for_period(self, period: str):
        """Retrieves the budget for a given period."""
        return self.budgets.get(period, None)

    def view_summary(self):
        """Displays the user's expense summary, including total expenses and remaining budget."""
        current_period = datetime.datetime.now().strftime("%Y-%m")
        total_expenses = sum(exp.amount for exp in self.expenses)
        budget = self.get_budget_for_period(current_period)

        print("\n------ Expense Summary ------")
        if budget is not None:
            print(f"Budget for {current_period}: {budget:.2f}")
            print(f"Total Expenses     : {total_expenses:.2f}")
            print(f"Remaining Budget   : {budget - total_expenses:.2f}")
            if total_expenses > budget:
                print("[!] Warning: You have exceeded your budget!")
            else:
                print("[i] You are within your budget.")
        else:
            print(f"[i] No budget set for {current_period}.")
            print(f"Total Expenses     : {total_expenses:.2f}")

        print("\nExpenses by Category:")
        category_totals = {}
        for exp in self.expenses:
            category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount
        for cat, amt in category_totals.items():
            print(f"  {cat:<20}: {amt:.2f}")

    def list_expenses(self):
        """Lists all expenses for the user."""
        if not self.expenses:
            print("[i] No expenses recorded yet.")
            return
        print("\n------ Expense List ------")
        for exp in self.expenses:
            print(f"{exp.date} - {exp.category}: {exp.amount:.2f} ({exp.description})")

class Expense:
    def __init__(self, amount: float, category: str, description: str, user_id: int, date: str = None):
        """Initializes an expense object with a user-inputted date, ensuring valid input."""
        self.date = date
        self.amount = amount
        self.category = category
        self.description = description
        self.user_id = user_id
