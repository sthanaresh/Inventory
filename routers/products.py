import re
import sqlite3
from fastapi import HTTPException, status, Body, APIRouter
from pydantic import BaseModel, Field
from database import get_db_connection
from repositories.product_repository import create_products as create_product_db, get_all_products, update_products, delete_products,get_product_by_name

router = APIRouter(tags=["Products"])

class ProductsDetails(BaseModel):
    name: str = Field(min_length=1)
    id: int
    price: float
    stock_quantity: int
    category: str = Field(min_length=1)

class CreateProductRequest(BaseModel):
    name: str = Field(min_length=1)
    price: float
    stock_quantity: int
    category: str = Field(min_length=1)

class ProductResponse(BaseModel):
    name: str = Field(min_length=1)
    price: float
    stock_quantity: int
    available:bool


class UpdateProductResponse(BaseModel):
    name: str
    category: str

class ProductByCategoryResponse(BaseModel):
    name: str
    price: float
    stock_quantity: int

class LowStockResponse(BaseModel):
    message: str
    total_products: int
    products:list

@router.post("/products/create", status_code=status.HTTP_201_CREATED)
def create_products(product_name: CreateProductRequest):
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
    result=create_product_db(product_name)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category does not exist"
        )
    return {
        "message": "Product created successfully",
        "product": result
    }



@router.get("/products/", status_code=status.HTTP_200_OK)
def get_all_products_route()->list[ProductResponse]:
    result_all_product=get_all_products()
    products_list = []
    for product in result_all_product:
        products_list.append(ProductResponse(
            name=product["name"],
            price=product["price"],
            stock_quantity=product["stock_quantity"],
            available=product["stock_quantity"] > 0,
        ))
    return products_list

@router.put("/products/{product_id}", status_code=status.HTTP_200_OK)
def update_products_route(product_id: int, product_name: ProductsDetails = Body(...)):
    if product_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Product id is invalid"
        )
    try:
        update_products(product_id, product_name)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail= str(e)
        )

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_products_route(product_id: int):
    if product_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Product id is invalid"
        )
    try:
        delete_products(product_id)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
# Search products by name

@router.get("/products/{product_name}", status_code=status.HTTP_200_OK)
def get_product_by_name_route(product_name: str) -> ProductsDetails:

    if not product_name or not product_name.strip() or not re.fullmatch(r"[a-zA-Z\s-]+", product_name):
        raise HTTPException(
            status_code=400,
            detail="Bad Request!"
        )
    product_found = get_product_by_name(product_name)
    if not product_found:
        raise HTTPException(
            status_code=404,
            detail="Not found! Product name does not exist"
        )
    return ProductsDetails(
        id=product_found[0],
        name=product_found[1],
        price=product_found[2],
        stock_quantity=product_found[3],
        category=product_found[4],
    )
# Filter products by category.
@router.get("/products/{category_name}/", status_code=status.HTTP_200_OK)
def get_product_by_category(category_name: str)->list[ProductByCategoryResponse]:
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

    return[
        ProductByCategoryResponse(
            name=row[1],
            price=row[2],
            stock_quantity=row[3],
        )
        for row in product_by_category
    ]
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
def get_product_low_stock()->LowStockResponse:
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
            "product_name": product[1],
            "stock_quantity": product[3],
            "category": product[4]
        })
    return LowStockResponse (
        message="Low-stock products retrieved successfully",
        total_products= len(products),
        products= products
    )
