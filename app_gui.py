import tkinter as tk
from tkinter import ttk, messagebox
from auth import Authentication
from expenses import ExpenseTracker
from dashboards import AdminDashboard, UserDashboard


class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cha-Ching $$")
        self.geometry("1200x1200")
        self.configure(bg="#2e2e2e")
        self.center_window()

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
        w, h = 1000, 700
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def show_frame(self, frame_class):
        if frame_class not in self.frames:
            # Lazy-load dashboards after login
            if frame_class.__name__ == "AdminDashboard":
                self.frames[frame_class] = AdminDashboard(self, self)
            elif frame_class.__name__ == "UserDashboard":
                self.frames[frame_class] = UserDashboard(self, self)
            self.frames[frame_class].grid(row=0, column=0, sticky="nsew")

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

        # Back button top-left
        ttk.Button(self, text="←", command=lambda: controller.show_frame(HomePage)).place(x=10, y=10)

        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.4, anchor="center")

        ttk.Label(wrapper, text="Login", font=("Segoe UI", 20)).pack(pady=(0, 20))

        ttk.Label(wrapper, text="Username:").pack(anchor="w")
        self.username = ttk.Entry(wrapper, width=30)
        self.username.pack(pady=5)

        ttk.Label(wrapper, text="Password:").pack(anchor="w")
        self.password = ttk.Entry(wrapper, show="*", width=30)
        self.password.pack(pady=5)

        ttk.Button(wrapper, text="Login", style="Accent.TButton", command=self.login).pack(pady=15)

    def login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()

        if self.controller.auth.login(user, pwd):
            current_user = self.controller.auth.get_current_user()
            self.controller.current_tracker = ExpenseTracker(current_user)

            # Show the correct dashboard and call its landing loader
            if current_user.role == "admin":
                self.controller.show_frame(AdminDashboard)
                self.controller.frames[AdminDashboard].load_landing()  # 👈 shows the landing page inside the dashboard
            else:
                self.controller.show_frame(UserDashboard)
                self.controller.frames[UserDashboard].load_landing()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")


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

        ttk.Label(wrapper, text="Username:").pack(anchor="w")
        self.username = ttk.Entry(wrapper, width=30)
        self.username.pack(pady=5)

        ttk.Label(wrapper, text="Password:").pack(anchor="w")
        self.password = ttk.Entry(wrapper, show="*", width=30)
        self.password.pack(pady=5)

        ttk.Button(wrapper, text="Register", style="Accent.TButton", command=self.register).pack(pady=15)

    def register(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()

        if not user or not pwd:
            messagebox.showerror("Missing Fields", "Username and password are required.")
            return

        result = self.controller.auth.register(user, pwd)
        if result:
            messagebox.showinfo("Registration Successful", "Your account has been created.")
            self.controller.show_frame(LoginPage)
        else:
            messagebox.showerror("Registration Failed", "Username already exists.")

if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()
#