from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db.category_model import Category
from app.models.schemas.category_schema import CategoryCreate, CategoryUpdate


class CategoryRepository:
    """
    Repository for Category database operations.
    Handles all async database queries related to categories.
    """

    @staticmethod
    async def create(data: CategoryCreate, db: AsyncSession) -> Category:
        """
        Create a new category.
        
        Args:
            data: CategoryCreate schema with category details
            db: AsyncSession for database operations
            
        Returns:
            Created Category object
        """
        # Verify parent category exists if parent_id is provided
        if data.parent_id:
            parent = await CategoryRepository.get_by_id(data.parent_id, db)
            if not parent:
                raise ValueError(f"Parent category with ID {data.parent_id} not found")

        db_category = Category(
            name=data.name,
            slug=data.slug,
            description=data.description,
            parent_id=data.parent_id
        )
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return db_category

    @staticmethod
    async def get_by_id(category_id: int, db: AsyncSession) -> Optional[Category]:
        """
        Get category by ID.
        
        Args:
            category_id: ID of category to retrieve
            db: AsyncSession for database operations
            
        Returns:
            Category object or None if not found
        """
        result = await db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_slug(slug: str, db: AsyncSession) -> Optional[Category]:
        """
        Get category by slug.
        
        Args:
            slug: Slug of category to retrieve
            db: AsyncSession for database operations
            
        Returns:
            Category object or None if not found
        """
        result = await db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_slug_with_children(slug: str, db: AsyncSession) -> Optional[Category]:
        """
        Get category by slug with nested subcategories.
        
        Args:
            slug: Slug of category to retrieve
            db: AsyncSession for database operations
            
        Returns:
            Category object or None if not found
        """
        result = await db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list:
        """
        Get all top-level categories (no parent).
        
        Args:
            db: AsyncSession for database operations
            skip: Number of results to skip (pagination)
            limit: Maximum number of results to return
            
        Returns:
            List of Category objects
        """
        result = await db.execute(
            select(Category)
            .where(Category.parent_id.is_(None))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all_with_children(db: AsyncSession) -> list:
        """
        Get all top-level categories with nested subcategories.
        
        Args:
            db: AsyncSession for database operations
            
        Returns:
            List of Category objects
        """
        result = await db.execute(
            select(Category)
            .where(Category.parent_id.is_(None))
        )
        return list(result.scalars().all())

    @staticmethod
    async def update(category: Category, data: CategoryUpdate, db: AsyncSession) -> Category:
        """
        Update an existing category.
        
        Args:
            category: Category object to update
            data: CategoryUpdate schema with new values
            db: AsyncSession for database operations
            
        Returns:
            Updated Category object
        """
        # Verify parent category exists if parent_id is being changed
        if data.parent_id is not None and data.parent_id != category.parent_id:
            parent = await CategoryRepository.get_by_id(data.parent_id, db)
            if not parent:
                raise ValueError(f"Parent category with ID {data.parent_id} not found")

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)

        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete(category: Category, db: AsyncSession) -> None:
        """
        Delete a category.
        
        Args:
            category: Category object to delete
            db: AsyncSession for database operations
        """
        await db.delete(category)
        await db.commit()

    @staticmethod
    async def slug_exists(slug: str, db: AsyncSession, exclude_id: Optional[int] = None) -> bool:
        """
        Check if a slug already exists (excluding a specific category by ID).
        
        Args:
            slug: Slug to check
            db: AsyncSession for database operations
            exclude_id: Category ID to exclude from check (for updates)
            
        Returns:
            True if slug exists, False otherwise
        """
        query = select(Category).where(Category.slug == slug)
        if exclude_id:
            query = query.where(Category.id != exclude_id)
        
        result = await db.execute(query)
        return result.scalars().first() is not None

    @staticmethod
    async def get_children(category_id: int, db: AsyncSession) -> list:
        """
        Get all direct children of a category.
        
        Args:
            category_id: ID of parent category
            db: AsyncSession for database operations
            
        Returns:
            List of Category objects that are direct children
        """
        result = await db.execute(
            select(Category).where(Category.parent_id == category_id)
        )
        return list(result.scalars().all())
