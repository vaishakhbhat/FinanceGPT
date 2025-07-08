import sqlite3
from datetime import datetime

DB_NAME = "portfolio.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_trade(symbol, quantity, price):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO trades (symbol, quantity, price, timestamp)
        VALUES (?, ?, ?, ?)
    """, (symbol.upper(), quantity, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_portfolio():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT symbol,
               SUM(quantity) AS total_qty,
               CASE WHEN SUM(quantity) > 0 THEN
                   ROUND(SUM(quantity * price) / SUM(quantity), 2)
               ELSE 0 END AS avg_price
        FROM trades
        GROUP BY symbol
        HAVING total_qty > 0
    """)
    result = cur.fetchall()
    conn.close()
    return result

def remove_trade(symbol, quantity):
    """Handles selling a stock by inserting negative quantity trade"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO trades (symbol, quantity, price, timestamp)
        VALUES (?, ?, ?, ?)
    """, (symbol.upper(), -abs(quantity), 0, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def sell_stock(symbol, quantity):
    symbol = symbol.upper()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT SUM(quantity), SUM(quantity * price)
        FROM trades WHERE symbol = ?
    """, (symbol,))
    total_qty, total_value = cur.fetchone()

    if not total_qty or total_qty < quantity:
        conn.close()
        raise ValueError("Not enough shares to sell")

    avg_price = total_value / total_qty if total_qty else 0
    cur.execute("""
        INSERT INTO trades (symbol, quantity, price, timestamp)
        VALUES (?, ?, ?, ?)
    """, (symbol, -quantity, avg_price, datetime.now().isoformat()))

    conn.commit()
    conn.close()
