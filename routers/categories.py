import sqlite3
from fastapi import HTTPException, APIRouter, status, Body
from database import get_db_connection
router = APIRouter(tags=["Categories"])
@router.post("/categories/create")
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
@router.get("/categories")
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
@router.get("/categories/{category_id}")
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
@router.put("/categories/{category_id}", status_code=status.HTTP_200_OK)
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
@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
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
