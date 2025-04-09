import tkinter as tk
from tkinter import ttk, messagebox
from file_manager import load_data, save_data
from expenses import ExpenseTracker
import datetime
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BaseDashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # Top user menu
        top_bar = ttk.Frame(self)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

        user = self.controller.auth.get_current_user()
        user_menu = ttk.Menubutton(top_bar, text=f"\U0001F464 {user.username}")
        menu = tk.Menu(user_menu, tearoff=0)
        menu.add_command(label=f"Profile ({user.username})", command=self.show_profile)
        menu.add_command(label="Logout", command=self.logout)
        user_menu["menu"] = menu
        user_menu.pack(side="right", padx=10, pady=5)

        # Left navigation panel
        self.nav_frame = ttk.Frame(self)
        self.nav_frame.grid(row=1, column=0, sticky="ns")

        # Content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=1, sticky="nsew")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_profile(self):
        self.clear_content()
        ttk.Label(self.content_frame, text=f"User Profile - {self.controller.auth.get_current_user().username}",
                  font=("Segoe UI", 16)).pack(pady=20)

    def logout(self):
        self.controller.auth.logout()
        self.controller.show_frame(type(self.controller.frames[list(self.controller.frames.keys())[0]]))  # Redirect to HomePage

class AdminDashboard(BaseDashboard):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Button(self.nav_frame, text="Create Category", command=self.create_category).pack(pady=5, fill="x")
        ttk.Button(self.nav_frame, text="Delete Category", command=self.delete_category).pack(pady=5, fill="x")

        self.cat_name = ttk.Entry(self.content_frame)
        self.cat_name.pack(pady=10)
        self.cat_name.insert(0, "New Category Name")

        self.cat_list = ttk.Combobox(self.content_frame)
        self.cat_list.pack(pady=10)

        self.refresh_categories()

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

class UserDashboard(BaseDashboard):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        ttk.Button(self.nav_frame, text="Add Expense", command=self.add_expense).pack(pady=5, fill="x")
        ttk.Button(self.nav_frame, text="View Expenses", command=self.view_expenses).pack(pady=5, fill="x")
        ttk.Button(self.nav_frame, text="View Summary", command=self.view_summary).pack(pady=5, fill="x")
        ttk.Button(self.nav_frame, text="Set Budget", command=self.set_budget).pack(pady=5, fill="x")

    def add_expense(self):
        self.clear_content()
        user = self.controller.auth.get_current_user()
        data = load_data()
        categories = data.get("categories", {})
        cat_options = [(cid, cat["name"]) for cid, cat in categories.items()]

        ttk.Label(self.content_frame, text="Add Expense", font=("Segoe UI", 16)).pack(pady=10)

        ttk.Label(self.content_frame, text="Category").pack()
        category_var = tk.StringVar()
        cat_dropdown = ttk.Combobox(self.content_frame, textvariable=category_var)
        cat_dropdown["values"] = [f"{cid}: {name}" for cid, name in cat_options]
        cat_dropdown.pack(pady=5)

        ttk.Label(self.content_frame, text="Description").pack()
        desc_entry = ttk.Entry(self.content_frame)
        desc_entry.pack(pady=5)

        ttk.Label(self.content_frame, text="Amount").pack()
        amt_entry = ttk.Entry(self.content_frame)
        amt_entry.pack(pady=5)

        ttk.Label(self.content_frame, text="Date").pack()
        date_picker = DateEntry(self.content_frame, width=16, background="darkgreen", foreground="white", borderwidth=2, date_pattern='yyyy-mm-dd')
        date_picker.pack(pady=5)

        def submit_expense():
            try:
                selected = category_var.get()
                if ":" not in selected:
                    raise ValueError("Please select a valid category.")
                cat_id = int(selected.split(":")[0])
                cat_name = categories[str(cat_id)]["name"]

                desc = desc_entry.get().strip()
                if not desc:
                    raise ValueError("Description is required.")

                amount = float(amt_entry.get())
                if amount <= 0:
                    raise ValueError("Amount must be a positive number.")

                date = date_picker.get_date().strftime("%Y-%m-%d")

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
                self.add_expense()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add expense: {e}")

        ttk.Button(self.content_frame, text="Submit", style="Accent.TButton", command=submit_expense).pack(pady=10)

    def view_expenses(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        import datetime
        from tkcalendar import DateEntry

        user = self.controller.auth.get_current_user()
        data = load_data()
        full_expenses = data.get("expenses", {}).get(str(user.user_id), [])

        filter_frame = ttk.Frame(self.content_frame)
        filter_frame.pack(pady=10)

        ttk.Label(filter_frame, text="Month (YYYY-MM):").pack(side="left", padx=5)
        month_var = tk.StringVar()
        default_month = datetime.datetime.now().strftime("%Y-%m")
        month_entry = ttk.Entry(filter_frame, textvariable=month_var, width=10)
        month_var.set(default_month)
        month_entry.pack(side="left", padx=5)

        tree = ttk.Treeview(self.content_frame, columns=("Date", "Category", "Amount", "Description"), show="headings",
                            height=15)
        for col in ("Date", "Category", "Amount", "Description"):
            tree.heading(col, text=col)
            tree.column(col, width=140 if col != "Description" else 220)
        tree.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.97, rely=0.2, relheight=0.7)

        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=10)

        id_map = {}

        def populate_table(month):
            tree.delete(*tree.get_children())
            id_map.clear()
            for exp in full_expenses:
                if exp["date"].startswith(month):
                    tree_id = tree.insert("", "end", values=(
                    exp["date"], exp["category"], f"{exp['amount']:.2f}", exp["description"]))
                    id_map[tree_id] = exp["expense_id"]

        def filter_by_month():
            month = month_var.get().strip()
            if not month or len(month) != 7 or "-" not in month:
                messagebox.showerror("Invalid Input", "Enter a valid month in YYYY-MM format.")
                return
            populate_table(month)

        def delete_expense():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select Expense", "Please select an expense to delete.")
                return
            tree_id = selected[0]
            expense_id = id_map[tree_id]

            confirm = messagebox.askyesno("Confirm", "Delete this expense?")
            if not confirm:
                return

            data["expenses"][str(user.user_id)] = [
                exp for exp in data["expenses"][str(user.user_id)]
                if exp["expense_id"] != expense_id
            ]
            save_data(data)
            tree.delete(tree_id)
            messagebox.showinfo("Deleted", "Expense deleted successfully.")

        def edit_expense():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select Expense", "Please select an expense to edit.")
                return
            tree_id = selected[0]
            expense_id = id_map[tree_id]

            for exp in data["expenses"][str(user.user_id)]:
                if exp["expense_id"] == expense_id:
                    open_edit_window(exp, tree_id)
                    break

        def open_edit_window(expense, tree_id):
            ewin = tk.Toplevel(self)
            ewin.title("Edit Expense")
            ewin.geometry("400x400")
            ewin.configure(bg="#2e2e2e")

            ttk.Label(ewin, text="Edit Expense", font=("Segoe UI", 14)).pack(pady=10)

            categories = data.get("categories", {})
            category_var = tk.StringVar()
            cat_dropdown = ttk.Combobox(ewin, textvariable=category_var)
            cat_dropdown["values"] = [f"{cid}: {cat['name']}" for cid, cat in categories.items()]
            current_cat = next(
                (f"{cid}: {cat['name']}" for cid, cat in categories.items() if cat["name"] == expense["category"]), "")
            cat_dropdown.set(current_cat)
            cat_dropdown.pack(pady=5)

            ttk.Label(ewin, text="Description").pack()
            desc_entry = ttk.Entry(ewin)
            desc_entry.insert(0, expense["description"])
            desc_entry.pack(pady=5)

            ttk.Label(ewin, text="Amount").pack()
            amt_entry = ttk.Entry(ewin)
            amt_entry.insert(0, str(expense["amount"]))
            amt_entry.pack(pady=5)

            ttk.Label(ewin, text="Date").pack()
            date_picker = DateEntry(ewin, width=16, background="darkgreen", foreground="white", borderwidth=2,
                                    date_pattern='yyyy-mm-dd')
            date_picker.set_date(expense["date"])
            date_picker.pack(pady=5)

            def save_changes():
                try:
                    selected = category_var.get()
                    if ":" not in selected:
                        raise ValueError("Please select a valid category.")
                    cat_id = int(selected.split(":")[0])
                    cat_name = categories[str(cat_id)]["name"]

                    new_desc = desc_entry.get().strip()
                    new_amt = float(amt_entry.get().strip())
                    new_date = date_picker.get_date().strftime("%Y-%m-%d")

                    expense["category"] = cat_name
                    expense["description"] = new_desc
                    expense["amount"] = new_amt
                    expense["date"] = new_date
                    save_data(data)

                    tree.item(tree_id, values=(new_date, cat_name, f"{new_amt:.2f}", new_desc))
                    messagebox.showinfo("Success", "Expense updated.")
                    ewin.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not update expense: {e}")

            ttk.Button(ewin, text="Save Changes", style="Accent.TButton", command=save_changes).pack(pady=15)

        ttk.Button(button_frame, text="Filter", command=filter_by_month).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Edit Selected", command=edit_expense).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Delete Selected", command=delete_expense).pack(side="left", padx=10)

        populate_table(default_month)

    def view_summary(self):
        self.clear_content()
        user = self.controller.auth.get_current_user()
        data = load_data()
        expenses = data.get("expenses", {}).get(str(user.user_id), [])
        budget_data = data.get("budgets", {}).get(str(user.user_id), {})

        ttk.Label(self.content_frame, text="Monthly Summary", font=("Segoe UI", 16)).pack(pady=10)

        ttk.Label(self.content_frame, text="Select Month (YYYY-MM):").pack(pady=5)
        month_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m"))
        month_entry = ttk.Entry(self.content_frame, textvariable=month_var, width=10)
        month_entry.pack(pady=5)

        result_frame = ttk.Frame(self.content_frame)
        result_frame.pack(pady=10)

        def update_summary():
            for widget in result_frame.winfo_children():
                widget.destroy()

            current_month = month_var.get().strip()
            month_expenses = [e for e in expenses if e["date"].startswith(current_month)]
            total_spent = sum(e["amount"] for e in month_expenses)
            budget = budget_data.get(current_month)
            remaining = (budget - total_spent) if budget else None

            ttk.Label(result_frame, text=f"Total Expenses: ${total_spent:.2f}").pack()
            if budget is not None:
                ttk.Label(result_frame, text=f"Budget: ${budget:.2f}").pack()
                ttk.Label(result_frame, text=f"Remaining: ${remaining:.2f}").pack()
                if remaining < 0:
                    ttk.Label(result_frame, text="⚠️ Budget exceeded!", foreground="red").pack()
            else:
                ttk.Label(result_frame, text="No budget set for this month.", foreground="orange").pack()

            fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
            labels = ["Expenses", "Budget"]
            values = [total_spent, budget if budget is not None else 0]
            colors = ["#f54242", "#42f55a"]

            ax.bar(labels, values, color=colors)
            ax.set_title("Expenses vs Budget")
            ax.set_ylabel("Amount ($)")
            ax.grid(True, axis='y')

            canvas = FigureCanvasTkAgg(fig, master=result_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)

        ttk.Button(self.content_frame, text="Show Summary", style="Accent.TButton", command=update_summary).pack(
            pady=10)
        update_summary()

    def set_budget(self):
        self.clear_content()
        user = self.controller.auth.get_current_user()

        ttk.Label(self.content_frame, text="Set Monthly Budget", font=("Segoe UI", 14)).pack(pady=10)

        ttk.Label(self.content_frame, text="Month (YYYY-MM):").pack(pady=5)
        month_entry = ttk.Entry(self.content_frame)
        month_entry.insert(0, datetime.datetime.now().strftime("%Y-%m"))
        month_entry.pack()

        ttk.Label(self.content_frame, text="Budget Amount:").pack(pady=5)
        amount_entry = ttk.Entry(self.content_frame)
        amount_entry.pack()

        def submit_budget():
            try:
                month = month_entry.get().strip()
                amount = float(amount_entry.get().strip())
                if not month or amount <= 0:
                    raise ValueError("Invalid inputs.")

                data = load_data()
                if str(user.user_id) not in data["budgets"]:
                    data["budgets"][str(user.user_id)] = {}
                data["budgets"][str(user.user_id)][month] = amount
                save_data(data)

                messagebox.showinfo("Success", f"Budget set for {month}")
                self.set_budget()
            except Exception as e:
                messagebox.showerror("Error", f"Could not set budget: {e}")

        ttk.Button(self.content_frame, text="Save", style="Accent.TButton", command=submit_budget).pack(pady=15)
