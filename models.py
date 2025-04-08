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

#
# # === Data File Initialization ===
# DATA_FILE = "data.json"
# if not os.path.exists(DATA_FILE):
#     with open(DATA_FILE, "w") as f:
#         json.dump({"users": [], "expenses": {}, "categories": {}, "budgets": {}}, f)
#
# # === File Manager ===
# def load_data():
#     try:
#         with open(DATA_FILE, "r") as f:
#             return json.load(f)
#     except Exception as e:
#         logging.error(f"Error loading data: {e}")
#         return {"users": [], "expenses": {}, "categories": {}, "budgets": {}}
#
# def save_data(data):
#     try:
#         with open(DATA_FILE, "w") as f:
#             json.dump(data, f, indent=4)
#         logging.info("Data saved successfully.")
#     except Exception as e:
#         logging.error(f"Error saving data: {e}")
#
# def hash_password(password):
#     return sha256(password.encode()).hexdigest()
#
# def verify_password(stored_password, input_password):
#     return stored_password == hash_password(input_password)
#
# # === Models ===
# class User:
#     _id_counter = itertools.count(1)
#     def __init__(self, username: str, password: str, role="user", user_id=None):
#         if user_id is None:
#             self.user_id = next(User._id_counter)
#         else:
#             self.user_id = user_id
#             User._id_counter = itertools.count(user_id + 1)
#         self.username = username
#         self.password = password
#         self.role = role
#     def __str__(self):
#         return f"User(id={self.user_id}, username='{self.username}', role='{self.role}')"
#
# class Expense:
#     _id_counter = itertools.count(1)
#     def __init__(self, amount, category, description, user_id, date=None, expense_id=None):
#         self.expense_id = expense_id if expense_id is not None else next(Expense._id_counter)
#         self.amount = amount
#         self.category = category
#         self.description = description
#         self.user_id = user_id
#         if date is None:
#             self.date = datetime.datetime.now().strftime("%Y-%m-%d")
#         else:
#             self.date = date
#     def __str__(self):
#         return f"{self.expense_id:<4}{self.date:<12}{self.category:<20}{self.amount:<10.2f}{self.description}"
#
# class Category:
#     _id_counter = itertools.count(1)
#     def __init__(self, name, user_id, category_id=None):
#         self.category_id = category_id if category_id is not None else next(Category._id_counter)
#         self.name = name
#         self.user_id = user_id
#     def __str__(self):
#         return f"{self.category_id}: {self.name}"
#
# class Budget:
#     def __init__(self, user_id, period, amount):
#         self.user_id = user_id
#         self.period = period
#         self.amount = amount
#     def __str__(self):
#         return f"Budget(user_id={self.user_id}, period={self.period}, amount={self.amount:.2f})"
#
# # === Authentication ===
# class Authentication:
#     def __init__(self):
#         data = load_data()
#         self.users = [User(**user) for user in data["users"]]
#         if self.users:
#             max_id = max(user.user_id for user in self.users)
#             User._id_counter = itertools.count(max_id + 1)
#         self.current_user = None
#
#     def register(self, username, password, role="user"):
#         if any(user.username == username for user in self.users):
#             logging.warning(f"Registration failed: Username '{username}' already exists.")
#             print("[!] Username already exists. Choose another one.")
#             return None
#         new_user = User(username, hash_password(password), role)
#         self.users.append(new_user)
#         data = load_data()
#         data["users"].append(vars(new_user))
#         save_data(data)
#         logging.info(f"User '{username}' registered successfully.")
#         print("[+] Registration successful:", new_user)
#         return new_user
#
#     def login(self, username, password):
#         for user in self.users:
#             if user.username == username and verify_password(user.password, password):
#                 self.current_user = user
#                 logging.info(f"User '{username}' logged in successfully.")
#                 print("[+] Login successful:", user)
#                 return True
#         logging.warning(f"Failed login attempt for username '{username}'")
#         print("[!] Invalid username or password.")
#         return False
#
#     def logout(self):
#         if self.current_user:
#             logging.info(f"User '{self.current_user.username}' logged out.")
#             print(f"[-] User '{self.current_user.username}' logged out.")
#         self.current_user = None
#
#     def get_current_user(self):
#         return self.current_user
