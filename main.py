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
    categories_all = []
    for category in categories:
        categories_all.append({
            "category_id": category[0],
            "category_name": category[1],
        })
    return {
        "message": "All categories retrieved successfully",
        "total categories": len(categories_all),
        "categories": categories_all
    }


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
    return {
        "category id": category[0],
        "category name": category[1]
    }


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

@app.post("/products/create", status_code=status.HTTP_201_CREATED)
def create_products(product_name: ProductsDetails):
    if (not product_name.name.strip()
            or not product_name.category.strip()
            or product_name.price is None
            or product_name.stock_quantity is None
            or product_name.stock_quantity < 0
            or product_name.price < 0):
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Product details are required"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT *
    FROM Category
    WHERE name =?
    """, (product_name.category, ))
    category_found = cursor.fetchone()
    if not category_found:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category does not exist"

        )
    cursor.execute("""
    INSERT INTO Products (Category, Stock_Quantity, Price, Name)
                     VALUES (?, ?, ?, ?)""",
                   (product_name.category,
                    product_name.stock_quantity,
                    product_name.price,
                    product_name.name))
    connection.commit()
    connection.close()

@app.get("/products/", status_code=status.HTTP_200_OK)
def get_all_products():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        select * from Products        
        """)
    connection.close()


@app.put("/products/{product_id}", status_code=status.HTTP_200_OK)
def update_products(product_id: int, product_name: ProductsDetails = Body(...)):
    if product_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Product id is invalid"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT *
    FROM Products
    WHERE id = ?
    """, (product_id,))
    product_found = cursor.fetchone()
    if not product_found:
        raise HTTPException(
            status_code=404,
            detail="Not found! Product id does not exist"
        )
    cursor.execute("""
    UPDATE Products
    SET Name=?, price=?, stock_quantity=?, category=?
    where id=?
    """, (product_name.name, product_name.price, product_name.stock_quantity, product_name.category, product_id))
    connection.commit()
    connection.close()


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_products(product_id: int):
    if product_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Product id is invalid"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    delete from Products
    where id = ?
    """, (product_id,))
    connection.commit()
    connection.close()

# Search products by name
@app.get("/products/{product_name}", status_code=status.HTTP_200_OK)
def get_product_by_name(product_name: str):
    if not product_name or not product_name.strip() or not re.fullmatch(r"[a-zA-Z\s-]+", product_name):
        raise HTTPException(
            status_code=400,
            detail="Bad Request!"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT *
    FROM Products
    WHERE LOWER(name) = LOWER(?)
    """, (product_name,))
    product_found = cursor.fetchone()
    if not product_found:
        raise HTTPException(
            status_code=404,
            detail="Not found! Product name does not exist"
        )


# Filter products by category.
@app.get("/products/{category_name}/", status_code=status.HTTP_200_OK)
def get_product_by_category(category_name: str):
    if not category_name or not category_name.strip() or not re.fullmatch(r"[a-zA-Z\s-]+", category_name):
        raise HTTPException(
            status_code=400,
            detail="Bad Request!"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT *
    FROM Products
    WHERE LOWER(category) = LOWER(?)
    """, (category_name,))
    product_by_category = cursor.fetchall()
    if not product_by_category:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category does not exist"
        )
    connection.close()


# increase stock quantity
@app.put("/products/increase-stock/", status_code=status.HTTP_200_OK)
def increase_stock(product_id: int, quantity_to_add: int):
    if not product_id or not quantity_to_add or product_id <= 0 or quantity_to_add <= 0:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Enter valid data"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    UPDATE Products
    SET stock_quantity = stock_quantity + ?
    WHERE id = ?
    """, (quantity_to_add, product_id))
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Product id not found "
        )
    connection.commit()
    connection.close()


# decrease stock quantity
@app.put("/products/decrease-stock/", status_code=status.HTTP_200_OK)
def decrease_stock(product_id: int, quantity_to_decrease: int):
    if not product_id or not quantity_to_decrease or product_id <= 0 or quantity_to_decrease <= 0:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Enter valid data"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    UPDATE Products
    SET stock_quantity = stock_quantity - ?
    WHERE id = ?
    AND stock_quantity >= ?    
    """, (quantity_to_decrease, product_id, quantity_to_decrease))
    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Product not found or insufficient stock")
    connection.commit()
    connection.close()


# Find products with low stock.
@app.get("/products/low-stock/items", status_code=status.HTTP_200_OK)
def get_product_low_stock():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT * from Products
    where stock_quantity <=5
    """)
    product_low_stock = cursor.fetchall()
    connection.close()
    if not product_low_stock:
        raise HTTPException(
            status_code=404,
            detail="No low-stock products found"
        )
    products = []

    for product in product_low_stock:
        products.append({
            "product_id": product[0],
            "product_name": product[1],
            "price": product[2],
            "stock_quantity": product[3],
            "category": product[4]
        })

    return {
        "message": "Low-stock products retrieved successfully",
        "total_products": len(products),
        "products": products
    }
