from fastapi import HTTPException, APIRouter, status, Body

from database import get_db_connection
from repositories.category_repository import create_category, get_all_categories, get_category_by_id, update_category

router = APIRouter(tags=["Categories"])


@router.post("/categories/create", status_code=status.HTTP_200_OK)
def create_categories_route(category_name: str):
    if not category_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Name is required"
        )
    result = create_category(category_name)
    if result == "already_exists":
        raise HTTPException(
            status_code=400,
            detail="Name already exists"
        )
    return {
        "message": f"{category_name} category created successfully"
    }


@router.get("/categories", status_code=status.HTTP_200_OK)
def get_all_categories_route():
    categories = get_all_categories()
    categories_all = []
    for category in categories:
        categories_all.append({
            "id": category["id"],
            "name": category["name"],
        })
    return categories_all


@router.get("/categories/{category_id}", status_code=status.HTTP_200_OK)
def get_category_by_id_route(category_id: int):
    if category_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category id is required"
        )
    category = get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category does not exist"
        )
    return {
        "category id": category["id"],
        "category name": category["name"]
    }


@router.put("/categories/{category_id}", status_code=status.HTTP_200_OK)
def update_category_route(category_id: int, category_name: str = Body(...)):
    if category_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Bad Request! Category id is required"
        )
    if not category_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Category name is required"
        )
    result = update_category(category_id, category_name.strip())
    if result == "not_found":
        raise HTTPException(
            status_code=404,
            detail="Not found! Category does not exist"
        )
    if result == "already_exists":
        raise HTTPException(
            status_code=400,
            detail="Category name already exists"
        )
    return {
        "message": f"Category updated successfully to {category_name.strip()}"
    }


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
