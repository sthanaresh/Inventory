import re
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection, create_database
import sqlite3
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class CategoriesDetails(BaseModel):
    name: str = Field(min_length=1)
    id: int


class ProductsDetails(BaseModel):
    name: str = Field(min_length=1)
    id: int
    price: float
    stock_quantity: int
    category: str = Field(min_length=1)


@app.post("/categories/create")
def create_categories(category_name: str):
    if not category_name.strip():
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
    """, (category_name,))
    found_name = cursor.fetchone()
    if found_name:
        raise HTTPException(
            status_code=400,
            detail="Name already exists"
        )

    cursor.execute("""
    INSERT INTO Category (
                         Name)
                     VALUES ( ? );                   
                   """, (category_name,), )

    connection.commit()
    connection.close()
    return {"message": f"{category_name} category created successfully"}


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
            "id": category[0],
            "name": category[1],
        })
    return categories_all


@app.get("/categories/{category_id}")
def getCategory_by_id(category_id: int):
    if category_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category id is required")
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT *
    FROM Category
    WHERE id = ?
    """, (category_id,))
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


@app.put("/categories/{category_id}", status_code=status.HTTP_200_OK)
def update_category(category_id: int, category_name: str = Body(...)):
    print(f"User input:{category_name}")
    if category_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category id is required"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    select * from Category where id = ?
    """, (category_id,))
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
                   """, (category_name, category_id))
    updated_category = cursor.fetchone()
    connection.commit()
    print(update_category)
    connection.commit()
    connection.close()


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int):
    if category_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category id is not valid"
        )
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    delete from Category where id = ?
    """, (category_id,))
    connection.commit()
    connection.close()
    return None


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
    """, (product_name.category,))
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
    all_products = cursor.fetchall()
    connection.close()
    products_list = []
    for product in all_products:
        products_list.append({
            "product id": product[0],
            "product name": product[1],
            "product price": product[2],
            "product stock quantity": product[3],
            "product category": product[4]
        })
    return products_list


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
    return {
        "product id": product_found[0],
        "product name": product_found[1],
        "product price": product_found[2],
        "product stock quantity": product_found[3],
        "product category": product_found[4]
    }


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
    category_total = []
    for category in product_by_category:
        category_total.append({
            "product id": category[0],
            "product name": category[1],
            "product price": category[2],
            "product stock quantity": category[3],
            "product category": category[4]
        })
    return category_total


# increase stock quantity
@app.put("/products/increase-stock/", status_code=status.HTTP_200_OK)
def increase_stock(product_id: int, quantity_to_add: int):
    if product_id < 1 or quantity_to_add < 1:
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
