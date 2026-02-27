from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    """Base category fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    slug: str = Field(..., min_length=1, max_length=255, description="URL-friendly slug")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID for nesting")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None


class CategoryOut(CategoryBase):
    """Schema for returning category data"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryTree(CategoryOut):
    """Schema for returning nested category structure with children"""
    children: List["CategoryOut"] = []

    model_config = ConfigDict(from_attributes=True)


# Update forward references
CategoryTree.model_rebuild()
