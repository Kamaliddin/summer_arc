import sqlite3
import random
from datetime import date, datetime, timedelta

DB_PATH = 'restaurant.db'
SIMULATED_TODAY_WEEKDAY = 2  # Wednesday (Monday=0)


def get_simulated_today():
    """Treat Wednesday of the current calendar week as 'today'."""
    real_today = date.today()
    monday = real_today - timedelta(days=real_today.weekday())
    return monday + timedelta(days=SIMULATED_TODAY_WEEKDAY)


def get_simulated_today_name():
    return 'Wednesday'


def get_week_bounds():
    """Monday and Sunday dates for the week containing simulated today."""
    today = get_simulated_today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.executescript('''
        -- Targets per weekday
        CREATE TABLE IF NOT EXISTS targets (
            day TEXT PRIMARY KEY,
            revenue_target INTEGER,
            customers_target INTEGER
        );

        -- Daily revenue log
        CREATE TABLE IF NOT EXISTS daily_revenue (
            date TEXT PRIMARY KEY,
            revenue INTEGER,
            customers INTEGER
        );

        -- Employees
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            daily_earnings INTEGER DEFAULT 0
        );

        -- Table bookings
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY,
            status TEXT DEFAULT "empty",
            employee_id INTEGER,
            booked_at TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );

        -- Service ratings
        CREATE TABLE IF NOT EXISTS service_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            table_id INTEGER,
            rating REAL,
            revenue INTEGER,
            date TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );

        -- Seed weekday targets
        INSERT OR IGNORE INTO targets VALUES ("Monday",    600000, 40);
        INSERT OR IGNORE INTO targets VALUES ("Tuesday",   600000, 40);
        INSERT OR IGNORE INTO targets VALUES ("Wednesday", 600000, 40);
        INSERT OR IGNORE INTO targets VALUES ("Thursday",  600000, 40);
        INSERT OR IGNORE INTO targets VALUES ("Friday",    600000, 40);
        INSERT OR IGNORE INTO targets VALUES ("Saturday",  800000, 50);
        INSERT OR IGNORE INTO targets VALUES ("Sunday",    800000, 50);

        -- Seed demo employees
        INSERT OR IGNORE INTO employees (id, name, role) VALUES (1, "Akbar",  "Waiter");
        INSERT OR IGNORE INTO employees (id, name, role) VALUES (2, "Leila",  "Waitress");
        INSERT OR IGNORE INTO employees (id, name, role) VALUES (3, "Jamil",  "Waiter");
        INSERT OR IGNORE INTO employees (id, name, role) VALUES (4, "Nodira", "Waitress");

        -- Seed 20 tables all empty
        INSERT OR IGNORE INTO tables (id, status) VALUES (1,  "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (2,  "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (3,  "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (4,  "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (5,  "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (6,  "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (7,  "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (8,  "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (9,  "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (10, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (11, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (12, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (13, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (14, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (15, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (16, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (17, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (18, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (19, "empty");
        INSERT OR IGNORE INTO tables (id, status) VALUES (20, "empty");
    ''')
    conn.commit()
    conn.close()

# ── TARGETS ────────────────────────────────────────
def get_targets(day):
    conn = get_connection()
    row = conn.execute('SELECT * FROM targets WHERE day=?', (day,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_target(day, revenue, customers):
    conn = get_connection()
    conn.execute('UPDATE targets SET revenue_target=?, customers_target=? WHERE day=?',
                 (revenue, customers, day))
    conn.commit()
    conn.close()

# ── REVENUE ─────────────────────────────────────────
def get_weekly_revenue():
    """Get current week's revenue (Monday-Sunday) in order."""
    conn = get_connection()
    monday, sunday = get_week_bounds()
    rows = conn.execute(
        'SELECT * FROM daily_revenue WHERE date >= ? AND date <= ? ORDER BY date ASC',
        (monday.isoformat(), sunday.isoformat())
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_today_revenue_row():
    """Revenue and guests for simulated today (Wednesday)."""
    conn = get_connection()
    today = get_simulated_today().isoformat()
    row = conn.execute('SELECT * FROM daily_revenue WHERE date=?', (today,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {'date': today, 'revenue': 0, 'customers': 0}


def update_today_revenue(revenue, customers):
    today = get_simulated_today().isoformat()
    conn = get_connection()
    conn.execute(
        'INSERT OR REPLACE INTO daily_revenue VALUES (?,?,?)',
        (today, revenue, customers)
    )
    conn.commit()
    conn.close()

# ── EMPLOYEES ───────────────────────────────────────
def get_all_employees():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_employee_stats(employee_id):
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM service_ratings WHERE employee_id=? AND date=?',
        (employee_id, get_simulated_today().isoformat())
    ).fetchall()
    conn.close()
    ratings = [r['rating'] for r in rows]
    avg_rating = round(sum(ratings)/len(ratings), 1) if ratings else 0
    orders = len(rows)
    earnings = sum(int(r['revenue'] * 0.05) for r in rows)
    return {'orders': orders, 'rating': avg_rating, 'earnings': earnings}

# ── TABLES ──────────────────────────────────────────
def get_all_tables():
    conn = get_connection()
    rows = conn.execute('''
        SELECT t.*, e.name as employee_name, e.role as employee_role
        FROM tables t
        LEFT JOIN employees e ON t.employee_id = e.id
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def book_table(table_id, employee_id):
    conn = get_connection()
    conn.execute(
        'UPDATE tables SET status="occupied", employee_id=?, booked_at=? WHERE id=?',
        (employee_id, datetime.now().isoformat(), table_id)
    )
    conn.commit()
    conn.close()

def clear_table(table_id, rating, revenue):
    conn = get_connection()
    today = get_simulated_today().isoformat()
    table = conn.execute('SELECT * FROM tables WHERE id=?', (table_id,)).fetchone()
    if table and table['employee_id']:
        commission = int(revenue * 0.05)
        conn.execute('''
            INSERT INTO service_ratings (employee_id, table_id, rating, revenue, date)
            VALUES (?,?,?,?,?)
        ''', (table['employee_id'], table_id, rating,
              revenue, today))
        conn.execute(
            'UPDATE employees SET daily_earnings = daily_earnings + ? WHERE id=?',
            (commission, table['employee_id'])
        )
    # Update daily revenue with the payment
    daily = conn.execute('SELECT * FROM daily_revenue WHERE date=?', (today,)).fetchone()
    if daily:
        current_rev = daily['revenue']
        current_cust = daily['customers']
        conn.execute(
            'UPDATE daily_revenue SET revenue=?, customers=? WHERE date=?',
            (current_rev + revenue, current_cust + 1, today)
        )
    else:
        conn.execute(
            'INSERT INTO daily_revenue VALUES (?,?,?)',
            (today, revenue, 1)
        )
    conn.execute(
        'UPDATE tables SET status="empty", employee_id=NULL, booked_at=NULL WHERE id=?',
        (table_id,)
    )
    conn.commit()
    conn.close()

# ── RESET TODAY'S DATA ──────────────────────────────
def reset_today_data():
    today = get_simulated_today().isoformat()
    conn = get_connection()
    conn.execute('DELETE FROM daily_revenue WHERE date=?', (today,))
    conn.execute('DELETE FROM service_ratings WHERE date=?', (today,))
    conn.execute('UPDATE employees SET daily_earnings=0')
    conn.execute('UPDATE tables SET status="empty", employee_id=NULL, booked_at=NULL')
    conn.commit()
    conn.close()

# ── ENSURE WEEKLY REVENUE ───────────────────────────
def ensure_weekly_revenue():
    """Seed Mon/Tue with random revenue; Wed (today) and later days at zero."""
    conn = get_connection()
    monday, sunday = get_week_bounds()
    mon_str, sun_str = monday.isoformat(), sunday.isoformat()

    wed_str = get_simulated_today().isoformat()
    conn.execute(
        'DELETE FROM daily_revenue WHERE date < ? OR date > ?',
        (mon_str, sun_str)
    )
    conn.execute(
        'DELETE FROM daily_revenue WHERE date >= ? AND date < ?',
        (mon_str, wed_str)
    )
    conn.execute(
        'DELETE FROM service_ratings WHERE date < ? OR date > ?',
        (mon_str, sun_str)
    )

    for i in range(7):
        d = monday + timedelta(days=i)
        d_str = d.isoformat()
        if i in (0, 1):
            rng = random.Random(d_str)
            rev = rng.randint(450000, 750000)
            cust = rng.randint(25, 45)
            conn.execute(
                'INSERT OR REPLACE INTO daily_revenue VALUES (?,?,?)',
                (d_str, rev, cust)
            )
            continue
        exists = conn.execute('SELECT 1 FROM daily_revenue WHERE date=?', (d_str,)).fetchone()
        if not exists:
            conn.execute('INSERT INTO daily_revenue VALUES (?,?,?)', (d_str, 0, 0))

    conn.commit()
    conn.close()
