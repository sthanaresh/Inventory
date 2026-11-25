import sqlite3
from database import get_db_connection

def create_products(product_name):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT *
            FROM Category
            WHERE name =?
            """, (product_name.category,))
        category_found = cursor.fetchone()
        if not category_found:
            raise Exception("Category not found")

        cursor.execute("""
               INSERT INTO Products (Category, Stock_Quantity, Price, Name)
                                VALUES (?, ?, ?, ?)""",
                       (product_name.category,
                        product_name.stock_quantity,
                        product_name.price,
                        product_name.name))
        product_id = cursor.lastrowid
        connection.commit()
        cursor.execute("""
                       SELECT *
                       FROM Products
                       WHERE id = ?
                   """, (product_id,))

        product_details = cursor.fetchone()

        return product_details
    finally:
        connection.close()

def get_all_products():
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.cursor()
        cursor.execute("""
                       select * from Products        
                       """)
        all_products = cursor.fetchall()
        if all_products is None:
            return[]
        cursor.close()
        return all_products
    finally:
        connection.close()

def update_products(product_id,product_name):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
                SELECT *
                FROM Products
                WHERE id = ?
                """, (product_id,))
        product_found = cursor.fetchone()
        if product_found is None:
            raise Exception("Product id not found")

        cursor.execute("""
              UPDATE Products
              SET Name=?, price=?, stock_quantity=?, category=?
              where id=?
              """, (product_name.name, product_name.price, product_name.stock_quantity, product_name.category,
                    product_id))
        connection.commit()
    finally:
        connection.close()

def delete_products(product_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM Products
            WHERE id = ?
        """, (product_id,))

        if cursor.rowcount == 0:
            raise Exception("Product id not found")

        connection.commit()

    finally:
        connection.close()

def get_product_by_name(product_name):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM Products
            WHERE LOWER(name) = LOWER(?)
        """, (product_name,))

        product_found = cursor.fetchone()

        if not product_found:
            return None
        return product_found
    finally:
        connection.close()

def get_product_by_category(category_name: str):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM Products
            WHERE LOWER(category) = LOWER(?)
        """, (category_name,))

        product_by_category = cursor.fetchall()

        if not product_by_category:
            return []
        return product_by_category
    finally:
        connection.close()

def increase_stock(product_id: int, quantity_to_add: int):

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Products
            SET stock_quantity = stock_quantity + ?
            WHERE id = ?
        """, (quantity_to_add, product_id))

        if cursor.rowcount == 0:
            return False

        connection.commit()

        return True

    finally:
        connection.close()


def decrease_stock(product_id: int, quantity_to_decrease: int):

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE Products
            SET stock_quantity = stock_quantity - ?
            WHERE id = ?
            AND stock_quantity >= ?
        """, (quantity_to_decrease, product_id, quantity_to_decrease))

        if cursor.rowcount == 0:
            return False

        connection.commit()

        return True

    finally:
        connection.close()


def get_product_low_stock():

    connection = get_db_connection()
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM Products
            WHERE stock_quantity <= 5
        """)

        product_low_stock = cursor.fetchall()

        return product_low_stock

    finally:
        connection.close()


