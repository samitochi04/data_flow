from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryOut
from app.api.controllers.category_controller import CategoryController

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new category (admin only).
    
    - **name**: Category name (required)
    - **slug**: URL-friendly slug (required, must be unique)
    - **description**: Optional category description
    - **parent_id**: Optional ID of parent category for nesting
    """
    return await CategoryController.create_category(payload, db)


@router.get("", response_model=list)
async def list_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    List all top-level categories with pagination.
    
    - **skip**: Number of results to skip (pagination)
    - **limit**: Maximum number of results to return (1-100)
    """
    return await CategoryController.list_categories(db, skip, limit)


@router.get("/tree", response_model=list)
async def list_categories_tree(
    db: AsyncSession = Depends(get_db)
):
    """
    List all top-level categories with nested children structure.
    
    Returns categories organized hierarchically with all subcategories populated.
    """
    return await CategoryController.list_categories_tree(db)


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific category by ID.
    """
    return await CategoryController.get_category(category_id, db)


@router.get("/{category_id}/tree", response_model=dict)
async def get_category_tree(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a category with all its nested subcategories.
    
    Returns the category data along with all direct and nested children.
    """
    return await CategoryController.get_category_tree(category_id, db)


@router.put("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing category (admin only).
    
    Allows updating name, slug, description, and parent category.
    """
    return await CategoryController.update_category(category_id, payload, db)


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a category (admin only).
    
    Cannot delete categories that have subcategories.
    Delete child categories first, then delete parent.
    """
    return await CategoryController.delete_category(category_id, db)
