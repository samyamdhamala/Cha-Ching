# admin_dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from core.file_manager import load_data, save_data
from .base_dashboard import BaseDashboard
from ui.landing import build_landing_content

class AdminDashboard(BaseDashboard):
    """
    Admin dashboard for category management.
    Enables category creation, editing, and deletion.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.nav_actions = {}

        # Create and bind sidebar navigation item
        def create_nav_item(icon, text, command):
            full_text = f"{icon}  {text}"
            btn = tk.Label(self.nav_frame, text=full_text, bg="#1f1f2e", fg="white",
                           font=("Segoe UI", 11), anchor="w", padx=20)
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e: btn.config(bg="#333354"))
            btn.bind("<Leave>", lambda e: btn.config(bg="#1f1f2e"))
            btn.bind("<Button-1>", lambda e: command())
            return btn

        self.nav_actions["Categories"] = create_nav_item("\U0001F4C1", "Categories", self.manage_categories)

    def manage_categories(self):
        """
        Displays category management UI with add/edit/delete functionality.
        """
        logger = logging.getLogger(__name__)
        self.clear_content()
        user = self.controller.auth.get_current_user()
        data = load_data()
        logger.info(f"[{user.username}] opened Category Management dashboard.")

        wrapper = ttk.Frame(self.content_frame)
        wrapper.pack(fill="both", expand=True, padx=40, pady=30)
        wrapper.columnconfigure(0, weight=1)

        # Page Heading
        ttk.Label(wrapper, text="\U0001F4C1 Manage Categories", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, pady=(0, 20), sticky="w")
        categories = data.get("categories", {})

        # -------------------- Treeview --------------------
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

        # -------------------- Button Controls --------------------
        button_frame = ttk.Frame(wrapper)
        button_frame.grid(row=2, column=0, pady=(10, 0), sticky="w")

        def refresh_table():
            """Clears and repopulates category list."""
            for row in tree.get_children():
                tree.delete(row)
            for cid in sorted(categories, key=int):
                cat = categories[cid]
                tree.insert("", "end", iid=cid, values=(cid, cat['name']))

        def on_edit():
            """Handles category editing via popup."""
            selected = tree.selection()
            if not selected:
                logger.warning(f"[{user.username}] attempted to edit without selecting a category.")
                messagebox.showwarning("Select", "Please select a category to edit.")
                return

            cid = selected[0]
            old_name = categories[cid]['name']

            # --- Edit Popup ---
            edit_win = tk.Toplevel(self)
            edit_win.title("Edit Category")
            edit_win.geometry("320x180")
            edit_win.configure(bg="#2e2e2e")

            # Entry label and input
            ttk.Label(edit_win, text="Edit Category Name:", font=("Segoe UI", 12)).grid(row=0, column=0, pady=10,
                                                                                        padx=20, sticky="w")
            name_var = tk.StringVar(value=old_name)
            entry = ttk.Entry(edit_win, textvariable=name_var, font=("Segoe UI", 11), width=30)
            entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

            def save():
                new_name = name_var.get().strip()
                if not new_name:
                    logger.warning(f"[{user.username}] tried renaming category ID {cid} with empty name.")
                    messagebox.showerror("Error", "Name cannot be empty.")
                    return
                if any(cat['name'].lower() == new_name.lower() for k, cat in categories.items() if k != cid):
                    logger.warning(f"[{user.username}] tried renaming category to duplicate: {new_name}")
                    messagebox.showerror("Error", "Category already exists.")
                    return

                # Update category name and all related expenses
                categories[cid]['name'] = new_name
                for uid, exps in data.get("expenses", {}).items():
                    for exp in exps:
                        if exp["category"] == old_name:
                            exp["category"] = new_name

                save_data(data)
                refresh_table()
                logger.info(f"[{user.username}] renamed category '{old_name}' to '{new_name}'")
                messagebox.showinfo("Updated", "Category updated successfully.")
                edit_win.destroy()

            # Fix: use grid layout for the frame and pack inside it
            button_frame = ttk.Frame(edit_win)
            button_frame.grid(row=2, column=0, pady=15)
            ttk.Button(button_frame, text="💾 Save", style="Accent.TButton", command=save).pack()

        def on_delete():
            """Handles deletion of selected category."""
            selected = tree.selection()
            if not selected:
                logger.warning(f"[{user.username}] tried to delete without selecting a category.")
                messagebox.showwarning("Select", "Please select a category to delete.")
                return

            cid = selected[0]
            cat_name = categories[cid]["name"]
            used = any(exp["category"] == cat_name for exps in data.get("expenses", {}).values() for exp in exps)
            if used:
                logger.warning(f"[{user.username}] tried deleting category in use: {cat_name}")
                messagebox.showerror("Blocked", f"Category '{cat_name}' is used in expenses.")
                return

            if messagebox.askyesno("Confirm", f"Delete category '{cat_name}'?"):
                del categories[cid]
                save_data(data)
                refresh_table()
                logger.info(f"[{user.username}] deleted category ID {cid}: '{cat_name}'")
                messagebox.showinfo("Deleted", "Category deleted.")

        ttk.Button(button_frame, text="✏️ Edit", style="Accent.TButton", command=on_edit).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", style="Danger.TButton", command=on_delete).pack(side="left", padx=5)

        # -------------------- New Category Creation --------------------
        create_frame = ttk.Frame(wrapper)
        create_frame.grid(row=3, column=0, pady=(30, 0), sticky="w")
        ttk.Label(create_frame, text="➕ Create New Category:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="w")
        new_cat_var = tk.StringVar()
        new_cat_entry = ttk.Entry(create_frame, textvariable=new_cat_var, font=("Segoe UI", 11), width=30)
        new_cat_entry.grid(row=1, column=0, pady=(0, 5), sticky="w")

        def create_category():
            """Handles new category creation."""
            name = new_cat_var.get().strip()
            if not name:
                logger.warning(f"[{user.username}] tried creating category with empty name.")
                messagebox.showerror("Error", "Category name cannot be empty.")
                return
            if any(cat['name'].lower() == name.lower() for cat in categories.values()):
                logger.warning(f"[{user.username}] tried creating duplicate category: {name}")
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

        ttk.Button(create_frame, text="Create", style="Accent.TButton", command=create_category).grid(row=1, column=1, padx=10)
        refresh_table()

    def load_landing(self):
        """Loads the landing screen for admins (on clicking profile)."""
        self.clear_content()
        build_landing_content(self.content_frame, self.controller)

    def trigger_nav(self, name):
        """Triggers the sidebar navigation action."""
        if name in self.nav_actions:
            self.nav_actions[name].event_generate("<Button-1>")
