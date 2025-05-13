# landing.py - Landing Page for the Application
from tkinter import ttk
from core.file_manager import load_data
import datetime


def build_landing_content(container, controller):
    # Get the current logged-in user
    user = controller.auth.get_current_user()
    # Load the application data
    data = load_data()

    # Display a welcome message with the username
    ttk.Label(container, text=f"👋 Welcome back, {user.username}!", font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

    # Check user role and call appropriate landing function
    if user.role == "user":
        show_user_landing(container, user, data, controller)
    else:
        show_admin_landing(container, data, controller)


def show_user_landing(container, user, data, controller):
    # Extract user ID as a string
    user_id = str(user.user_id)
    # Get the current month in YYYY-MM format
    current_month = datetime.datetime.now().strftime("%Y-%m")
    # Get the expenses for the current user
    expenses = data.get("expenses", {}).get(user_id, [])
    # Calculate the total expenses for the current month
    total = sum(e["amount"] for e in expenses if e["date"].startswith(current_month))
    # Get the budget set for the current month, if any
    budget = data.get("budgets", {}).get(user_id, {}).get(current_month)
    # Determine the budget status
    budget_status = f"Set: ${budget:.2f}" if budget else "Not Set"

    # Display summary information with current month, expenses, and budget status
    info = f"📆 Month: {current_month}\n💸 Total Expenses: ${total:.2f}\n📊 Budget: {budget_status}"
    ttk.Label(container, text=info, font=("Segoe UI", 12)).pack(pady=10)

    # Get the dashboard frame from the controller
    dashboard = next(v for k, v in controller.frames.items() if k.__name__ == "UserDashboard")
    # Create a button frame for quick actions
    button_frame = ttk.Frame(container)
    button_frame.pack(pady=20)

    # Add buttons for quick access to features
    ttk.Button(button_frame, text="➕ Add Expense", style="Accent.TButton",
               command=lambda: dashboard.trigger_nav("Add Expense")).pack(side="left", padx=10)
    ttk.Button(button_frame, text="📊 View Summary",
               command=lambda: dashboard.trigger_nav("View Summary")).pack(side="left", padx=10)
    ttk.Button(button_frame, text="📁 View Expenses",
               command=lambda: dashboard.trigger_nav("View Expenses")).pack(side="left", padx=10)
    ttk.Button(button_frame, text="💼 Set Budget",
               command=lambda: dashboard.trigger_nav("Set Budget")).pack(side="left", padx=10)

    # Create a recent activity section
    recent_frame = ttk.LabelFrame(container, text="🕓 Recent Activity", padding=10)
    recent_frame.pack(pady=(20, 10), fill="x")

    # Get the most recent three expenses sorted by date
    recent_exp = sorted(expenses, key=lambda x: x['date'], reverse=True)[:3]
    # Display the recent expenses or a message if none exist
    if recent_exp:
        for exp in recent_exp:
            text = f"{exp['date']} - ${exp['amount']:.2f} for {exp['category']} | {exp['description'][:40]}"
            ttk.Label(recent_frame, text=text, font=("Segoe UI", 10)).pack(anchor="w", pady=2)
    else:
        ttk.Label(recent_frame, text="No recent activity.", font=("Segoe UI", 10, "italic")).pack(anchor="w")

    # Display a motivational quote at the bottom
    ttk.Label(container, text="“Beware of little expenses. A small leak will sink a great ship.” – Benjamin Franklin",
              font=("Segoe UI", 10, "italic"), foreground="#999").pack(pady=15)


def show_admin_landing(container, data, controller):
    # Get the total number of categories and count unused ones
    categories = data.get("categories", {})
    total_categories = len(categories)
    unused = sum(1 for cat in categories.values()
                 if cat["name"] not in {exp["category"]
                 for exps in data.get("expenses", {}).values() for exp in exps})

    # Display admin summary with total and unused categories
    info = f"🗂 Total Categories: {total_categories}\n🚫 Unused Categories: {unused}"
    ttk.Label(container, text=info, font=("Segoe UI", 12)).pack(pady=10)

    # Get the dashboard frame for admin
    dashboard = next(v for k, v in controller.frames.items() if k.__name__ == "AdminDashboard")
    # Create a button frame for admin quick actions
    button_frame = ttk.Frame(container)
    button_frame.pack(pady=20)

    # Add button for category management
    ttk.Button(button_frame, text="📂 Manage Categories", style="Accent.TButton",
               command=lambda: dashboard.trigger_nav("Categories")).pack(side="left", padx=10)

    # Display a leadership quote for admins
    ttk.Label(container, text="“Leadership is not about being in charge. It's about taking care of those in your charge.”",
              font=("Segoe UI", 10, "italic"), foreground="#999").pack(pady=15)
