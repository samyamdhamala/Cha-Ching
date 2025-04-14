# landing.py
import tkinter as tk
from tkinter import ttk
from file_manager import load_data
import datetime


def build_landing_content(container, controller):
    user = controller.auth.get_current_user()
    data = load_data()

    ttk.Label(container, text=f"👋 Welcome back, {user.username}!", font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

    if user.role == "user":
        show_user_landing(container, user, data, controller)
    else:
        show_admin_landing(container, data, controller)

def show_user_landing(container, user, data, controller):
    user_id = str(user.user_id)
    current_month = datetime.datetime.now().strftime("%Y-%m")
    expenses = data.get("expenses", {}).get(user_id, [])
    total = sum(e["amount"] for e in expenses if e["date"].startswith(current_month))
    budget = data.get("budgets", {}).get(user_id, {}).get(current_month)
    budget_status = f"Set: ${budget:.2f}" if budget else "Not Set"

    # Summary info
    info = f"📆 Month: {current_month}\n💸 Total Expenses: ${total:.2f}\n📊 Budget: {budget_status}"
    ttk.Label(container, text=info, font=("Segoe UI", 12)).pack(pady=10)

    # Quick Actions using nav trigger
    dashboard = next(v for k, v in controller.frames.items() if k.__name__ == "UserDashboard")
    button_frame = ttk.Frame(container)
    button_frame.pack(pady=20)

    ttk.Button(button_frame, text="➕ Add Expense", style="Accent.TButton",
               command=lambda: dashboard.trigger_nav("Add Expense")).pack(side="left", padx=10)
    ttk.Button(button_frame, text="📊 View Summary",
               command=lambda: dashboard.trigger_nav("View Summary")).pack(side="left", padx=10)
    ttk.Button(button_frame, text="📁 View Expenses",
               command=lambda: dashboard.trigger_nav("View Expenses")).pack(side="left", padx=10)
    ttk.Button(button_frame, text="💼 Set Budget",
               command=lambda: dashboard.trigger_nav("Set Budget")).pack(side="left", padx=10)

    # Recent Activity
    recent_frame = ttk.LabelFrame(container, text="🕓 Recent Activity", padding=10)
    recent_frame.pack(pady=(20, 10), fill="x")

    recent_exp = sorted(expenses, key=lambda x: x['date'], reverse=True)[:3]
    if recent_exp:
        for exp in recent_exp:
            text = f"{exp['date']} - ${exp['amount']:.2f} for {exp['category']} | {exp['description'][:40]}"
            ttk.Label(recent_frame, text=text, font=("Segoe UI", 10)).pack(anchor="w", pady=2)
    else:
        ttk.Label(recent_frame, text="No recent activity.", font=("Segoe UI", 10, "italic")).pack(anchor="w")

    # Quote
    ttk.Label(container, text="“Beware of little expenses. A small leak will sink a great ship.” – Benjamin Franklin",
              font=("Segoe UI", 10, "italic"), foreground="#999").pack(pady=15)

def show_admin_landing(container, data, controller):
    categories = data.get("categories", {})
    total_categories = len(categories)
    unused = sum(1 for cat in categories.values()
                 if cat["name"] not in {exp["category"]
                 for exps in data.get("expenses", {}).values() for exp in exps})

    # Summary
    info = f"🗂 Total Categories: {total_categories}\n🚫 Unused Categories: {unused}"
    ttk.Label(container, text=info, font=("Segoe UI", 12)).pack(pady=10)

    # Quick Actions using nav trigger
    dashboard = next(v for k, v in controller.frames.items() if k.__name__ == "AdminDashboard")
    button_frame = ttk.Frame(container)
    button_frame.pack(pady=20)

    ttk.Button(button_frame, text="📂 Manage Categories", style="Accent.TButton",
               command=lambda: dashboard.trigger_nav("Categories")).pack(side="left", padx=10)

    # Quote
    ttk.Label(container, text="“Leadership is not about being in charge. It's about taking care of those in your charge.”",
              font=("Segoe UI", 10, "italic"), foreground="#999").pack(pady=15)
