# models.py - User, Expense, Category, Budget Classes
import itertools
import datetime

class User:
    _id_counter = itertools.count(1)
    def __init__(self, username: str, password: str, role="user", user_id=None):
        """Initializes a User object with unique IDs."""
        if user_id is None:
            self.user_id = next(User._id_counter)
        else:
            self.user_id = user_id
            User._id_counter = itertools.count(user_id + 1)
        self.username = username
        self.password = password
        self.role = role
    def __str__(self):
        return f"User(id={self.user_id}, username='{self.username}', role='{self.role}')"


class Expense:
    _id_counter = itertools.count(1)

    def __init__(self, amount: float, category: str, description: str, user_id: int, date: str = None, expense_id=None):
        """Initializes an Expense object."""
        self.expense_id = expense_id if expense_id is not None else next(Expense._id_counter)
        self.amount = amount
        self.category = category
        self.description = description
        self.user_id = user_id

        # If date is None, prompt the user for input instead of setting today's date automatically
        if date is None:
            while True:
                date_input = input("Enter Date (YYYY-MM-DD) or press Enter for today's date: ").strip()
                if not date_input:
                    self.date = datetime.datetime.now().strftime("%Y-%m-%d")
                    break
                try:
                    datetime.datetime.strptime(date_input, "%Y-%m-%d")  # Validate format
                    self.date = date_input
                    break
                except ValueError:
                    print("[!] Invalid date format. Please enter in YYYY-MM-DD format.")
        else:
            self.date = date

    def __str__(self):
        return f"{self.expense_id:<4}{self.date:<12}{self.category:<20}{self.amount:<10.2f}{self.description}"


class Category:
    _id_counter = itertools.count(1)
    def __init__(self, name: str, user_id: int, category_id=None):
        """Initializes a category assigned to a user."""
        self.category_id = category_id if category_id is not None else next(Category._id_counter)
        self.name = name
        self.user_id = user_id
    def __str__(self):
        return f"{self.category_id}: {self.name}"

class Budget:
    def __init__(self, user_id: int, period: str, amount: float):
        """Initializes a budget assigned to a user."""
        self.user_id = user_id
        self.period = period
        self.amount = amount
    def __str__(self):
        return f"Budget(user_id={self.user_id}, period={self.period}, amount={self.amount:.2f})"


