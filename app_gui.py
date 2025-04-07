
import tkinter as tk
from tkinter import messagebox
from auth import Authentication
from expenses import ExpenseTracker

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cha-Ching $$ Expense Tracker")
        self.geometry("400x480")
        self.configure(bg='#333333')
        self.center_window()

        self.auth = Authentication()
        self.current_tracker = None

        self.frames = {}
        for F in (LoginPage, RegisterPage, UserDashboard):
            frame = F(parent=self, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def center_window(self):
        self.update_idletasks()
        width, height = 400, 480
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#333333')
        self.controller = controller

        tk.Label(self, text="Login", font=("Arial", 30), bg='#333333', fg="#FF3399").grid(row=0, column=0, columnspan=2, pady=40)

        tk.Label(self, text="Username", font=("Arial", 16), bg='#333333', fg="#FFFFFF").grid(row=1, column=0)
        self.username = tk.Entry(self, font=("Arial", 16))
        self.username.grid(row=1, column=1, pady=20)

        tk.Label(self, text="Password", font=("Arial", 16), bg='#333333', fg="#FFFFFF").grid(row=2, column=0)
        self.password = tk.Entry(self, font=("Arial", 16), show="*")
        self.password.grid(row=2, column=1, pady=20)

        tk.Button(self, text="Login", font=("Arial", 16), bg="#FF3399", fg="#FFFFFF", command=self.login_user).grid(row=3, column=0, columnspan=2, pady=30)
        tk.Button(self, text="Go to Register", font=("Arial", 12), bg="#555555", fg="#FFFFFF", command=lambda: controller.show_frame(RegisterPage)).grid(row=4, column=0, columnspan=2)

    def login_user(self):
        username = self.username.get()
        password = self.password.get()
        if self.controller.auth.login(username, password):
            self.controller.current_tracker = ExpenseTracker(self.controller.auth.get_current_user())
            self.controller.show_frame(UserDashboard)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")


class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#333333')
        self.controller = controller

        tk.Label(self, text="Register", font=("Arial", 30), bg='#333333', fg="#FF3399").grid(row=0, column=0, columnspan=2, pady=40)

        tk.Label(self, text="Username", font=("Arial", 16), bg='#333333', fg="#FFFFFF").grid(row=1, column=0)
        self.username = tk.Entry(self, font=("Arial", 16))
        self.username.grid(row=1, column=1, pady=20)

        tk.Label(self, text="Password", font=("Arial", 16), bg='#333333', fg="#FFFFFF").grid(row=2, column=0)
        self.password = tk.Entry(self, font=("Arial", 16), show="*")
        self.password.grid(row=2, column=1, pady=20)

        tk.Button(self, text="Register", font=("Arial", 16), bg="#FF3399", fg="#FFFFFF", command=self.register_user).grid(row=3, column=0, columnspan=2, pady=30)
        tk.Button(self, text="Back to Login", font=("Arial", 12), bg="#555555", fg="#FFFFFF", command=lambda: controller.show_frame(LoginPage)).grid(row=4, column=0, columnspan=2)

    def register_user(self):
        username = self.username.get()
        password = self.password.get()
        if self.controller.auth.register(username, password):
            messagebox.showinfo("Success", "Registration successful!")
            self.controller.show_frame(LoginPage)
        else:
            messagebox.showerror("Error", "Username already exists!")


class UserDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#333333')
        self.controller = controller

        tk.Label(self, text="User Dashboard", font=("Arial", 24), bg='#333333', fg="#FF3399").pack(pady=40)

        tk.Button(self, text="Add Expense (Coming Soon)", font=("Arial", 14), bg="#555555", fg="#FFFFFF", state=tk.DISABLED).pack(pady=10)
        tk.Button(self, text="View Summary (Coming Soon)", font=("Arial", 14), bg="#555555", fg="#FFFFFF", state=tk.DISABLED).pack(pady=10)
        tk.Button(self, text="Logout", font=("Arial", 14), bg="#FF3399", fg="#FFFFFF", command=self.logout).pack(pady=30)

    def logout(self):
        self.controller.auth.logout()
        self.controller.show_frame(LoginPage)


if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()
