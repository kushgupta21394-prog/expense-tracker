# Expense Tracker - Python + SQLite
import csv
import sqlite3
from datetime import date

conn = sqlite3.connect("expenses.db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    note TEXT
)""")
conn.commit()


def get_amount():
    while True:
        try:
            return float(input("Amount: "))
        except ValueError:
            print("Enter a valid number.")


def get_date():
    text = input("Date (YYYY-MM-DD, Enter for today): ").strip()
    if text == "":
        return str(date.today())
    try:
        date.fromisoformat(text)
        return text
    except ValueError:
        print("Invalid date, using today.")
        return str(date.today())


def add_expense():
    amount = get_amount()
    category = input("Category (food/travel/etc): ").strip().lower()
    when = get_date()
    note = input("Note (optional): ")
    cur.execute("INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
                (amount, category, when, note))
    conn.commit()
    print("Expense added.")


def show_expenses():
    cur.execute("SELECT id, date, category, amount, note FROM expenses ORDER BY date DESC")
    rows = cur.fetchall()
    if not rows:
        print("No expenses yet.")
        return
    print(f"{'ID':<5}{'Date':<12}{'Category':<12}{'Amount':<10}Note")
    for r in rows:
        print(f"{r[0]:<5}{r[1]:<12}{r[2]:<12}{r[3]:<10.2f}{r[4] or ''}")


def edit_expense():
    exp_id = input("Expense ID to edit: ")
    cur.execute("SELECT id FROM expenses WHERE id = ?", (exp_id,))
    if cur.fetchone() is None:
        print("ID not found.")
        return
    amount = get_amount()
    category = input("New category: ").strip().lower()
    cur.execute("UPDATE expenses SET amount = ?, category = ? WHERE id = ?",
                (amount, category, exp_id))
    conn.commit()
    print("Expense updated.")


def delete_expense():
    exp_id = input("Expense ID to delete: ")
    cur.execute("DELETE FROM expenses WHERE id = ?", (exp_id,))
    conn.commit()
    print("Deleted." if cur.rowcount else "ID not found.")


def monthly_summary():
    month = input("Month (YYYY-MM): ").strip()
    cur.execute("SELECT category, SUM(amount) FROM expenses WHERE date LIKE ? "
                "GROUP BY category ORDER BY SUM(amount) DESC", (month + "%",))
    rows = cur.fetchall()
    if not rows:
        print("No expenses for that month.")
        return
    total = 0
    for category, amount in rows:
        print(f"{category:<12}{amount:.2f}")
        total += amount
    print(f"{'TOTAL':<12}{total:.2f}")


def export_csv():
    cur.execute("SELECT id, date, category, amount, note FROM expenses ORDER BY date")
    with open("expenses.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Date", "Category", "Amount", "Note"])
        writer.writerows(cur.fetchall())
    print("Exported to expenses.csv")


def main():
    while True:
        print("\n1.Add 2.Show all 3.Edit 4.Delete")
        print("5.Monthly summary 6.Export CSV 7.Exit")
        choice = input("Choose: ")
        if choice == "1":
            add_expense()
        elif choice == "2":
            show_expenses()
        elif choice == "3":
            edit_expense()
        elif choice == "4":
            delete_expense()
        elif choice == "5":
            monthly_summary()
        elif choice == "6":
            export_csv()
        elif choice == "7":
            conn.close()
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


main()
