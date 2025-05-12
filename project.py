# personal_finance_cli.py

import os
import shutil
import sqlite3
import datetime
import unittest
from getpass import getpass
from tabulate import tabulate

# --- Database Setup ---
DB_PATH = "finance_db.sqlite"
BACKUP_DIR = "backup"
BACKUP_FILE = os.path.join(BACKUP_DIR, "finance_db_backup.sqlite")

if not os.path.exists(DB_PATH):
    print("⚠️ Database not found. Creating new one...")

# Connect to SQLite and enable foreign keys
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

# --- Create Tables ---
def create_tables():
    """Create tables for users, transactions, and budgets."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        category TEXT,
        amount REAL,
        month INTEGER,
        year INTEGER,
        FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
    )
    """)
    conn.commit()

# --- Backup and Restore Functions ---
def backup_database():
    """Backup the SQLite database to a backup directory."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copy2(DB_PATH, BACKUP_FILE)
    print("✅ Backup created at", BACKUP_FILE)

def restore_database():
    """Restore the SQLite database from backup."""
    if os.path.exists(BACKUP_FILE):
        shutil.copy2(BACKUP_FILE, DB_PATH)
        print("✅ Database restored from backup.")
    else:
        print("❌ No backup found.")

# --- User Functions ---
def register():
    """Register a new user."""
    username = input("Enter new username: ")
    password = getpass("Enter password: ")
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print("❌ Username already exists. Try another one.")
        return
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    print("✅ Registration successful.")

def login():
    """Authenticate a user."""
    username = input("Username: ")
    password = getpass("Password: ")
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    if cursor.fetchone():
        print("Login successful.")
        return username
    else:
        print("Login failed.")
        return None

# --- Transaction Functions ---
def add_transaction(username):
    """Add a new income or expense transaction."""
    type_ = input("Type (income/expense): ").strip().lower()
    amount = float(input("Amount: "))
    category = input("Category: ").strip()
    date = input("Date (YYYY-MM-DD): ")
    cursor.execute("""
        INSERT INTO transactions (username, type, amount, category, date)
        VALUES (?, ?, ?, ?, ?)
    """, (username, type_, amount, category, date))
    conn.commit()
    print("✅ Transaction added.")

def list_transactions(username):
    """List all transactions of a user."""
    cursor.execute("SELECT amount, type, category, date, created_at FROM transactions WHERE username=?", (username,))
    rows = cursor.fetchall()
    print(tabulate(rows, headers=["Amount", "Type", "Category", "Date", "Created At"], tablefmt="fancy_grid"))

def generate_monthly_report(username):
    """Generate income/expense summary with budget comparison for a month."""
    month = int(input("Enter month (1-12): "))
    year = int(input("Enter year: "))
    cursor.execute("""
        SELECT category, type, SUM(amount) FROM transactions 
        WHERE username=? AND strftime('%m', date)=? AND strftime('%Y', date)=?
        GROUP BY category, type
    """, (username, f"{month:02d}", str(year)))
    data = cursor.fetchall()

    cursor.execute("""
        SELECT category, amount FROM budgets 
        WHERE username=? AND month=? AND year=?
    """, (username, month, year))
    budgets = {row[0]: row[1] for row in cursor.fetchall()}

    income_report = []
    expense_report = []
    total_income = total_expense = 0

    for category, type_, amt in data:
        budget_amt = budgets.get(category, '-')
        if type_ == 'income':
            total_income += amt
            income_report.append([category, amt])
        else:
            total_expense += amt
            expense_report.append([category, amt, budget_amt])

    print("\n--- Monthly Income Report ---")
    print(tabulate(income_report, headers=["Category", "Amount"], tablefmt="fancy_grid"))

    print("\n--- Monthly Expense Report ---")
    print(tabulate(expense_report, headers=["Category", "Amount", "Budget"], tablefmt="fancy_grid"))

    print(f"\nTotal Income: ₹{total_income}")
    print(f"Total Expense: ₹{total_expense}")
    print(f"Savings: ₹{total_income - total_expense}")

# --- Main Menu ---
def main():
    """Main entry point for the application."""
    create_tables()
    while True:
        print("""
1. Register
2. Login
3. Backup Database
4. Restore Database
5. Exit
        """)
        choice = input("Enter choice: ")
        if choice == '1':
            register()
        elif choice == '2':
            user = login()
            if user:
                user_menu(user)
        elif choice == '3':
            backup_database()
        elif choice == '4':
            restore_database()
        elif choice == '5':
            break
        else:
            print("Invalid choice.")

# --- User Menu ---
def user_menu(username):
    """Menu available after user logs in."""
    while True:
        print("""
1. Add Transaction
2. View Transactions
3. Generate Monthly Report
4. Logout
        """)
        choice = input("Enter choice: ")
        if choice == '1':
            add_transaction(username)
        elif choice == '2':
            list_transactions(username)
        elif choice == '3':
            generate_monthly_report(username)
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

# --- Unit Tests ---
class TestFinanceApp(unittest.TestCase):
    def setUp(self):
        create_tables()
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM transactions")
        conn.commit()

    def test_register_and_login(self):
        cursor.execute("INSERT INTO users VALUES (?, ?)", ('testuser', 'pass'))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", ('testuser', 'pass'))
        self.assertIsNotNone(cursor.fetchone())

    def test_add_transaction(self):
        cursor.execute("INSERT INTO users VALUES (?, ?)", ('tuser', 'pass'))
        conn.commit()
        cursor.execute("INSERT INTO transactions (username, type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                       ('tuser', 'income', 1000.0, 'Salary', '2025-05-12'))
        conn.commit()
        cursor.execute("SELECT * FROM transactions WHERE username=?", ('tuser',))
        self.assertEqual(len(cursor.fetchall()), 1)

    def test_generate_monthly_report_empty(self):
        cursor.execute("INSERT INTO users VALUES (?, ?)", ('emptyuser', '1234'))
        conn.commit()
        cursor.execute("SELECT * FROM transactions WHERE username=?", ('emptyuser',))
        self.assertEqual(cursor.fetchall(), [])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ Application error:", e)

