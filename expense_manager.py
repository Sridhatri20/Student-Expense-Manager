import sqlite3
from datetime import datetime

DB_NAME = "student_expenses.db"


# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Create table for expenses
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT
        )
    """)

    # Create table for monthly budget
    cur.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            month TEXT PRIMARY KEY,
            amount REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------- HELPER FUNCTIONS ----------
def get_current_month_key():
    """
    Returns month key like '2025-12' for December 2025.
    """
    now = datetime.now()
    return now.strftime("%Y-%m")


def input_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("Amount cannot be negative. Try again.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


# ---------- CORE FEATURES ----------
def add_expense():
    print("\n--- Add New Expense ---")
    date_str = input("Enter date (YYYY-MM-DD) [press Enter for today]: ").strip()

    if date_str == "":
        date_str = datetime.now().strftime("%Y-%m-%d")

    category = input("Enter category (Food/Travel/Shopping/Fees/Other): ").strip()
    amount = input_float("Enter amount spent: ")
    note = input("Enter note/description (optional): ").strip()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO expenses (date, category, amount, note)
        VALUES (?, ?, ?, ?)
    """, (date_str, category, amount, note))

    conn.commit()
    conn.close()

    print("✅ Expense added successfully!")


def set_monthly_budget():
    print("\n--- Set / Update Monthly Budget ---")
    month_key = get_current_month_key()
    print(f"Current month: {month_key} (YYYY-MM)")
    amount = input_float("Enter budget amount for this month: ")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Insert or replace budget
    cur.execute("""
        INSERT INTO budget (month, amount)
        VALUES (?, ?)
        ON CONFLICT(month) DO UPDATE SET amount = excluded.amount
    """, (month_key, amount))

    conn.commit()
    conn.close()

    print(f"✅ Budget of {amount} set for month {month_key}.")


def view_all_expenses():
    print("\n--- All Expenses ---")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT id, date, category, amount, note FROM expenses ORDER BY date")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("No expenses found.")
        return

    print("{:<5} {:<12} {:<15} {:<10} {:<30}".format("ID", "Date", "Category", "Amount", "Note"))
    print("-" * 75)
    for row in rows:
        print("{:<5} {:<12} {:<15} {:<10.2f} {:<30}".format(row[0], row[1], row[2], row[3], row[4] if row[4] else ""))


def view_month_summary():
    print("\n--- Monthly Summary (Current Month) ---")
    month_key = get_current_month_key()
    print(f"Month: {month_key}")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Total expenses in this month
    cur.execute("""
        SELECT SUM(amount) FROM expenses
        WHERE strftime('%Y-%m', date) = ?
    """, (month_key,))
    total_expense = cur.fetchone()[0]
    if total_expense is None:
        total_expense = 0.0

    # Budget for this month
    cur.execute("SELECT amount FROM budget WHERE month = ?", (month_key,))
    row = cur.fetchone()
    budget_amount = row[0] if row else None

    print(f"Total expenses this month: ₹{total_expense:.2f}")

    if budget_amount is None:
        print("⚠ No budget set for this month.")
    else:
        print(f"Budget for this month:   ₹{budget_amount:.2f}")
        remaining = budget_amount - total_expense
        if remaining >= 0:
            print(f"✅ You are within budget. Remaining: ₹{remaining:.2f}")
        else:
            print(f"❌ Budget exceeded by: ₹{-remaining:.2f}")

    conn.close()


def view_category_wise_summary():
    print("\n--- Category-wise Summary (Current Month) ---")
    month_key = get_current_month_key()
    print(f"Month: {month_key}")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT category, SUM(amount) 
        FROM expenses
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY category
    """, (month_key,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("No expenses found for this month.")
        return

    print("{:<15} {:<10}".format("Category", "Total Spent"))
    print("-" * 30)
    for category, total in rows:
        print("{:<15} {:<10.2f}".format(category, total))


def delete_expense():
    print("\n--- Delete Expense ---")
    view_all_expenses()

    try:
        expense_id = int(input("Enter the ID of the expense to delete: "))
    except ValueError:
        print("Invalid ID.")
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    deleted_count = cur.rowcount
    conn.close()

    if deleted_count == 0:
        print("⚠ No expense found with that ID.")
    else:
        print("✅ Expense deleted successfully.")


# ---------- MAIN MENU ----------
def main_menu():
    init_db()
    while True:
        print("\n==============================")
        print("  Student Expense Manager")
        print("==============================")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Set / Update Monthly Budget")
        print("4. View Monthly Summary")
        print("5. View Category-wise Summary")
        print("6. Delete an Expense")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_all_expenses()
        elif choice == "3":
            set_monthly_budget()
        elif choice == "4":
            view_month_summary()
        elif choice == "5":
            view_category_wise_summary()
        elif choice == "6":
            delete_expense()
        elif choice == "0":
            print("Exiting... Bye! 👋")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
