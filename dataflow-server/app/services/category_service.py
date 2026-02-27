from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryOut
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    """
    Service layer for category business logic.
    Handles validation, authorization, and orchestration.
    """

    @staticmethod
    async def create_category(data: CategoryCreate, db: AsyncSession) -> CategoryOut:
        """
        Create a new category with validation.
        
        Args:
            data: CategoryCreate schema with category details
            db: AsyncSession for database operations
            
        Raises:
            HTTPException: If slug already exists or parent category not found
            
        Returns:
            CategoryOut schema with created category data
        """
        # Check if slug already exists
        if await CategoryRepository.slug_exists(data.slug, db):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Slug '{data.slug}' already exists"
            )

        # Verify parent category exists if specified
        if data.parent_id:
            parent = await CategoryRepository.get_by_id(data.parent_id, db)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category with ID {data.parent_id} not found"
                )

        try:
            category = await CategoryRepository.create(data, db)
            return CategoryOut.model_validate(category)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create category: {str(e)}"
            )

    @staticmethod
    async def get_category(category_id: int, db: AsyncSession) -> CategoryOut:
        """
        Get category by ID.
        
        Raises:
            HTTPException: If category not found
            
        Returns:
            CategoryOut schema with category data
        """
        category = await CategoryRepository.get_by_id(category_id, db)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )
        return CategoryOut.model_validate(category)

    @staticmethod
    async def get_category_with_children(category_id: int, db: AsyncSession) -> dict:
        """
        Get category by ID with nested subcategories.
        
        Raises:
            HTTPException: If category not found
            
        Returns:
            Dictionary with category data and nested children
        """
        category = await CategoryRepository.get_by_id(category_id, db)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )

        # Fetch children separately
        children = await CategoryRepository.get_children(category_id, db)
        
        result = CategoryOut.model_validate(category).model_dump()
        result["children"] = [CategoryOut.model_validate(child).model_dump() for child in children]
        return result

    @staticmethod
    async def list_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> list:
        """
        List all top-level categories (without parent).
        
        Args:
            db: AsyncSession for database operations
            skip: Number of results to skip (pagination)
            limit: Maximum number of results
            
        Returns:
            List of CategoryOut schemas
        """
        categories = await CategoryRepository.get_all(db, skip, limit)
        return [CategoryOut.model_validate(cat) for cat in categories]

    @staticmethod
    async def list_categories_tree(db: AsyncSession) -> list:
        """
        List all top-level categories with nested children structure.
        
        Args:
            db: AsyncSession for database operations
            
        Returns:
            List of dictionaries with category data and nested children
        """
        categories = await CategoryRepository.get_all_with_children(db)
        
        result = []
        for cat in categories:
            cat_data = CategoryOut.model_validate(cat).model_dump()
            # Fetch children separately
            children = await CategoryRepository.get_children(cat.id, db)
            cat_data["children"] = [CategoryOut.model_validate(child).model_dump() for child in children]
            result.append(cat_data)
        
        return result

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
            data: CategoryUpdate schema with new values
            db: AsyncSession for database operations
            
        Raises:
            HTTPException: If category not found, slug exists, or parent not found
            
        Returns:
            CategoryOut schema with updated category data
        """
        category = await CategoryRepository.get_by_id(category_id, db)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )

        # Check if new slug already exists (if being changed)
        if data.slug and data.slug != category.slug:
            if await CategoryRepository.slug_exists(data.slug, db, exclude_id=category_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Slug '{data.slug}' already exists"
                )

        # Verify parent category exists if being changed
        if data.parent_id is not None and data.parent_id != category.parent_id:
            parent = await CategoryRepository.get_by_id(data.parent_id, db)
            if not parent and data.parent_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category with ID {data.parent_id} not found"
                )

        try:
            updated_category = await CategoryRepository.update(category, data, db)
            return CategoryOut.model_validate(updated_category)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update category: {str(e)}"
            )

    @staticmethod
    async def delete_category(category_id: int, db: AsyncSession) -> dict:
        """
        Delete a category.
        
        Args:
            category_id: ID of category to delete
            db: AsyncSession for database operations
            
        Raises:
            HTTPException: If category not found or has children
            
        Returns:
            Dictionary with deletion message
        """
        category = await CategoryRepository.get_by_id(category_id, db)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )

        # Check if category has children
        children = await CategoryRepository.get_children(category_id, db)
        if children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category with {len(children)} subcategories. "
                       "Please move or delete child categories first."
            )

        try:
            await CategoryRepository.delete(category, db)
            return {"message": f"Category '{category.name}' deleted successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete category: {str(e)}"
            )
