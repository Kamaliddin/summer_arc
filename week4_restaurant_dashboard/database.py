import sqlite3

def get_connection():
    conn = sqlite3.connect('restaurant.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS targets (
            day TEXT PRIMARY KEY,
            revenue_target INTEGER,
            customers_target INTEGER
        );

        CREATE TABLE IF NOT EXISTS daily_revenue (
            date TEXT PRIMARY KEY,
            revenue INTEGER,
            customers INTEGER
        );

        INSERT OR IGNORE INTO targets VALUES ('Monday', 700000, 40);
        INSERT OR IGNORE INTO targets VALUES ('Tuesday', 700000, 40);
        INSERT OR IGNORE INTO targets VALUES ('Wednesday', 700000, 40);
        INSERT OR IGNORE INTO targets VALUES ('Thursday', 700000, 40);
        INSERT OR IGNORE INTO targets VALUES ('Friday', 900000, 55);
        INSERT OR IGNORE INTO targets VALUES ('Saturday', 900000, 55);
        INSERT OR IGNORE INTO targets VALUES ('Sunday', 800000, 50);

        INSERT OR IGNORE INTO daily_revenue VALUES ('2024-01-15', 520000, 32);
        INSERT OR IGNORE INTO daily_revenue VALUES ('2024-01-16', 640000, 38);
        INSERT OR IGNORE INTO daily_revenue VALUES ('2024-01-17', 480000, 28);
        INSERT OR IGNORE INTO daily_revenue VALUES ('2024-01-18', 710000, 45);
        INSERT OR IGNORE INTO daily_revenue VALUES ('2024-01-19', 390000, 22);
        INSERT OR IGNORE INTO daily_revenue VALUES ('2024-01-20', 640000, 39);
        INSERT OR IGNORE INTO daily_revenue VALUES ('2024-01-21', 850000, 47);
    ''')
    conn.commit()
    conn.close()

def get_targets(day):
    conn = get_connection()
    target = conn.execute(
        'SELECT * FROM targets WHERE day = ?', (day,)
    ).fetchone()
    conn.close()
    return dict(target) if target else None

def update_target(day, revenue, customers):
    conn = get_connection()
    conn.execute(
        'UPDATE targets SET revenue_target=?, customers_target=? WHERE day=?',
        (revenue, customers, day)
    )
    conn.commit()
    conn.close()

def get_weekly_revenue():
    conn = get_connection()
    rows = conn.execute(
        'SELECT * FROM daily_revenue ORDER BY date DESC LIMIT 7'
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def update_today(revenue, customers):
    from datetime import date
    today = date.today().isoformat()
    conn = get_connection()
    conn.execute(
        'INSERT OR REPLACE INTO daily_revenue VALUES (?, ?, ?)',
        (today, revenue, customers)
    )
    conn.commit()
    conn.close()