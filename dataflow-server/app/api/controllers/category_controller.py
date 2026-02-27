from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryOut
from app.services.category_service import CategoryService


class CategoryController:
    """
    Controller layer for category endpoints.
    Handles HTTP request/response and delegates to service logic.
    """

    @staticmethod
    async def create_category(data: CategoryCreate, db: AsyncSession) -> CategoryOut:
        """
        Create a new category.
        
        Args:
            data: CategoryCreate schema
            db: AsyncSession for database operations
            
        Returns:
            CategoryOut schema with created category
        """
        return await CategoryService.create_category(data, db)

    @staticmethod
    async def get_category(category_id: int, db: AsyncSession) -> CategoryOut:
        """
        Get a category by ID.
        
        Args:
            category_id: ID of category to retrieve
            db: AsyncSession for database operations
            
        Returns:
            CategoryOut schema
        """
        return await CategoryService.get_category(category_id, db)

    @staticmethod
    async def get_category_tree(category_id: int, db: AsyncSession) -> dict:
        """
        Get a category with nested subcategories.
        
        Args:
            category_id: ID of category to retrieve
            db: AsyncSession for database operations
            
        Returns:
            Dictionary with category and nested children
        """
        return await CategoryService.get_category_with_children(category_id, db)

    @staticmethod
    async def list_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> list:
        """
        List all top-level categories.
        
        Args:
            db: AsyncSession for database operations
            skip: Pagination skip
            limit: Pagination limit
            
        Returns:
            List of CategoryOut schemas
        """
        return await CategoryService.list_categories(db, skip, limit)

    @staticmethod
    async def list_categories_tree(db: AsyncSession) -> list:
        """
        List all top-level categories with nested children structure.
        
        Args:
            db: AsyncSession for database operations
            
        Returns:
            List of categories with nested children
        """
        return await CategoryService.list_categories_tree(db)

    @staticmethod
    async def update_category(
        category_id: int,
        data: CategoryUpdate,
        db: AsyncSession
    ) -> CategoryOut:
        """
        Update an existing category.
        
        Args:
            category_id: ID of category to update
            data: CategoryUpdate schema
            db: AsyncSession for database operations
            
        Returns:
            Updated CategoryOut schema
        """
        return await CategoryService.update_category(category_id, data, db)

    @staticmethod
    async def delete_category(category_id: int, db: AsyncSession) -> dict:
        """
        Delete a category.
        
        Args:
            category_id: ID of category to delete
            db: AsyncSession for database operations
            
        Returns:
            Dictionary with deletion message
        """
        return await CategoryService.delete_category(category_id, db)
