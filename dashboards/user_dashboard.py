import tkinter as tk
import os
from tkinter import ttk, messagebox, filedialog
import datetime
import logging
import csv
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.cm import get_cmap
from core.file_manager import load_data, save_data
from core.expenses import ExpenseTracker
from ui.landing import build_landing_content
from dashboards.base_dashboard import BaseDashboard

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

class UserDashboard(BaseDashboard):
    """
    Provides the main dashboard interface for regular users. Users can:
    - Add new expenses
    - View and filter expense history
    - Edit or delete existing records
    - Visualize monthly summaries with bar and pie charts
    - Set monthly budget limits
    """

    def __init__(self, parent, controller):
        """
               Initializes the dashboard layout and navigation menu.
               Sets up sidebar options and tracks selected state.
               """

        super().__init__(parent, controller)
        self.active_nav_item = None  # Track currently selected nav label
        self.nav_actions = {}

        def create_nav_item(icon, text, command):
            """Creates a styled navigation button for the sidebar."""

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

        # Sidebar navigation items
        self.nav_actions["Add Expense"] = create_nav_item("💸", "Add Expense", self.add_expense)
        self.nav_actions["View Expenses"] = create_nav_item("📋", "View Expenses", self.view_expenses)
        self.nav_actions["Set Budget"] = create_nav_item("💼", "Set Budget", self.set_budget)
        self.nav_actions["View Summary"] = create_nav_item("📊", "View Summary", self.view_summary)
        self.nav_actions["Spending Trend"] = create_nav_item("📈", "Spending Trend", self.view_spending_trend)

        # Prevent the entire dashboard frame from shrinking
        self.config(width=1000, height=1000)
        self.grid_propagate(False)

    def add_expense(self):
        """
        Displays a form for the user to input a new expense, including:
        - Dropdown for selecting category
        - Text area for description
         - Entry for amount
        - Date picker for date
        - On submit, validates data and saves the expense.
        """
        self.clear_content()
        user = self.controller.auth.get_current_user()
        data = load_data()
        categories = data.get("categories", {})
        cat_options = [(cid, cat["name"]) for cid, cat in categories.items()]

        # Layout wrapper
        wrapper = ttk.Frame(self.content_frame)
        wrapper.pack(fill="both", expand=True, padx=40, pady=30)
        wrapper.columnconfigure(0, weight=1)

        ttk.Label(wrapper, text="\U0001F4B0 Add New Expense", font=("Segoe UI", 20, "bold")).grid(row=0, column=0,
                                                                                                  pady=(0, 20))
        # Category dropdown
        ttk.Label(wrapper, text="📂 Category", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
        category_var = tk.StringVar()
        cat_dropdown = ttk.Combobox(wrapper, textvariable=category_var, font=("Segoe UI", 11), width = 18, state="readonly")
        cat_dropdown["values"] = [f"{cid}: {name}" for cid, name in cat_options]
        cat_dropdown.grid(row=2, column=0, pady=(0, 15), sticky="ew")

        # Description field
        ttk.Label(wrapper, text="📝 Description", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="w")
        desc_entry = tk.Text(wrapper, height=4, font=("Segoe UI", 11), wrap="word")
        desc_entry.grid(row=4, column=0, pady=(0, 15), sticky="ew")

        # Amount field
        ttk.Label(wrapper, text="💵 Amount", font=("Segoe UI", 12)).grid(row=5, column=0, sticky="w")
        amt_entry = ttk.Entry(wrapper, font=("Segoe UI", 11), width=50)
        amt_entry.grid(row=6, column=0, pady=(0, 15), sticky="ew")
        amt_entry.insert(0, "0.00")

        # Date picker
        ttk.Label(wrapper, text="📅 Date", font=("Segoe UI", 12)).grid(row=7, column=0, sticky="w")
        date_picker = DateEntry(wrapper, width=18, background="darkgreen", foreground="white", borderwidth=2,
                                date_pattern='yyyy-mm-dd', font=("Segoe UI", 11))
        date_picker.grid(row=8, column=0, pady=(0, 20), sticky="w")

        # Handle submission
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
                logging.info(f"[User {user.user_id}] added expense: {amount:.2f}, {cat_name}, {desc[:30]}, {date}")
                messagebox.showinfo("Success", "Expense added successfully.")
                self.add_expense()
            except Exception as e:
                logging.error(f"[User {user.user_id}] failed to add expense: {e}")
                messagebox.showerror("Error", f"Failed to add expense. Please enter a valid amount.")

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

        # Filter + Import + Export Buttons
        ttk.Button(filter_frame, text="Filter", style="Outlined.TButton", command=lambda: filter_by_month()).pack(
            side="left", padx=10)
        ttk.Button(filter_frame, text="📥 Import Expenses", style="Outlined.TButton",  command=self.import_expenses_from_csv).pack(
            side="left", padx=5)
        ttk.Button(filter_frame, text="📤 Export to CSV", style="Outlined.TButton", command=lambda: export_to_csv(month_var.get())).pack(
            side="left", padx=5)


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
            logging.info(f"[User {user.user_id}] viewed summary for month: {month}")
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

            file_path = os.path.join(DATA_DIR, f"expenses_{user.username}_{month}.csv")
            try:
                with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Date", "Category", "Amount", "Description"])
                    for exp in filtered_expenses:
                        writer.writerow([exp["date"], exp["category"], f"{exp['amount']:.2f}", exp["description"]])
                messagebox.showinfo("Export Successful", f"Expenses exported to '{file_path}'")
                logging.info(f"[User {user.user_id}] exported expenses to CSV for month: {month}")

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
            logging.info(f"[User {user.user_id}] deleted expense ID {expense_id}")

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
                    logging.info(f"[User {user.user_id}] edited expense ID {expense['expense_id']}")
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
            saved_paths = []

            if self.chart_type.get().lower() in ["bar", "both"] and self.fig1:
                bar_path = os.path.join(DATA_DIR, f"{username}_bar_chart.png")
                self.fig1.savefig(bar_path)
                saved_paths.append(bar_path)

            if self.chart_type.get().lower() in ["pie", "both"] and self.fig2:
                pie_path = os.path.join(DATA_DIR, f"{username}_pie_chart.png")
                self.fig2.savefig(pie_path)
                saved_paths.append(pie_path)

            if saved_paths:
                file_list = "\n".join(saved_paths)
                messagebox.showinfo("Saved", f"Chart(s) saved to:\n{file_list}")
                logging.info(f"[User {user.user_id}] downloaded chart(s): {self.chart_type.get().lower()}")

        ttk.Button(chart_control, text="📥 Download Chart(s)", style="Accent.TButton", command=download_charts).grid(
            row=0, column=2, padx=10)

        # --- Result frame ---
        result_frame = ttk.Frame(wrapper)
        result_frame.grid(row=3, column=0, sticky="nsew")
        result_frame.grid_rowconfigure(1, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        def update_summary():
            # Close previous figures
            if self.fig1:
                plt.close(self.fig1)
            if self.fig2:
                plt.close(self.fig2)

            for widget in result_frame.winfo_children():
                widget.destroy()

            current_month = month_var.get().strip()
            logging.info(f"[User {user.user_id}] viewed summary for month: {current_month}")
            month_expenses = [e for e in expenses if e["date"].startswith(current_month)]
            total_spent = sum(e["amount"] for e in month_expenses)
            budget = budget_data.get(current_month)
            remaining = (budget - total_spent) if budget else None

            # --- Summary Section ---
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

            # --- Chart Frame ---
            chart_frame = ttk.Frame(result_frame)
            chart_frame.grid(row=1, column=0, sticky="nsew", padx=10)
            chart_frame.grid_propagate(False)
            chart_frame.config(width=1100, height=500)
            chart_frame.grid_columnconfigure(0, weight=1)
            chart_frame.grid_columnconfigure(1, weight=2)
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

                canvas_wrapper = ttk.Frame(chart_frame)
                canvas_wrapper.grid(row=0, column=0, sticky="nsew")
                canvas_wrapper.grid_propagate(False)
                canvas_wrapper.config(width=500, height=450)

                canvas1 = FigureCanvasTkAgg(self.fig1, master=canvas_wrapper)
                canvas1.draw()
                canvas1.get_tk_widget().pack(fill="both", expand=True)

            if chart_type in ["pie", "both"] and category_totals:
                self.fig2, ax2 = plt.subplots(figsize=(7.5, 5.5), dpi=100)
                pie_labels = list(category_totals.keys())
                pie_sizes = list(category_totals.values())
                pie_colors = [
                    "#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854",
                    "#ffd92f", "#e5c494", "#b3b3b3", "#f781bf", "#999999"
                ]

                wedges, _, autotexts = ax2.pie(
                    pie_sizes,
                    labels=None,
                    autopct='%1.1f%%',
                    startangle=140,
                    colors=pie_colors[:len(pie_labels)],
                    wedgeprops=dict(edgecolor='white')
                )

                for autotext in autotexts:
                    autotext.set_color("black")
                    autotext.set_fontsize(12)

                ax2.legend(
                    wedges,
                    pie_labels,
                    title="Categories",
                    loc="center left",
                    bbox_to_anchor=(1, 0.5),
                    fontsize=11,
                    title_fontsize=12
                )

                ax2.set_title("Expenses by Category", fontsize=14, fontweight="bold")
                self.fig2.tight_layout(rect=[0, 0, 0.85, 1])

                canvas_wrapper = ttk.Frame(chart_frame)
                canvas_wrapper.grid(row=0, column=1, sticky="nsew")
                canvas_wrapper.grid_propagate(False)
                canvas_wrapper.config(width=600, height=450)

                canvas2 = FigureCanvasTkAgg(self.fig2, master=canvas_wrapper)
                canvas2.draw()
                canvas2.get_tk_widget().pack(fill="both", expand=True)

            # ✅ Force re-layout after all chart rendering
            self.update_idletasks()

        update_summary()

    def set_budget(self):
        import datetime

        self.clear_content()
        user = self.controller.auth.get_current_user()

        # === Top section with title ===
        wrapper_top = ttk.Frame(self.content_frame)
        wrapper_top.pack(fill="x", pady=(30, 10))

        ttk.Label(wrapper_top, text="💼 Set Monthly Budget", font=("Segoe UI", 20, "bold")).pack(anchor="center")

        # --- Form wrapper (centered) ---
        wrapper_center = ttk.Frame(self.content_frame)
        wrapper_center.pack(pady=(20, 0))  # ⬅️ Space below title only
        wrapper_center.columnconfigure(0, weight=1)

        # --- Month Row ---
        ttk.Label(wrapper_center, text="📅 Month (YYYY-MM):", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="e",
                                                                                         padx=(0, 10), pady=5)
        month_entry = ttk.Entry(wrapper_center, font=("Segoe UI", 11), width=20)
        month_entry.insert(0, datetime.datetime.now().strftime("%Y-%m"))
        month_entry.grid(row=0, column=1, pady=5, sticky="w")

        # --- Budget Amount Row ---
        ttk.Label(wrapper_center, text="💵 Budget Amount:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="e",
                                                                                       padx=(0, 10), pady=5)
        amount_entry = ttk.Entry(wrapper_center, font=("Segoe UI", 11), width=20)
        amount_entry.grid(row=1, column=1, pady=5, sticky="w")
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

                logging.info(f"[User {user.user_id}] set budget for {month}: ${amount:.2f}")
                messagebox.showinfo("Success", f"Budget of ${amount:.2f} set for {month}")
                self.set_budget()
            except Exception as e:
                logging.error(f"[User {user.user_id}] failed to set budget: {e}")
                messagebox.showerror("Error", f"Could not set budget. Please ensure valid date/amount.")


        # --- Save Button Centered Across Columns ---
        ttk.Button(wrapper_center, text="💾 Save Budget", style="Accent.TButton", command=submit_budget).grid(
            row=4, column=0, pady=10, sticky="e"
        )

    def load_landing(self):
        """
        Displays the landing content (profile/overview section).
        """
        self.clear_content()
        build_landing_content(self.content_frame, self.controller)

    def trigger_nav(self, name):
        """
             Programmatically triggers a sidebar button (used after login or routing).
        """
        if name in self.nav_actions:
            self.nav_actions[name].event_generate("<Button-1>")

    def import_expenses_from_csv(self):
        """Imports expenses from a selected CSV file."""
        user = self.controller.auth.get_current_user()
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                data = load_data()

                # Ensure the user has an expense list
                if str(user.user_id) not in data["expenses"]:
                    data["expenses"][str(user.user_id)] = []

                imported_count = 0
                for row in reader:
                    try:
                        amount = float(row["Amount"])
                        date = datetime.datetime.strptime(row["Date"], "%Y-%m-%d").strftime("%Y-%m-%d")
                        category = row["Category"]
                        description = row["Description"]

                        expense = {
                            "expense_id": next(ExpenseTracker.expense_id_counter),
                            "amount": amount,
                            "category": category,
                            "description": description,
                            "user_id": user.user_id,
                            "date": date
                        }
                        data["expenses"][str(user.user_id)].append(expense)
                        imported_count += 1
                    except Exception as e:
                        logging.warning(f"Failed to import row {row}: {e}")

                save_data(data)
                messagebox.showinfo("Success", f"Successfully imported {imported_count} expenses from CSV.")
                logging.info(f"[User {user.user_id}] imported {imported_count} expenses from CSV.")
                self.view_expenses()  # Refresh expenses view
        except Exception as e:
            logging.error(f"Error importing CSV: {e}")
            messagebox.showerror("Error", f"Failed to import expenses from CSV: {e}")

    def view_spending_trend(self):
        """Displays a spending trend line graph for selected months."""
        self.clear_content()
        user = self.controller.auth.get_current_user()

        # Logging the start of the spending trend view
        logging.info(f"User '{user.username}' initiated the Spending Trend view.")

        # Frame for the trend UI
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title of the Spending Trend view
        ttk.Label(frame, text="📈 Spending Trend", font=("Segoe UI", 18, "bold")).pack(pady=10)

        # --- Month Selection ---
        month_selection_frame = ttk.Frame(frame)
        month_selection_frame.pack(pady=10)

        ttk.Label(month_selection_frame, text="Select Months:", font=("Segoe UI", 12)).pack(side="left", padx=5)

        # Generate a list of months from the data
        data = load_data()
        expenses = data.get("expenses", {}).get(str(user.user_id), [])
        available_months = sorted(set(exp["date"][:7] for exp in expenses), reverse=True)

        # Log the available months for debugging
        logging.info(f"Available months for user '{user.username}': {available_months}")

        # Multi-Select Dropdown
        month_var = tk.StringVar(value="Select Months")
        month_entry = ttk.Entry(month_selection_frame, textvariable=month_var, state="readonly", width=25)
        month_entry.pack(side="left", padx=5)

        # Track the chart canvas to prevent overlapping
        self.chart_canvas = None

        # Function to open the multi-select month selector
        def open_month_selector():
            """Opens a popup to select multiple months."""

            def update_selection():
                """Updates the month selection from the listbox."""
                selected = sorted([month_listbox.get(i) for i in month_listbox.curselection()])
                month_var.set(", ".join(selected))
                selector.destroy()
                logging.info(f"User '{user.username}' selected months: {selected}")

            # Create a popup window for month selection
            selector = tk.Toplevel(self)
            selector.title("Select Months")
            selector.geometry("250x300")
            selector.configure(bg="#2e2e2e")
            selector.grab_set()
            logging.info("Month selection popup opened.")

            # Wrapper for the listbox
            wrapper = ttk.Frame(selector, padding=10)
            wrapper.pack(fill="both", expand=True)

            # Listbox for selecting multiple months
            month_listbox = tk.Listbox(wrapper, selectmode="multiple", height=10, width=20)
            month_listbox.pack(pady=10)

            # Populate the listbox with available months
            for month in available_months:
                month_listbox.insert("end", month)

            # Button to confirm selection
            ttk.Button(wrapper, text="Select", style="Accent.TButton", command=update_selection).pack()
            logging.info("Month selection listbox created.")

        # Open month selection on button click
        ttk.Button(month_selection_frame, text="🔽", style="Accent.TButton", command=open_month_selector).pack(
            side="left", padx=5)

        # Function to plot the spending trend
        def plot_spending_trend():
            """Plots the spending trend based on selected months."""
            selected_months = month_var.get().split(", ")
            if len(selected_months) < 1:
                messagebox.showwarning("Selection Error", "Please select at least one month.")
                logging.warning(f"User '{user.username}' attempted to plot without selecting any month.")
                return

            # Log the months being plotted
            logging.info(f"User '{user.username}' plotting spending trend for months: {selected_months}")

            # Clear the previous chart if it exists to avoid overlapping
            if self.chart_canvas:
                self.chart_canvas.get_tk_widget().destroy()
                logging.info("Previous chart canvas cleared.")

            # Calculate total expenses for the selected months
            month_totals = {}
            for month in selected_months:
                total = sum(exp["amount"] for exp in expenses if exp["date"].startswith(month))
                month_totals[month] = total
                logging.info(f"Total for {month}: ${total:.2f}")

            # Prepare data for the line graph
            months = list(month_totals.keys())
            totals = list(month_totals.values())

            # Log the data to be plotted
            logging.info(f"Plotting data for user '{user.username}': Months - {months}, Totals - {totals}")

            # Create the line graph
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(months, totals, marker='o', linestyle='-', color='#d62728', linewidth=2, markersize=8)
            ax.fill_between(months, totals, color='#ff9999', alpha=0.4)
            ax.set_title("Spending Trend Over Selected Months")
            ax.set_ylabel("Total Expense ($)")
            ax.set_xlabel("Months")
            ax.grid(True, linestyle='--', alpha=0.5)

            # Add value labels on points
            for i, value in enumerate(totals):
                ax.text(i, value + 20, f"${value:.2f}", ha='center', va='bottom')

            # Embed the plot in Tkinter and track the canvas to prevent overlapping
            self.chart_canvas = FigureCanvasTkAgg(fig, master=frame)
            self.chart_canvas.draw()
            self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)
            logging.info("Spending trend chart rendered.")

        # Plot Button to generate the trend grap h
        plot_button = ttk.Button(month_selection_frame, text="Show Trend", style="Accent.TButton",
                                 command=plot_spending_trend)
        plot_button.pack(side="left", padx=10)
        logging.info("Plot button created and ready.")




