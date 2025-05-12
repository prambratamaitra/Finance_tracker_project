# Finance_tracker_project

A command-line application for managing personal finances. This tool allows users to register, track income and expenses, set budgets, generate reports, and manage backups—all stored in an SQLite database.

🚀 Features
✅ User Registration & Login

💸 Add, View, and Categorize Income/Expenses

📊 Generate Monthly Reports with Budget Comparison

🎯 Set and Monitor Budgets

💾 SQLite Database with Backup & Restore

🧪 Unit Tests for Core Features

📚 CLI-Based User Experience

🛠 Setup Instructions
Clone or Download this repository.

Install Required Libraries (only tabulate is third-party):

bash
Copy
Edit
pip install tabulate
Run the Application:

bash
Copy
Edit
python personal_finance_cli.py
SQLite database will be created automatically if it doesn't exist.

📚 CLI Usage Guide
Main Menu:
markdown
Copy
Edit
1. Register
2. Login
3. Backup Database
4. Restore Database
5. Exit
After Login:
markdown
Copy
Edit
1. Add Transaction
2. View Transactions
3. Generate Monthly Report
4. Logout
💾 Database Details
users: Stores usernames and hashed passwords.

transactions: Records of income and expenses with timestamps.

budgets: Optional category-wise monthly budget limits.

📦 Backup & Restore
Backups stored in /backup/finance_db_backup.sqlite

Use option 3 & 4 in the main menu to back up or restore your data.

🧪 Running Unit Tests
Run the script in test mode using:

bash
Copy
Edit
python -m unittest personal_finance_cli.py
📝 Notes
All date inputs should be in YYYY-MM-DD format.

Budget comparisons are shown in the monthly report.

Default storage is in finance_db.sqlite.

