import tkinter as tk
from tkinter import ttk, messagebox
from auth import Authentication
from expenses import ExpenseTracker
from dashboards import AdminDashboard, UserDashboard

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cha-Ching $$")
        self.geometry("1000x1000")
        self.configure(bg="#2e2e2e")
        self.center_window()

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#2e2e2e")
        style.configure("TLabel", background="#2e2e2e", foreground="#eeeeee", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 11), padding=6)
        style.configure("Accent.TButton", background="#21c064", foreground="white")
        style.map("Accent.TButton", background=[("active", "#1ba558"), ("pressed", "#188e4d")])

        self.auth = Authentication()
        self.current_tracker = None

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
            current_user = self.controller.auth.get_current_user()
            self.controller.current_tracker = ExpenseTracker(current_user)
            if current_user.role == "admin":
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

if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()
