import sqlite3

from database import get_db_connection


def create_category(category_name: str):
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT *
            FROM Category
            WHERE name = ?
        """, (category_name,))
        found_name = cursor.fetchone()
        if found_name:
            return "already_exists"
        cursor.execute("""
            INSERT INTO Category (Name)
            VALUES (?)
        """, (category_name,))
        connection.commit()
        return "success"
    finally:
        connection.close()


def get_all_categories():
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT *
            FROM Category
        """)
        categories = cursor.fetchall()
        return categories
    finally:
        connection.close()


def get_category_by_id(category_id: int):
    connection = get_db_connection()
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM Category
            WHERE id = ?
        """, (category_id,))

        category = cursor.fetchone()

        return category

    finally:
        connection.close()


def update_category(category_id: int, category_name: str):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        # Check whether category exists
        cursor.execute("""
            SELECT *
            FROM Category
            WHERE id = ?
        """, (category_id,))

        category_found = cursor.fetchone()

        if not category_found:
            return "not_found"

        # Check whether another category has the same name
        cursor.execute("""
            SELECT *
            FROM Category
            WHERE Name = ?
            AND id != ?
        """, (category_name, category_id))

        if cursor.fetchone():
            return "already_exists"

        # Update category
        cursor.execute("""
            UPDATE Category
            SET Name = ?
            WHERE id = ?
        """, (category_name, category_id))

        connection.commit()

        return "success"

    finally:
        connection.close()


def delete_category_by_id(category_id: int):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM Category
            WHERE id = ?
        """, (category_id,))
        if cursor.rowcount == 0:
            return False
        connection.commit()
        return True
    finally:
        connection.close()
