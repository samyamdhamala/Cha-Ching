
import tkinter as tk
from tkinter import ttk, messagebox
from auth import Authentication
from expenses import ExpenseTracker
from file_manager import load_data, save_data

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cha-Ching $$")
        self.geometry("700x500")
        self.center_window()

        self.configure(bg="#2e2e2e")
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background="#2e2e2e")
        style.configure("TLabel", background="#2e2e2e", foreground="#eeeeee", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 11), padding=6)
        style.configure("Accent.TButton", background="#21c064", foreground="white")
        style.map("Accent.TButton",
                  background=[("active", "#1ba558"), ("pressed", "#188e4d")])

        self.auth = Authentication()
        self.current_tracker = None

        self.frames = {}
        for F in (HomePage, LoginPage, RegisterPage, AdminDashboard, UserDashboard):
            frame = F(self, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def center_window(self):
        self.update_idletasks()
        w, h = 700, 500
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def show_frame(self, frame):
        self.frames[frame].tkraise()

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Cha-Ching $$", font=("Segoe UI", 24)).pack(pady=40)
        ttk.Button(self, text="Login", style="Accent.TButton", command=lambda: controller.show_frame(LoginPage)).pack(pady=10)
        ttk.Button(self, text="Register", command=lambda: controller.show_frame(RegisterPage)).pack(pady=5)

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Login", font=("Segoe UI", 20)).pack(pady=20)
        self.username = ttk.Entry(self)
        self.username.pack(pady=5)
        self.username.insert(0, "Username")

        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5)
        self.password.insert(0, "Password")

        ttk.Button(self, text="Login", style="Accent.TButton", command=self.login).pack(pady=15)

    def login(self):
        user = self.username.get()
        pwd = self.password.get()
        if self.controller.auth.login(user, pwd):
            u = self.controller.auth.get_current_user()
            self.controller.current_tracker = ExpenseTracker(u)
            if u.role == "admin":
                self.controller.show_frame(AdminDashboard)
            else:
                self.controller.show_frame(UserDashboard)
        else:
            messagebox.showerror("Error", "Invalid login")

class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Register", font=("Segoe UI", 20)).pack(pady=20)
        self.username = ttk.Entry(self)
        self.username.pack(pady=5)
        self.username.insert(0, "Username")

        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5)
        self.password.insert(0, "Password")

        ttk.Button(self, text="Register", style="Accent.TButton", command=self.register).pack(pady=15)

    def register(self):
        user = self.username.get()
        pwd = self.password.get()
        if self.controller.auth.register(user, pwd):
            messagebox.showinfo("Success", "User registered")
            self.controller.show_frame(LoginPage)
        else:
            messagebox.showerror("Error", "Username already exists")

class AdminDashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Admin Dashboard", font=("Segoe UI", 18)).pack(pady=10)

        self.cat_name = ttk.Entry(self)
        self.cat_name.pack(pady=5)
        self.cat_name.insert(0, "New Category Name")

        ttk.Button(self, text="Create Category", command=self.create_category).pack(pady=5)
        ttk.Button(self, text="Delete Category", command=self.delete_category).pack(pady=5)

        self.cat_list = ttk.Combobox(self)
        self.cat_list.pack(pady=10)

        self.refresh_categories()
        ttk.Button(self, text="Logout", command=self.logout).pack(pady=20)

    def refresh_categories(self):
        data = load_data()
        cats = data.get("categories", {})
        items = [f"{k}: {v['name']}" for k, v in cats.items()]
        self.cat_list["values"] = items

    def create_category(self):
        name = self.cat_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Category name cannot be empty.")
            return
        data = load_data()
        new_id = max(map(int, data.get("categories", {}).keys()), default=0) + 1
        data["categories"][new_id] = {"name": name, "user_id": 1}
        save_data(data)
        messagebox.showinfo("Success", "Category created.")
        self.refresh_categories()

    def delete_category(self):
        selected = self.cat_list.get()
        if ":" not in selected:
            return
        cat_id = int(selected.split(":")[0])
        data = load_data()
        if cat_id in data["categories"]:
            del data["categories"][cat_id]
            save_data(data)
            messagebox.showinfo("Deleted", "Category deleted.")
            self.refresh_categories()

    def logout(self):
        self.controller.auth.logout()
        self.controller.show_frame(HomePage)

class UserDashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="User Dashboard", font=("Segoe UI", 18)).pack(pady=10)

        ttk.Button(self, text="Add Expense", command=self.add_expense).pack(pady=5)
        ttk.Button(self, text="View Expenses", command=self.view_expenses).pack(pady=5)
        ttk.Button(self, text="View Summary", command=self.view_summary).pack(pady=5)
        ttk.Button(self, text="Logout", command=self.logout).pack(pady=20)

    def view_summary(self):
        self.controller.current_tracker.view_summary()

    def view_expenses(self):
        user = self.controller.auth.get_current_user()
        data = load_data()
        expenses = data.get("expenses", {}).get(str(user.user_id), [])

        win = tk.Toplevel(self)
        win.title("All Expenses")
        win.geometry("650x400")
        win.configure(bg="#2e2e2e")

        ttk.Label(win, text="Your Expenses", font=("Segoe UI", 14)).pack(pady=10)

        cols = ("ID", "Date", "Category", "Amount", "Description")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120 if col != "Description" else 200)

        for exp in expenses:
            tree.insert("", "end", values=(
            exp["expense_id"], exp["date"], exp["category"], f"${exp['amount']:.2f}", exp["description"]))

        tree.pack(pady=10, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def logout(self):
        self.controller.auth.logout()
        self.controller.show_frame(HomePage)

    # This patch goes inside UserDashboard class as a new method

    def add_expense(self):
        user = self.controller.auth.get_current_user()
        data = load_data()
        categories = data.get("categories", {})
        cat_options = [(cid, cat["name"]) for cid, cat in categories.items()]

        win = tk.Toplevel(self)
        win.title("Add Expense")
        win.geometry("400x350")
        win.configure(bg="#2e2e2e")

        ttk.Label(win, text="Add Expense", font=("Segoe UI", 16)).pack(pady=10)

        ttk.Label(win, text="Category").pack()
        category_var = tk.StringVar()
        cat_dropdown = ttk.Combobox(win, textvariable=category_var)
        cat_dropdown["values"] = [f"{cid}: {name}" for cid, name in cat_options]
        cat_dropdown.pack(pady=5)

        ttk.Label(win, text="Description").pack()
        desc_entry = ttk.Entry(win)
        desc_entry.pack(pady=5)

        ttk.Label(win, text="Amount").pack()
        amt_entry = ttk.Entry(win)
        amt_entry.pack(pady=5)

        ttk.Label(win, text="Date (YYYY-MM-DD)").pack()
        date_entry = ttk.Entry(win)
        date_entry.insert(0, "YYYY-MM-DD")
        date_entry.pack(pady=5)

        def submit_expense():
            try:
                selected = category_var.get()
                if ":" not in selected:
                    raise ValueError("Invalid category selection")
                cat_id = int(selected.split(":")[0])
                cat_name = categories[str(cat_id)]["name"]

                amount = float(amt_entry.get())
                desc = desc_entry.get()
                date = date_entry.get()

                expense = {
                    "expense_id": next(ExpenseTracker.expense_id_counter),
                    "amount": amount,
                    "category": cat_name,
                    "description": desc,
                    "user_id": user.user_id,
                    "date": date
                }

                if str(user.user_id) not in data["expenses"]:
                    data["expenses"][str(user.user_id)] = []
                data["expenses"][str(user.user_id)].append(expense)
                save_data(data)

                messagebox.showinfo("Success", "Expense added successfully.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add expense: {e}")

        ttk.Button(win, text="Submit", style="Accent.TButton", command=submit_expense).pack(pady=10)




if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()
