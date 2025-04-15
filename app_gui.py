import tkinter as tk
from tkinter import ttk, messagebox
from core.auth import Authentication
from core.expenses import ExpenseTracker
from dashboards import AdminDashboard, UserDashboard
import logging


class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cha-Ching $$")
        self.geometry("1200x1200")
        self.configure(bg="#2e2e2e")
        self.center_window()
        self.minsize(1100, 700)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 11))  # Default for all ttk widgets

        # Frame background
        style.configure("TFrame", background="#1b1b2f")

        # Label styling
        style.configure("TLabel", background="#1b1b2f", foreground="#eeeeee", font=("Segoe UI", 12))

        # Entry fields
        style.configure("TEntry", foreground="#ffffff", fieldbackground="#2e2e3e", background="#2e2e3e")

        # Buttons - default (e.g., Register, Quit)
        style.configure("TButton",background="#2e2e3e",foreground="#eeeeee",font=("Segoe UI", 11),padding=6,relief="flat",borderwidth=0)
        style.map("TButton",background=[("active", "#3a3a4d"), ("pressed", "#252532")],foreground=[("disabled", "#888888")])

        style.configure("Accent.TButton",background="#21c064",foreground="white",font=("Segoe UI", 11, "bold"),relief="flat",borderwidth=0)

        # Danger (red) buttons - e.g., Delete Category
        style.configure("Danger.TButton",background="#d9534f",foreground="white",font=("Segoe UI", 11, "bold"),relief="flat",borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#c9302c"), ("pressed", "#ac2925")])

        self.auth = Authentication()
        self.current_tracker = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, LoginPage, RegisterPage):
            frame = F(self, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def center_window(self):
        self.update_idletasks()
        w, h = 1200, 750  # ⬅️ More space for charts + legends
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def show_frame(self, frame_class):
        if frame_class not in self.frames:
            if frame_class.__name__ == "AdminDashboard":
                self.frames[frame_class] = AdminDashboard(self, self)
            elif frame_class.__name__ == "UserDashboard":
                self.frames[frame_class] = UserDashboard(self, self)
            self.frames[frame_class].grid(row=0, column=0, sticky="nsew")

        # ✅ Clear login fields when navigating to LoginPage
        if frame_class.__name__ == "LoginPage":
            self.frames[frame_class].reset_fields()

        # ✅ Clear register fields when navigating to RegisterPage
        if frame_class.__name__ == "RegisterPage":
            self.frames[frame_class].reset_fields()

        self.frames[frame_class].tkraise()


class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.4, anchor="center")

        title = ttk.Label(wrapper, text="Cha-Ching $$", font=("Segoe UI", 30, "bold"))
        subtitle = ttk.Label(wrapper, text="Track your expenses with style 💸", font=("Segoe UI", 14))
        title.pack(pady=(0, 5))
        subtitle.pack(pady=(0, 20))

        ttk.Button(wrapper, text="Login", style="Accent.TButton",
                   command=lambda: controller.show_frame(LoginPage)).pack(pady=5, ipadx=20)
        ttk.Button(wrapper, text="Register", style="Accent.TButton",
                   command=lambda: controller.show_frame(RegisterPage)).pack(pady=5, ipadx=18)

        # Quit Button at bottom right
        quit_btn = ttk.Button(self, text="Quit", style="TButton", command=controller.destroy)
        quit_btn.place(relx=0.95, rely=0.95, anchor="se")

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Back button (top-left corner)
        ttk.Button(self, text="←", command=lambda: controller.show_frame(HomePage)).place(x=10, y=10)

        # Centered wrapper frame
        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.4, anchor="center")

        ttk.Label(wrapper, text="Login", font=("Segoe UI", 20)).pack(pady=(0, 20))

        # --- Username Field ---
        ttk.Label(wrapper, text="Username:").pack(anchor="w")
        self.username = ttk.Entry(wrapper, width=30, font=("Segoe UI", 12))
        self.username.insert(0, "Enter username...")
        self.username.pack(pady=5, ipady=6)
        self.username.focus_set()

        # --- Password Field ---
        ttk.Label(wrapper, text="Password:").pack(anchor="w")
        self.password = ttk.Entry(wrapper, show="*", width=30, font=("Segoe UI", 12))
        self.password.insert(0, "Enter password...")
        self.password.pack(pady=5, ipady=6)

        # --- Show Password Toggle ---
        def toggle_password():
            if show_pass_var.get():
                self.password.config(show="")
            else:
                self.password.config(show="*")

        show_pass_var = tk.BooleanVar()
        ttk.Checkbutton(wrapper, text="Show Password", variable=show_pass_var,
                        command=toggle_password).pack(anchor="w", pady=(0, 10))

        # --- Validation Message Label ---
        self.validation_msg = ttk.Label(wrapper, text="", foreground="red", font=("Segoe UI", 10))
        self.validation_msg.pack(pady=(0, 5))

        # --- Clear on First Click ---
        def clear_once(entry, placeholder):
            def inner(event):
                if entry.get() == placeholder:
                    entry.delete(0, "end")
                entry.unbind("<FocusIn>")
            return inner

        self.username.bind("<FocusIn>", clear_once(self.username, "Enter username..."))
        self.password.bind("<FocusIn>", clear_once(self.password, "Enter password..."))

        # --- Login Button ---
        ttk.Button(wrapper, text="Login", style="Accent.TButton", command=self.login).pack(pady=15)

    def reset_fields(self):
        """Clears the username and password fields."""
        self.username.delete(0, "end")
        self.password.delete(0, "end")
        self.validation_msg.config(text="")

    def login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()

        # Inline validation
        if not user or user == "Enter username...":
            self.validation_msg.config(text="Username is required.")
            self.username.focus_set()
            return
        if not pwd or pwd == "Enter password...":
            self.validation_msg.config(text="Password is required.")
            self.password.focus_set()
            return

        # Auth check
        if self.controller.auth.login(user, pwd):
            current_user = self.controller.auth.get_current_user()
            logging.info(f"[GUI] User '{current_user.username}' logged in successfully.")

            self.controller.current_tracker = ExpenseTracker(current_user)
            if current_user.role == "admin":
                self.controller.show_frame(AdminDashboard)
                self.controller.frames[AdminDashboard].load_landing()
            else:
                self.controller.show_frame(UserDashboard)
                self.controller.frames[UserDashboard].load_landing()
        else:
            logging.warning(f"[GUI] Failed login attempt with username: '{user}'")
            self.validation_msg.config(text="Invalid username or password.")
            self.username.focus_set()



class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Back button top-left
        ttk.Button(self, text="←", command=lambda: controller.show_frame(HomePage)).place(x=10, y=10)

        # Wrapper frame centered
        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.4, anchor="center")

        ttk.Label(wrapper, text="Register", font=("Segoe UI", 20)).pack(pady=(0, 20))

        # Username
        ttk.Label(wrapper, text="Username:").pack(anchor="w")
        self.username = ttk.Entry(wrapper, width=30, font=("Segoe UI", 12))
        self.username.insert(0, "Enter username...")
        self.username.pack(pady=5, ipady=6)
        self.username.focus_set()

        # Password
        ttk.Label(wrapper, text="Password:").pack(anchor="w")
        self.password = ttk.Entry(wrapper, show="*", width=30, font=("Segoe UI", 12))
        self.password.insert(0, "Enter password...")
        self.password.pack(pady=5, ipady=6)

        # Confirm Password
        ttk.Label(wrapper, text="Confirm Password:").pack(anchor="w")
        self.confirm_password = ttk.Entry(wrapper, show="*", width=30, font=("Segoe UI", 12))
        self.confirm_password.insert(0, "Re-enter password...")
        self.confirm_password.pack(pady=5, ipady=6)

        # Show Password Toggle
        def toggle_password():
            if show_pass_var.get():
                self.password.config(show="")
                self.confirm_password.config(show="")
            else:
                self.password.config(show="*")
                self.confirm_password.config(show="*")

        show_pass_var = tk.BooleanVar()
        show_pass_check = ttk.Checkbutton(wrapper, text="Show Password", variable=show_pass_var, command=toggle_password)
        show_pass_check.pack(anchor="w", pady=(0, 10))

        # Validation message label (empty by default)
        self.validation_msg = ttk.Label(wrapper, text="", foreground="red", font=("Segoe UI", 10))
        self.validation_msg.pack(pady=(0, 5))

        # Clear on first focus (for placeholder-like behavior)
        def clear_once(entry):
            def inner(event):
                if entry.get() in ["Enter username...", "Enter password...", "Re-enter password..."]:
                    entry.delete(0, "end")
                entry.unbind("<FocusIn>")
            return inner

        self.username.bind("<FocusIn>", clear_once(self.username))
        self.password.bind("<FocusIn>", clear_once(self.password))
        self.confirm_password.bind("<FocusIn>", clear_once(self.confirm_password))

        # Register button
        ttk.Button(wrapper, text="Register", style="Accent.TButton", command=self.register).pack(pady=15)

    def reset_fields(self):
        """Clears all input fields and validation message."""
        self.username.delete(0, "end")
        self.password.delete(0, "end")
        self.confirm_password.delete(0, "end")
        self.validation_msg.config(text="")

    def register(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        confirm = self.confirm_password.get().strip()

        if not user or user == "Enter username...":
            self.validation_msg.config(text="Username is required.")
            self.username.focus_set()
            return

        if not pwd or pwd == "Enter password...":
            self.validation_msg.config(text="Password is required.")
            self.password.focus_set()
            return

        if pwd != confirm:
            self.validation_msg.config(text="Passwords do not match.")
            self.confirm_password.focus_set()
            return

        result = self.controller.auth.register(user, pwd)
        if result:
            self.validation_msg.config(text="", foreground="green")
            messagebox.showinfo("Registration Successful", "Your account has been created.")
            self.controller.show_frame(LoginPage)
        else:
            self.validation_msg.config(text="Username already exists.", foreground="red")
            self.username.focus_set()


if __name__ == "__main__":
    import sys
    import tkinter.messagebox as mb

    mb.showwarning(
        "Improper Launch",
        "Please run the application using app.py\n\nThis ensures proper logging and admin setup."
    )
    sys.exit()
#