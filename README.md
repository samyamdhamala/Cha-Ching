# Cha-Ching $$ - Personal Expense Tracker

![Cha-Ching Logo](https://your-logo-url.com)  
*A Python-based personal expense tracker with file-based storage and budget management.*

## 📌 Project Overview
Cha-Ching $$ is a **Python-based personal expense tracking application** that allows users to log, categorize, and manage their daily expenses. The project uses **file-based storage (JSON)** for persistence, secure **password hashing (SHA-256)** for authentication, and a modular architecture for maintainability.

## 🚀 Features
### **User Management**
- Secure **registration & login** with password hashing.
- Admin & User roles with different permissions.

### **Expense Tracking**
- Users can **add, edit, delete, and view expenses**.
- Expenses are stored persistently in `data.json`.

### **Budget Management**
- Users can **set monthly budgets** and get warnings if exceeded.
- Budget tracking by period (e.g., `YYYY-MM`).

### **Category Management (Admin Only)**
- Admin can **create, update, and delete categories**.
- Users select categories for expenses.

### **File-Based Storage**
- No database required, all data is stored in `data.json`.

## 🛠️ Technologies Used
- **Python 3.9+**
- **File-Based Storage (JSON)**
- **Password Hashing (SHA-256)**
- **Logging (app.log for user activity tracking)**

## Project Structure
```
Cha-Ching/
│── app.py             # Main entry point for the application
│── auth.py            # Handles authentication (login, registration, hashing)
│── expenses.py        # Expense tracking and budget management
│── file_manager.py    # Handles file-based storage (JSON)
│── models.py         # User, Expense, Budget, and Category models
│── data.json         # Stores all user data, expenses, budgets, and categories
│── app.log           # Logs application activity
│── README.md         # Project documentation (You're here!)
```

## 🔧 Installation & Setup
1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Cha-Ching.git
cd Cha-Ching
```

3. **Run the application**
```bash
python app.py
```

## 🎮 How to Use
1. **Launch the app** and select an option from the **Main Menu**:
   - **Register a new account** *(first-time users)*.
   - **Login** *(if you already have an account)*.
   - **Exit** *(to quit the application)*.

2. **For Admin Users:**
   - Manage **categories** (Add, Edit, Delete).
   - View all available categories.

3. **For Regular Users:**
   - **Add expenses** under predefined categories.
   - **Set a monthly budget** and track spending.
   - **View expense summary** by category and date.

## 🚀 Future Enhancements
✔ **Graphical User Interface (GUI)** using Tkinter.  
✔ **Data Export** options (CSV, Excel reports).  
✔ **Session-based authentication** to keep users logged in.  
✔ **Performance optimizations** for file read/write operations.  

## 📜 License
This project is **open-source** and licensed under the [MIT License](LICENSE). Feel free to contribute! 😊

## 📧 Contact
For any questions or suggestions, feel free to reach out:
- **GitHub:** [@ySamyam Dhamala](https://github.com/samyamdhamala)
- **GitHub:** [@Alvi Anowar](https://github.com/alvianowar)
- **GitHub:** [@Gamvirta Poudel](https://github.com/GamvirtaPoudel)

---
💡 _Cha-Ching $$ - Because every penny counts!_ 🤑

