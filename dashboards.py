import logging
import tkinter as tk
from tkinter import ttk, messagebox
from file_manager import load_data, save_data
from expenses import ExpenseTracker
import datetime
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from landing import build_landing_content



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
        menu.add_command(label=f"👤 Profile ({user.username})", command=self.show_profile)
        menu.add_command(label="🚪 Logout", command=self.logout)
        user_menu["menu"] = menu
        user_menu.pack(side="right", padx=10, pady=5)

        # Left navigation panel
        self.nav_frame = tk.Frame(self, bg="#1f1f2e", width=150)
        self.nav_frame.grid(row=1, column=0, sticky="ns")
        self.nav_frame.grid_propagate(False)

        # Content frame
        self.content_frame = ttk.Frame(self, width=800, height=600)
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        self.content_frame.grid_propagate(False)


    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_profile(self):
        self.load_landing()

    def logout(self):
        self.controller.auth.logout()
        self.controller.show_frame(type(self.controller.frames[list(self.controller.frames.keys())[0]]))  # Redirect to HomePage



class AdminDashboard(BaseDashboard):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.nav_actions = {}

        def create_nav_item(icon, text, command):
            full_text = f"{icon}  {text}"
            btn = tk.Label(self.nav_frame, text=full_text, bg="#1f1f2e", fg="white",
                           font=("Segoe UI", 11), anchor="w", padx=20)
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e: btn.config(bg="#333354"))
            btn.bind("<Leave>", lambda e: btn.config(bg="#1f1f2e"))
            btn.bind("<Button-1>", lambda e: command())
            return btn


        # ttk.Button(self.nav_frame, text="Create Category", command=self.create_category).pack(pady=5, fill="x")
        # ttk.Button(self.nav_frame, text="Delete Category", command=self.delete_category).pack(pady=5, fill="x")

        # create_nav_item("➕", "Create Category", self.create_category)
        # create_nav_item("🗑️", "Delete Category", self.delete_category)
        self.nav_actions["Categories"] = create_nav_item("📁", "Categories", self.manage_categories)


    def manage_categories(self):
        import logging
        logger = logging.getLogger(__name__)

        # Clear current content in the right-side frame
        self.clear_content()
        user = self.controller.auth.get_current_user()
        data = load_data()

        logger.info(f"[{user.username}] opened Category Management dashboard.")

        # Wrapper frame for the full category management UI
        wrapper = ttk.Frame(self.content_frame)
        wrapper.pack(fill="both", expand=True, padx=40, pady=30)
        wrapper.columnconfigure(0, weight=1)

        # Page heading
        ttk.Label(wrapper, text="📁 Manage Categories", font=("Segoe UI", 20, "bold")).grid(row=0, column=0,
                                                                                           pady=(0, 20), sticky="w")

        categories = data.get("categories", {})

        # --- Treeview Table for Categories ---
        table_frame = ttk.Frame(wrapper)
        table_frame.grid(row=1, column=0, sticky="nsew")

        columns = ("ID", "Name")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Category Name")
        tree.column("ID", width=80, anchor="center")
        tree.column("Name", width=250)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # --- Edit/Delete Buttons ---
        button_frame = ttk.Frame(wrapper)
        button_frame.grid(row=2, column=0, pady=(10, 0), sticky="w")

        def refresh_table():
            for row in tree.get_children():
                tree.delete(row)
            for cid in sorted(categories, key=int):
                cat = categories[cid]
                tree.insert("", "end", iid=cid, values=(cid, cat['name']))

        def on_edit():
            selected = tree.selection()
            if not selected:
                logger.warning(f"[{user.username}] attempted to edit without selecting a category.")
                messagebox.showwarning("Select", "Please select a category to edit.")
                return
            cid = selected[0]
            old_name = categories[cid]['name']

            # --- Edit Category Modal (Toplevel Window) ---
            edit_win = tk.Toplevel(self)
            edit_win.title("Edit Category")
            edit_win.geometry("320x180")
            edit_win.configure(bg="#2e2e2e")  # Match dark theme

            # Label for input
            ttk.Label(edit_win, text="Edit Category Name:", font=("Segoe UI", 12)).pack(pady=10)

            # Input field
            name_var = tk.StringVar(value=old_name)
            entry = ttk.Entry(edit_win, textvariable=name_var, font=("Segoe UI", 11), width=30)
            entry.pack(pady=5)

            # Save Button
            button_frame = ttk.Frame(edit_win)
            button_frame.pack(pady=15)

            def save():
                new_name = name_var.get().strip()
                if not new_name:
                    logger.warning(f"[{user.username}] attempted to rename category ID {cid} with an empty name.")
                    messagebox.showerror("Error", "Name cannot be empty.")
                    return
                if any(cat['name'].lower() == new_name.lower() for k, cat in categories.items() if k != cid):
                    logger.warning(
                        f"[{user.username}] attempted to rename category ID {cid} to a duplicate name: '{new_name}'")
                    messagebox.showerror("Error", "Category already exists.")
                    return

                # ✅ Rename in category list
                categories[cid]['name'] = new_name

                # 🔁 Update all expenses using the old category name
                for user_id, expenses_list in data.get("expenses", {}).items():
                    for exp in expenses_list:
                        if exp["category"] == old_name:
                            exp["category"] = new_name

                save_data(data)
                refresh_table()
                logger.info(
                    f"[{user.username}] renamed category '{old_name}' to '{new_name}' and updated matching expenses.")
                messagebox.showinfo("Updated", "Category updated successfully.")
                edit_win.destroy()

            ttk.Button(button_frame, text="💾 Save", style="Accent.TButton", command=save).pack()

        def on_delete():
            selected = tree.selection()
            if not selected:
                logger.warning(f"[{user.username}] attempted to delete without selecting a category.")
                messagebox.showwarning("Select", "Please select a category to delete.")
                return

            cid = selected[0]
            cat_name = categories[cid]["name"]

            # 🔍 Check if category is used in any expense
            used_in_expenses = any(
                exp["category"] == cat_name
                for user_exp in data.get("expenses", {}).values()
                for exp in user_exp
            )
            if used_in_expenses:
                logger.warning(f"[{user.username}] attempted to delete category '{cat_name}' that is in use.")
                messagebox.showerror("Blocked", f"Category '{cat_name}' is used in expenses and cannot be deleted.")
                return

            confirm = messagebox.askyesno("Confirm", f"Delete category '{cat_name}'?")
            if confirm:
                logger.info(f"[{user.username}] deleted category ID {cid}: '{cat_name}'")
                del categories[cid]
                save_data(data)
                refresh_table()
                messagebox.showinfo("Deleted", "Category deleted.")

        ttk.Button(button_frame, text="✏️ Edit", style="Accent.TButton", command=on_edit).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", style="Danger.TButton", command=on_delete).pack(side="left", padx=5)

        # --- Create New Category Form ---
        create_frame = ttk.Frame(wrapper)
        create_frame.grid(row=3, column=0, pady=(30, 0), sticky="w")

        ttk.Label(create_frame, text="➕ Create New Category:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="w")
        new_cat_var = tk.StringVar()
        new_cat_entry = ttk.Entry(create_frame, textvariable=new_cat_var, font=("Segoe UI", 11), width=30)
        new_cat_entry.grid(row=1, column=0, pady=(0, 5), sticky="w")

        def create_category():
            name = new_cat_var.get().strip()
            if not name:
                logger.warning(f"[{user.username}] attempted to create a category with empty name.")
                messagebox.showerror("Error", "Category name cannot be empty.")
                return
            if any(cat['name'].lower() == name.lower() for cat in categories.values()):
                logger.warning(f"[{user.username}] attempted to create duplicate category: '{name}'")
                messagebox.showerror("Error", "Category already exists.")
                return

            new_id = max(map(int, categories.keys()), default=0) + 1
            categories[str(new_id)] = {
                "category_id": new_id,
                "name": name,
                "user_id": user.user_id
            }
            save_data(data)
            categories.clear()
            categories.update(load_data().get("categories", {}))
            new_cat_var.set("")
            refresh_table()
            logger.info(f"[{user.username}] created new category ID {new_id}: '{name}'")
            messagebox.showinfo("Created", f"Category '{name}' created.")

        ttk.Button(create_frame, text="Create", style="Accent.TButton", command=create_category).grid(row=1, column=1,
                                                                                                      padx=10)

        refresh_table()



    def load_landing(self):
        self.clear_content()
        build_landing_content(self.content_frame, self.controller)

    def trigger_nav(self, name):
        if name in self.nav_actions:
            self.nav_actions[name].event_generate("<Button-1>")


class UserDashboard(BaseDashboard):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.active_nav_item = None  # Track currently selected nav label
        self.nav_actions = {}

        def create_nav_item(icon, text, command):
            full_text = f"{icon}  {text}"
            btn = tk.Label(self.nav_frame, text=full_text, bg="#1f1f2e", fg="white",
                           font=("Segoe UI", 11), anchor="w", padx=20)
            btn.pack(fill="x", pady=2)

            def on_click(event=None):
                if self.active_nav_item:
                    self.active_nav_item.config(bg="#1f1f2e")  # Reset old
                btn.config(bg="#44446b")  # Active color
                self.active_nav_item = btn
                command()

            btn.bind("<Enter>", lambda e: btn.config(bg="#333354") if self.active_nav_item != btn else None)
            btn.bind("<Leave>", lambda e: btn.config(bg="#1f1f2e") if self.active_nav_item != btn else None)
            btn.bind("<Button-1>", on_click)

            return btn

        self.nav_actions["Add Expense"] = create_nav_item("💸", "Add Expense", self.add_expense)
        self.nav_actions["View Expenses"] = create_nav_item("📋", "View Expenses", self.view_expenses)
        self.nav_actions["View Summary"] = create_nav_item("📊", "View Summary", self.view_summary)
        self.nav_actions["Set Budget"] = create_nav_item("💼", "Set Budget", self.set_budget)

        # Prevent the entire dashboard frame from shrinking
        self.config(width=1000, height=1000)
        self.grid_propagate(False)

    def add_expense(self):
        self.clear_content()
        user = self.controller.auth.get_current_user()
        data = load_data()
        categories = data.get("categories", {})
        cat_options = [(cid, cat["name"]) for cid, cat in categories.items()]

        wrapper = ttk.Frame(self.content_frame)
        wrapper.pack(fill="both", expand=True, padx=40, pady=30)
        wrapper.columnconfigure(0, weight=1)

        ttk.Label(wrapper, text="\U0001F4B0 Add New Expense", font=("Segoe UI", 20, "bold")).grid(row=0, column=0,
                                                                                                  pady=(0, 20))

        ttk.Label(wrapper, text="📂 Category", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
        category_var = tk.StringVar()
        cat_dropdown = ttk.Combobox(wrapper, textvariable=category_var, font=("Segoe UI", 11), width = 18)
        cat_dropdown["values"] = [f"{cid}: {name}" for cid, name in cat_options]
        cat_dropdown.grid(row=2, column=0, pady=(0, 15), sticky="ew")

        ttk.Label(wrapper, text="📝 Description", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="w")
        desc_entry = tk.Text(wrapper, height=4, font=("Segoe UI", 11), wrap="word")
        desc_entry.grid(row=4, column=0, pady=(0, 15), sticky="ew")

        ttk.Label(wrapper, text="💵 Amount", font=("Segoe UI", 12)).grid(row=5, column=0, sticky="w")
        amt_entry = ttk.Entry(wrapper, font=("Segoe UI", 11), width=50)
        amt_entry.grid(row=6, column=0, pady=(0, 15), sticky="ew")
        amt_entry.insert(0, "0.00")

        ttk.Label(wrapper, text="📅 Date", font=("Segoe UI", 12)).grid(row=7, column=0, sticky="w")
        date_picker = DateEntry(wrapper, width=18, background="darkgreen", foreground="white", borderwidth=2,
                                date_pattern='yyyy-mm-dd', font=("Segoe UI", 11))
        date_picker.grid(row=8, column=0, pady=(0, 20), sticky="w")

        def submit_expense():
            try:
                selected = category_var.get()
                if ":" not in selected:
                    raise ValueError("Please select a valid category.")
                cat_id = int(selected.split(":")[0])
                cat_name = categories[str(cat_id)]["name"]

                desc = desc_entry.get("1.0", "end").strip()
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

        def reset_form():
            category_var.set("")
            desc_entry.delete("1.0", "end")
            amt_entry.delete(0, "end")
            amt_entry.insert(0, "0.00")
            date_picker.set_date(datetime.datetime.now())

        button_frame = ttk.Frame(wrapper)
        button_frame.grid(row=9, column=0, pady=10, sticky="e")
        ttk.Button(button_frame, text="Reset", command=reset_form).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Submit", style="Accent.TButton", command=submit_expense).pack(side="left")

    def view_expenses(self):
        # Clear previous content in the main frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        import datetime
        from tkcalendar import DateEntry

        # Load user data
        user = self.controller.auth.get_current_user()
        data = load_data()
        full_expenses = data.get("expenses", {}).get(str(user.user_id), [])

        # --- HEADER ---
        header = ttk.Label(self.content_frame, text="📄 View & Manage Expenses", font=("Segoe UI", 16, "bold"))
        header.pack(pady=(10, 5))

        # --- FILTER FRAME ---
        filter_frame = ttk.LabelFrame(self.content_frame, text="📅 Filter by Month")
        filter_frame.pack(padx=15, pady=10, fill="x")

        # Set default month to current
        month_var = tk.StringVar()
        default_month = datetime.datetime.now().strftime("%Y-%m")
        month_var.set(default_month)

        # Month Entry
        ttk.Label(filter_frame, text="Month (YYYY-MM):").pack(side="left", padx=(10, 5), pady=10)
        month_entry = ttk.Entry(filter_frame, textvariable=month_var, width=10)
        month_entry.pack(side="left", padx=5, pady=10)

        # Filter + Export Buttons
        ttk.Button(filter_frame, text="Filter", style="Outlined.TButton", command=lambda: filter_by_month()).pack(
            side="left", padx=10)
        ttk.Button(filter_frame, text="📤 Export to CSV", command=lambda: export_to_csv(month_var.get())).pack(side="left",
                                                                                                            padx=5)

        # --- EXPENSE TABLE FRAME ---
        table_frame = ttk.Frame(self.content_frame)
        table_frame.pack(padx=15, pady=10, fill="both", expand=True)

        # Expense Table (Treeview)
        tree = ttk.Treeview(table_frame, columns=("Date", "Category", "Amount", "Description"), show="headings",
                            height=15)
        for col in ("Date", "Category", "Amount", "Description"):
            tree.heading(col, text=col)
            tree.column(col, width=140 if col != "Description" else 220)
        tree.pack(side="left", fill="both", expand=True)

        # Vertical scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # --- BUTTONS: Edit/Delete ---
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(pady=(5, 15))

        ttk.Button(button_frame, text="✏️ Edit Selected", style="Accent.TButton", command=lambda: edit_expense()).pack(
            side="left", padx=10)
        ttk.Button(button_frame, text="🗑️ Delete Selected", style="Danger.TButton", command=lambda: delete_expense()).pack(side="left", padx=10)

        # --- MAPPING TREEVIEW ITEMS TO EXPENSE IDs ---
        id_map = {}

        # Populate table with data for given month
        def populate_table(month):
            tree.delete(*tree.get_children())
            id_map.clear()
            for exp in full_expenses:
                if exp["date"].startswith(month):
                    tree_id = tree.insert("", "end", values=(
                    exp["date"], exp["category"], f"{exp['amount']:.2f}", exp["description"]))
                    id_map[tree_id] = exp["expense_id"]

        # Validates and applies filter
        def filter_by_month():
            month = month_var.get().strip()
            if not month or len(month) != 7 or "-" not in month:
                messagebox.showerror("Invalid Input", "Enter a valid month in YYYY-MM format.")
                return
            populate_table(month)

        # Exports filtered expenses to CSV
        def export_to_csv(month):
            filtered_expenses = [exp for exp in full_expenses if exp["date"].startswith(month)]
            if not filtered_expenses:
                messagebox.showinfo("No Data", "No expenses to export for the selected month.")
                return

            file_path = f"expenses_{user.username}_{month}.csv"
            try:
                with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Date", "Category", "Amount", "Description"])
                    for exp in filtered_expenses:
                        writer.writerow([exp["date"], exp["category"], f"{exp['amount']:.2f}", exp["description"]])
                messagebox.showinfo("Export Successful", f"Expenses exported to '{file_path}'")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Error: {e}")

        # Deletes selected expense
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
            data["expenses"][str(user.user_id)] = [exp for exp in data["expenses"][str(user.user_id)] if
                                                   exp["expense_id"] != expense_id]
            save_data(data)
            tree.delete(tree_id)
            messagebox.showinfo("Deleted", "Expense deleted successfully.")

        # Opens the edit window for selected expense
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

        # Opens popup form styled like 'add_expense' for editing
        def open_edit_window(expense, tree_id):
            ewin = tk.Toplevel(self)
            ewin.title("Edit Expense")
            ewin.geometry("450x480")
            ewin.configure(bg="#2e2e2e")
            ewin.grab_set()

            wrapper = ttk.Frame(ewin, padding=20)
            wrapper.pack(fill="both", expand=True)
            wrapper.columnconfigure(0, weight=1)

            # Header
            ttk.Label(wrapper, text="🛠️ Edit Expense", font=("Segoe UI", 18, "bold")).grid(row=0, column=0,
                                                                                           pady=(0, 20))

            categories = data.get("categories", {})
            category_var = tk.StringVar()
            cat_dropdown = ttk.Combobox(wrapper, textvariable=category_var, font=("Segoe UI", 11), width=18)
            cat_dropdown["values"] = [f"{cid}: {cat['name']}" for cid, cat in categories.items()]
            current_cat = next(
                (f"{cid}: {cat['name']}" for cid, cat in categories.items() if cat["name"] == expense["category"]), "")
            cat_dropdown.set(current_cat)
            ttk.Label(wrapper, text="📂 Category", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
            cat_dropdown.grid(row=2, column=0, pady=(0, 15), sticky="ew")

            # Description
            ttk.Label(wrapper, text="📝 Description", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="w")
            desc_entry = tk.Text(wrapper, height=4, font=("Segoe UI", 11), wrap="word")
            desc_entry.insert("1.0", expense["description"])
            desc_entry.grid(row=4, column=0, pady=(0, 15), sticky="ew")

            # Amount
            ttk.Label(wrapper, text="💵 Amount", font=("Segoe UI", 12)).grid(row=5, column=0, sticky="w")
            amt_entry = ttk.Entry(wrapper, font=("Segoe UI", 11), width=50)
            amt_entry.insert(0, str(expense["amount"]))
            amt_entry.grid(row=6, column=0, pady=(0, 15), sticky="ew")

            # Date
            ttk.Label(wrapper, text="📅 Date", font=("Segoe UI", 12)).grid(row=7, column=0, sticky="w")
            date_picker = DateEntry(wrapper, width=18, background="darkgreen", foreground="white", borderwidth=2,
                                    date_pattern='yyyy-mm-dd', font=("Segoe UI", 11))
            date_picker.set_date(expense["date"])
            date_picker.grid(row=8, column=0, pady=(0, 20), sticky="w")

            # Save Changes Button
            def save_changes():
                try:
                    selected = category_var.get()
                    if ":" not in selected:
                        raise ValueError("Please select a valid category.")
                    cat_id = int(selected.split(":")[0])
                    cat_name = categories[str(cat_id)]["name"]

                    new_desc = desc_entry.get("1.0", "end").strip()
                    if not new_desc:
                        raise ValueError("Description cannot be empty.")

                    new_amt = float(amt_entry.get().strip())
                    if new_amt <= 0:
                        raise ValueError("Amount must be greater than 0.")

                    new_date = date_picker.get_date().strftime("%Y-%m-%d")

                    # Update data
                    expense["category"] = cat_name
                    expense["description"] = new_desc
                    expense["amount"] = new_amt
                    expense["date"] = new_date
                    save_data(data)

                    # Update Treeview row
                    tree.item(tree_id, values=(new_date, cat_name, f"{new_amt:.2f}", new_desc))
                    messagebox.showinfo("Success", "Expense updated.")
                    ewin.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not update expense: {e}")

            # Save + Cancel Buttons
            button_frame = ttk.Frame(wrapper)
            button_frame.grid(row=9, column=0, pady=10, sticky="e")
            ttk.Button(button_frame, text="Cancel", command=ewin.destroy).pack(side="left", padx=(0, 10))
            ttk.Button(button_frame, text="Save Changes", style="Accent.TButton", command=save_changes).pack(
                side="left")

        # Initial population of table
        populate_table(default_month)

    def view_summary(self):
        self.clear_content()
        user = self.controller.auth.get_current_user()
        data = load_data()

        expenses = data.get("expenses", {}).get(str(user.user_id), [])
        budget_data = data.get("budgets", {}).get(str(user.user_id), {})

        self.fig1 = None
        self.fig2 = None
        self.chart_type = tk.StringVar(value="Both")

        # Grid config for flexible resizing
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        wrapper = ttk.Frame(self.content_frame)
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.grid_rowconfigure(3, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        ttk.Label(wrapper, text="\U0001F4CA Monthly Summary", font=("Segoe UI", 20, "bold")).grid(row=0, column=0,
                                                                                                  pady=15)

        # --- Month filter ---
        month_frame = ttk.Frame(wrapper)
        month_frame.grid(row=1, column=0, pady=5)

        ttk.Label(month_frame, text="Select Month (YYYY-MM):", font=("Segoe UI", 12)).pack(side="left", padx=(0, 10))
        month_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m"))
        ttk.Entry(month_frame, textvariable=month_var, width=10, font=("Segoe UI", 11)).pack(side="left", padx=(0, 10))
        ttk.Button(month_frame, text="Show Summary", style="Accent.TButton", command=lambda: update_summary()).pack(
            side="left", padx=(10, 0))

        # --- Chart dropdown + download ---
        chart_control = ttk.Frame(wrapper)
        chart_control.grid(row=2, column=0, sticky="n", pady=5)
        wrapper.grid_columnconfigure(0, weight=1)

        ttk.Label(chart_control, text="Chart Type:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=5)
        chart_selector = ttk.Combobox(chart_control, textvariable=self.chart_type, state="readonly",
                                      values=["Bar", "Pie", "Both"], width=10)
        chart_selector.grid(row=0, column=1, padx=5)
        chart_selector.bind("<<ComboboxSelected>>", lambda e: update_summary())

        def download_charts():
            username = user.username
            if self.chart_type.get().lower() in ["bar", "both"] and self.fig1:
                self.fig1.savefig(f"{username}_bar_chart.png")
            if self.chart_type.get().lower() in ["pie", "both"] and self.fig2:
                self.fig2.savefig(f"{username}_pie_chart.png")
            messagebox.showinfo("Saved", "Chart(s) saved to current directory.")


        ttk.Button(chart_control, text="📥 Download Chart(s)", style="Accent.TButton", command=download_charts).grid(
            row=0, column=2, padx=10)

        # --- Result frame ---
        result_frame = ttk.Frame(wrapper)
        result_frame.grid(row=3, column=0, sticky="nsew")
        result_frame.grid_rowconfigure(1, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        def update_summary():
            for widget in result_frame.winfo_children():
                widget.destroy()

            current_month = month_var.get().strip()
            month_expenses = [e for e in expenses if e["date"].startswith(current_month)]
            total_spent = sum(e["amount"] for e in month_expenses)
            budget = budget_data.get(current_month)
            remaining = (budget - total_spent) if budget else None

            summary = ttk.Frame(result_frame)
            summary.grid(row=0, column=0, pady=10)
            ttk.Label(summary, text=f"Total Expenses: ${total_spent:.2f}", font=("Segoe UI", 13, "bold"),
                      foreground="#f54242").pack()
            if budget is not None:
                ttk.Label(summary, text=f"Budget: ${budget:.2f}", font=("Segoe UI", 13, "bold"),
                          foreground="#42a1f5").pack()
                ttk.Label(summary, text=f"Remaining: ${remaining:.2f}", font=("Segoe UI", 13, "bold"),
                          foreground="#2ed573" if remaining >= 0 else "red").pack()
                if remaining < 0:
                    ttk.Label(summary, text="\u26A0\uFE0F Budget exceeded!", foreground="red",
                              font=("Segoe UI", 12, "bold")).pack()
            else:
                ttk.Label(summary, text="No budget set for this month.", foreground="orange",
                          font=("Segoe UI", 12)).pack()

            chart_frame = ttk.Frame(result_frame)
            chart_frame.grid(row=1, column=0, sticky="nsew", padx=10)
            chart_frame.grid_columnconfigure(0, weight=1)
            chart_frame.grid_columnconfigure(1, weight=1)
            chart_frame.grid_rowconfigure(0, weight=1)

            from collections import defaultdict
            category_totals = defaultdict(float)
            for e in month_expenses:
                category_totals[e["category"]] += e["amount"]

            chart_type = self.chart_type.get().lower()

            if chart_type in ["bar", "both"]:
                self.fig1, ax1 = plt.subplots(figsize=(6.5, 4.5), dpi=100)
                labels = ["Expenses", "Budget"]
                values = [total_spent, budget if budget else 0]
                bars = ax1.bar(labels, values, color=["#f54242", "#42a1f5"], width=0.4)
                ax1.set_ylim(0, max(max(values), 1) * 1.2)
                ax1.set_title("Expenses vs Budget", fontsize=14, fontweight="bold", pad=20)
                ax1.set_ylabel("Amount ($)", fontsize=12)
                ax1.grid(True, axis='y', linestyle='--', alpha=0.7)
                for bar in bars:
                    yval = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width() / 2, yval + 10, f"${yval:.2f}", ha='center', va='bottom',
                             fontsize=11, fontweight='bold')
                canvas1 = FigureCanvasTkAgg(self.fig1, master=chart_frame)
                canvas1.draw()
                canvas1.get_tk_widget().grid(row=0, column=0 if chart_type == "both" else 0, padx=20, pady=10,
                                             sticky="nsew")

            if chart_type in ["pie", "both"] and category_totals:
                self.fig2, ax2 = plt.subplots(figsize=(7.5, 5.5), dpi=100)
                pie_labels = list(category_totals.keys())
                pie_sizes = list(category_totals.values())
                total = sum(pie_sizes)
                pie_colors = ["#ff4d4d" if size / total >= 0.3 else "#a3d2ca" for size in pie_sizes]
                wedges, texts, autotexts = ax2.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=140,
                                                   colors=pie_colors, wedgeprops=dict(edgecolor='white'))
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                ax2.set_title("Expenses by Category", fontsize=14, fontweight="bold")
                canvas2 = FigureCanvasTkAgg(self.fig2, master=chart_frame)
                canvas2.draw()
                canvas2.get_tk_widget().grid(row=0, column=1 if chart_type == "both" else 0, padx=20, pady=10,
                                             sticky="nsew")

        update_summary()

    def set_budget(self):
        import datetime

        self.clear_content()
        user = self.controller.auth.get_current_user()

        # Wrapper frame for better spacing
        wrapper = ttk.Frame(self.content_frame)
        wrapper.pack(fill="both", expand=True, padx=40, pady=30)
        wrapper.columnconfigure(0, weight=1)

        # --- Title ---
        ttk.Label(wrapper, text="💼 Set Monthly Budget", font=("Segoe UI", 20, "bold")).grid(row=0, column=0,
                                                                                            pady=(0, 20))

        # --- Month Entry ---
        ttk.Label(wrapper, text="📅 Month (YYYY-MM):", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
        month_entry = ttk.Entry(wrapper, font=("Segoe UI", 11), width=20)
        month_entry.insert(0, datetime.datetime.now().strftime("%Y-%m"))
        month_entry.grid(row=2, column=0, pady=(0, 15), sticky="w")

        # --- Budget Amount Entry ---
        ttk.Label(wrapper, text="💵 Budget Amount:", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="w")
        amount_entry = ttk.Entry(wrapper, font=("Segoe UI", 11), width=20)
        amount_entry.grid(row=4, column=0, pady=(0, 20), sticky="w")

        # --- Save Budget Logic ---
        def submit_budget():
            try:
                month = month_entry.get().strip()
                amount = float(amount_entry.get().strip())

                if not month or len(month) != 7 or "-" not in month:
                    raise ValueError("Please enter a valid month in YYYY-MM format.")
                if amount <= 0:
                    raise ValueError("Budget must be a positive number.")

                data = load_data()
                if str(user.user_id) not in data["budgets"]:
                    data["budgets"][str(user.user_id)] = {}
                data["budgets"][str(user.user_id)][month] = amount
                save_data(data)

                messagebox.showinfo("Success", f"Budget of ${amount:.2f} set for {month}")
                self.set_budget()
            except Exception as e:
                messagebox.showerror("Error", f"Could not set budget: {e}")

        # --- Action Button ---
        ttk.Button(wrapper, text="💾 Save Budget", style="Accent.TButton", command=submit_budget).grid(
            row=5, column=0, sticky="e", pady=10
        )

    def load_landing(self):
        self.clear_content()
        build_landing_content(self.content_frame, self.controller)

    def trigger_nav(self, name):
        if name in self.nav_actions:
            self.nav_actions[name].event_generate("<Button-1>")

#