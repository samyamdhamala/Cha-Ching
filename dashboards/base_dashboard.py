# base_dashboard.py

import tkinter as tk
from tkinter import ttk



class BaseDashboard(ttk.Frame):
    """
    Shared base class for both AdminDashboard and UserDashboard.
    Sets up consistent layout: top user menu, left navigation, and right content area.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Layout configuration
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # ------------------ TOP USER MENU ------------------
        top_bar = ttk.Frame(self)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

        user = self.controller.auth.get_current_user()
        user_menu = ttk.Menubutton(top_bar, text=f"\U0001F464 {user.username}")
        menu = tk.Menu(user_menu, tearoff=0)
        menu.add_command(label=f"\U0001F464 Profile ({user.username})", command=self.show_profile)
        menu.add_command(label="\U0001F6AA Logout", command=self.logout)
        user_menu["menu"] = menu
        user_menu.pack(side="right", padx=10, pady=5)

        # ------------------ LEFT NAVIGATION PANEL ------------------
        self.nav_frame = tk.Frame(self, bg="#1f1f2e", width=150)
        self.nav_frame.grid(row=1, column=0, sticky="ns")
        self.nav_frame.grid_propagate(False)

        # ------------------ MAIN CONTENT FRAME ------------------
        self.content_frame = ttk.Frame(self, width=800, height=600)
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        self.content_frame.grid_propagate(False)

    def clear_content(self):
        """Clears all widgets in the main content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_profile(self):
        """Loads profile/landing section (usually reuses landing page builder)."""
        self.load_landing()

    def logout(self):
        """Logs out the user and returns to Home screen."""
        self.controller.auth.logout()

        # Reset login fields and redirect to HomePage without importing them
        for frame_class, frame_instance in self.controller.frames.items():
            if frame_class.__name__ == "LoginPage":
                frame_instance.reset_fields()
            if frame_class.__name__ == "HomePage":
                self.controller.show_frame(frame_class)
                break


