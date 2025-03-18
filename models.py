# models.py - Defines Data Models
import itertools
import datetime

# ----------------------------
# User Class
# ----------------------------
class User:
    _id_counter = itertools.count(1)  # Auto-incrementing ID for users

    def __init__(self, username: str, password: str, role="user", user_id=None):
        """
        Initializes a User object.
        If loading from file, uses the given user_id. Otherwise, assigns a new unique ID.
        """
        self.user_id = user_id if user_id is not None else next(User._id_counter)
        self.username = username
        self.password = password
        self.role = role

    def __str__(self):
        return f"User(id={self.user_id}, username='{self.username}', role='{self.role}')"


# ----------------------------
# Expense Class
# ----------------------------
class Expense:
    _id_counter = itertools.count(1)  # Auto-incrementing ID for expenses

    def __init__(self, amount: float, category: str, description: str, user_id: int, date: str = None, expense_id=None):
        """
        Initializes an Expense object.
        If loading from file, uses the given expense_id. Otherwise, assigns a new unique ID.
        """
        self.expense_id = expense_id if expense_id is not None else next(Expense._id_counter)
        self.amount = amount
        self.category = category
        self.description = description
        self.user_id = user_id
        self.date = date if date else datetime.datetime.now().strftime("%Y-%m-%d")  # Default to today's date

    def __str__(self):
        return f"{self.expense_id:<4}{self.date:<12}{self.category:<20}{self.amount:<10.2f}{self.description}"


# ----------------------------
# Category Class
# ----------------------------
class Category:
    _id_counter = itertools.count(1)  # Auto-incrementing ID for categories

    def __init__(self, name: str, category_id=None):
        """
        Initializes a Category object.
        If loading from file, uses the given category_id. Otherwise, assigns a new unique ID.
        """
        self.category_id = category_id if category_id is not None else next(Category._id_counter)
        self.name = name

    def __str__(self):
        return f"{self.category_id}: {self.name}"


# ----------------------------
# Budget Class
# ----------------------------
class Budget:
    def __init__(self, user_id: int, period: str, amount: float):
        """
        Initializes a Budget object.
        """
        self.user_id = user_id
        self.period = period  # Format: "YYYY-MM" for monthly, "YYYY-WW" for weekly
        self.amount = amount

    def __str__(self):
        return f"Budget(user_id={self.user_id}, period={self.period}, amount={self.amount:.2f})"
