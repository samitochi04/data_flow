from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TopicClusterBase(BaseModel):
    """Base topic cluster fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Topic cluster name")
    slug: str = Field(..., min_length=1, max_length=255, description="URL-friendly slug")
    pillar_post_id: Optional[int] = Field(None, description="ID of the pillar/main post for this cluster")


class TopicClusterCreate(TopicClusterBase):
    """Schema for creating a new topic cluster"""
    pass


class TopicClusterUpdate(BaseModel):
    """Schema for updating an existing topic cluster"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    pillar_post_id: Optional[int] = None


class TopicClusterOut(TopicClusterBase):
    """Schema for returning topic cluster data"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
