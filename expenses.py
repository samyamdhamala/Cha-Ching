# expenses.py - Manages Expenses & Budgets with File-Based Storage
import datetime
from file_manager import load_data, save_data
from models import Expense, Budget


class ExpenseTracker:
    def __init__(self, user):
        self.user = user
        data = load_data()

        # Ensure expenses are linked to users
        self.expenses = [
            Expense(**exp) for exp in data["expenses"] if "user_id" in exp and exp["user_id"] == user.user_id
        ]
        self.budgets = data["budgets"].get(str(user.user_id), {})

    def add_expense(self, expense):
        """Add a new expense and save it to the file."""
        expense.user_id = self.user.user_id  # Ensure user_id is set
        self.expenses.append(expense)

        # Save to file
        data = load_data()
        data["expenses"].append(vars(expense))  # Convert object to dictionary
        save_data(data)

        print("[+] Expense added:", expense)

    def list_expenses(self):
        """Display all expenses for the current user."""
        if not self.expenses:
            print("[i] No expenses recorded.")
            return
        print("\nID   Date        Category            Amount    Description")
        print("-" * 60)
        for exp in self.expenses:
            print(exp)

    def set_budget(self, period: str, amount: float):
        """Set a budget for the user and save it to the file."""
        self.budgets[period] = amount

        # Save budget to file
        data = load_data()
        data["budgets"][str(self.user.user_id)] = self.budgets
        save_data(data)

        print(f"[+] Budget set for {period}: {amount:.2f}")

    def get_budget_for_period(self, period: str):
        """Retrieve budget for a given period."""
        return self.budgets.get(period, None)

    def view_summary(self):
        """Display expense summary for the user."""
        current_period = datetime.datetime.now().strftime("%Y-%m")
        total = sum(exp.amount for exp in self.expenses)
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
        category_totals = {}
        for exp in self.expenses:
            category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount
        for cat, amt in category_totals.items():
            print(f"  {cat:<20}: {amt:.2f}")
