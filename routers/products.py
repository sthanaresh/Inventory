from fastapi import HTTPException, FastAPI, status, Body, APIRouter
from pydantic import BaseModel, Field
from database import get_db_connection
router = APIRouter(tags=["Products"])

class ProductsDetails(BaseModel):
    name: str = Field(min_length=1)
    id: int
    price: float
    stock_quantity: int
    category: str = Field(min_length=1)
@router.post("/products/create", status_code=status.HTTP_201_CREATED)
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
@router.get("/products/", status_code=status.HTTP_200_OK)
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
@router.put("/products/{product_id}", status_code=status.HTTP_200_OK)
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
@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
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
@router.get("/products/{product_name}", status_code=status.HTTP_200_OK)
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
@router.get("/products/{category_name}/", status_code=status.HTTP_200_OK)
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
@router.put("/products/increase-stock/", status_code=status.HTTP_200_OK)
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
@router.put("/products/decrease-stock/", status_code=status.HTTP_200_OK)
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
@router.get("/products/low-stock/items", status_code=status.HTTP_200_OK)
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
