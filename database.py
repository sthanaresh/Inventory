import sqlite3


def create_database():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT UNIQUE NOT NULL)
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Price NUMERIC NOT NULL,
            Stock_Quantity INTEGER NOT NULL DEFAULT 0,
            Category TEXT NOT NULL)
    """)
    connection.commit()
    print("Database connected successfully")
    print("All tables are ready")
    connection.close()


def get_db_connection():
    return sqlite3.connect('/home/naresh/Inventory/InventoryManagement.db')
