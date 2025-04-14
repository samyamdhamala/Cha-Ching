import logging
from file_manager import load_data, save_data
from models import Expense
import itertools
import datetime
import re

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ExpenseTracker:
    expense_id_counter = itertools.count(1)  # Ensures unique expense IDs

    def __init__(self, user):
        """Initializes expense tracking for a user."""
        self.user = user
        data = load_data()
        user_expenses = data.get("expenses", {}).get(str(user.user_id), [])
        if user_expenses:
            max_existing_id = max(exp.get("expense_id", 0) for exp in user_expenses)
            ExpenseTracker.expense_id_counter = itertools.count(max_existing_id + 1)

    def add_expense(self):
        """Prompts the user to select a category and adds an expense."""
        data = load_data()
        categories = {int(k): v["name"] for k, v in
                      data.get("categories", {}).items()}  # Ensure category IDs are integers

        if not categories:
            print("[!] No categories available. Please ask the admin to create categories first.")
            return

        print("\nAvailable Categories:")
        for cat_id, cat_name in categories.items():
            print(f"{cat_id}: {cat_name}")

        while True:
            try:
                category_id = int(input("Select category ID: ").strip())
                if category_id not in categories:
                    raise ValueError("Invalid category ID.")
                category_name = categories[category_id]
                break
            except ValueError as e:
                logging.warning(f"Invalid category input: {e}")
                print("[!] Invalid category selection. Please enter a valid number.")

        while True:
            try:
                amount = float(input("Enter expense amount: ").strip())
                if amount <= 0:
                    raise ValueError("Amount must be a positive number.")
                break
            except ValueError as e:
                logging.warning(f"Invalid amount entered: {e}")
                print(f"[!] Invalid amount. Please enter a valid positive number.")

        while True:
            description = input("Enter description: ").strip()
            if not description:
                print("[!] Description cannot be empty.")
            else:
                break

        while True:
            date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if not date:
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                break
            elif re.match(r"^\d{4}-\d{2}-\d{2}$", date):  #date regex
                try:
                    datetime.datetime.strptime(date, "%Y-%m-%d")  # Validate actual date
                    break
                except ValueError:
                    print("[!] Invalid date. Please enter a valid date in YYYY-MM-DD format.")
            else:
                print("[!] Invalid date format. Please enter in YYYY-MM-DD format.")

        expense_id = next(ExpenseTracker.expense_id_counter)  # Assign unique ID
        expense = Expense(amount, category_name, description, self.user.user_id, date, expense_id)

        if str(self.user.user_id) not in data["expenses"]:
            data["expenses"][str(self.user.user_id)] = []
        data["expenses"][str(self.user.user_id)].append(vars(expense))
        save_data(data)

        logging.info(
            f"Expense added: {expense.amount}, {expense.category}, {expense.description}, {expense.date}, ID: {expense.expense_id} by user {self.user.user_id}."
        )
        print(f"[+] Expense added successfully with ID: {expense.expense_id}.")

    def list_expenses(self):
        """Lists all expenses for the user."""
        data = load_data()
        user_expenses = data["expenses"].get(str(self.user.user_id), [])
        if not user_expenses:
            print("[i] No expenses recorded yet.")
            return
        print("\n------ Expense List ------")
        for exp in user_expenses:
            print(
                f"ID: {exp['expense_id']} | {exp['date']} - {exp['category']}: {exp['amount']:.2f} ({exp['description']})")

    def view_summary(self):
        """Displays a summary of the user's expenses."""
        data = load_data()
        user_expenses = data["expenses"].get(str(self.user.user_id), [])
        total_expenses = sum(exp["amount"] for exp in user_expenses)
        budget_data = data.get("budgets", {}).get(str(self.user.user_id), {})
        current_month = datetime.datetime.now().strftime("%Y-%m")
        budget = budget_data.get(current_month, None)

        print("\n------ Expense Summary ------")
        print(f"Total Expenses: {total_expenses:.2f}")

        if budget is not None:
            print(f"Budget for {current_month}: {budget:.2f}")
            remaining_budget = budget - total_expenses
            print(f"Remaining Budget: {remaining_budget:.2f}")
            if total_expenses > budget:
                print("[!] Warning: You have exceeded your budget!")
            else:
                print("[i] You are within your budget.")
        else:
            print(f"[i] No budget set for {current_month}.")

        print("\nExpenses by Category:")
        category_totals = {}
        for exp in user_expenses:
            category_totals[exp["category"]] = category_totals.get(exp["category"], 0) + exp["amount"]
        for cat, amt in category_totals.items():
            print(f"  {cat:<20}: {amt:.2f}")

    def set_budget(self, period, amount):
        """Sets a budget for the user."""
        data = load_data()
        if str(self.user.user_id) not in data["budgets"]:
            data["budgets"][str(self.user.user_id)] = {}
        data["budgets"][str(self.user.user_id)][period] = amount
        save_data(data)
        logging.info(f"Budget set for {period}: {amount} by user {self.user.user_id}.")
        print(f"[+] Budget set for {period}: {amount:.2f}")

    def edit_expense(self):
        """Allows the user to edit an existing expense."""
        self.list_expenses()
        try:
            expense_id = int(input("Enter Expense ID to edit: "))
        except ValueError:
            print("[!] Invalid Expense ID.")
            return

        data = load_data()
        user_expenses = data["expenses"].get(str(self.user.user_id), [])
        for expense in user_expenses:
            if expense["expense_id"] == expense_id:
                try:
                    new_amount = float(input("Enter new amount: ").strip())
                    new_description = input("Enter new description: ").strip()
                    expense["amount"] = new_amount
                    expense["description"] = new_description
                    save_data(data)
                    print("[+] Expense updated successfully.")
                    return
                except ValueError:
                    print("[!] Invalid input.")
                    return
        print("[!] Expense ID not found.")

    def delete_expense(self):
        """Allows the user to delete an expense."""
        self.list_expenses()
        try:
            expense_id = int(input("Enter Expense ID to delete: "))
        except ValueError:
            print("[!] Invalid Expense ID.")
            return

        data = load_data()
        user_expenses = data["expenses"].get(str(self.user.user_id), [])
        updated_expenses = [exp for exp in user_expenses if exp["expense_id"] != expense_id]
        if len(updated_expenses) == len(user_expenses):
            print("[!] Expense ID not found.")
            return

        data["expenses"][str(self.user.user_id)] = updated_expenses
        save_data(data)
        print("[+] Expense deleted successfully.")
