import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database table
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            paid INTEGER NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Run initialization when the app starts
init_db()

# ... (keep your existing imports and init_db function) ...

@app.route('/')
def index():
    error = request.args.get('error')
    conn = get_db_connection()

    # Fetch all expenses
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()

    # Calculate total (handling the edge case where there are no expenses yet)
    total_row = conn.execute('SELECT SUM(amount) as total FROM expenses').fetchone()
    total = total_row['total'] if total_row['total'] else 0.0

    conn.close()
    return render_template('index.html', expenses=expenses, total=total, error=error)

@app.route('/add', methods=['POST'])
def add_expense():
    category = request.form.get('category')
    description = request.form.get('description')
    amount = request.form.get('amount')
    date = request.form.get('date')

    # Basic Edge Case Validation
    if not category or not description or not date:
        return redirect(url_for('index', error="All fields are required."))

    try:
        amount = float(amount)
        if amount <= 0:
            return redirect(url_for('index', error="Amount must be greater than 0."))
    except ValueError:
        return redirect(url_for('index', error="Invalid amount format."))

    # Save to SQLite
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO expenses (category, description, amount, date) VALUES (?, ?, ?, ?)',
        (category, description, amount, date)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
