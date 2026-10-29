# Create, view, update and delete categories.
# Category names must be unique.
# 2. Products
#
# Create, view, update and delete products.
# Each product has a name, price, stock quantity and category.
# Search products by name.
# Filter products by category.
# Find products with low stock.
# Increase or decrease stock quantity.
# Hints
# Design the database tables and relationships first.
# Decide which API endpoints are needed, including HTTP methods and URLs.
# Implement one feature at a time using SQL.
# Test your API with Swagger.
# Handle errors such as duplicate categories, missing products and invalid stock quantities.
# Use Git and commit your work regularly.
# You may use AI to generate a simple UI for testing your API.
import sqlite3
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status, Body

app = FastAPI()


def get_db_connection():
    return sqlite3.connect('/home/naresh/Inventory/InventoryManagement.db')


class CategoriesDetails(BaseModel):
    name: str = Field(min_length=1)
    id: int

class ProductsDetails(BaseModel):
    name: str = Field(min_length=1)
    id:int
    price: float
    stock_quantity: int
    category: str=Field(min_length=1)

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

create_database()

@app.post("/categories/create")
def create_categories(category_name: CategoriesDetails):
    if not category_name.name.strip():
        raise HTTPException(
            status_code=400,
            detail="Name is required"
        )

    connection = get_db_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("""
    SELECT *
    FROM Category
    WHERE name =?
    """,(category_name.name,))
    found_name= cursor.fetchone()
    if found_name:
        raise HTTPException(
            status_code=400,
            detail="Name already exists"
        )

    cursor.execute("""
    INSERT INTO Category (
                         Name)
                     VALUES ( ? );                   
                   """,(category_name.name,),)

    connection.commit()
    connection.close()
    return {"message": f"{category_name.name} category created successfully"}

@app.get("/categories")
def getAll_categories():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT *
    FROM Category
    """)
    categories = cursor.fetchall()
    connection.close()
    return categories

@app.get("/categories/{category_id}")
def getCategory_by_id(category_id: int):
    if not category_id:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category id is required")
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT *
    FROM Category
    WHERE id = ?
    """,(category_id,))
    category = cursor.fetchone()
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category does not exist"
        )
    connection.close()
    return category

@app.put("/categories/{category_id}",status_code=status.HTTP_200_OK)
def update_category(category_id: int, category_name: str = Body(...)):
    print(f"User input:{category_name}")
    if category_id<1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category id is required"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    select * from Category where id = ?
    """,(category_id,))
    category_found = cursor.fetchone()
    print(category_found)
    if not category_found:
        raise HTTPException(
            status_code=404,
            detail="Not found! Category does not exist"
        )
    cursor.execute("""
                   update Category
                   set Name=?
                   where id=?               
                   """,(category_name,category_id))
    updated_category=cursor.fetchone()
    connection.commit()
    print(update_category)
    connection.commit()
    connection.close()

@app.delete("/categories/{category_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int):
    if category_id<1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category id is not valid"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    delete from Category where id = ?
    """,(category_id,))
    connection.commit()
    connection.close()

# Implementing products
