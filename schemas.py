"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# Brand-specific persistent data

class Testimonial(BaseModel):
    """
    Testimonials from clients
    Collection: "testimonial"
    """
    name: str = Field(..., description="Client first name or alias")
    location: Optional[str] = Field(None, description="Client city/state")
    message: str = Field(..., description="Their experience in their own words")
    rating: Optional[int] = Field(5, ge=1, le=5, description="Star rating 1-5")
    service: Optional[str] = Field(None, description="Service they used")
    featured: bool = Field(False, description="Highlight on homepage")

class BlogPost(BaseModel):
    """
    Long-form educational content
    Collection: "blogpost"
    """
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    tags: List[str] = []
    published: bool = True
    published_at: Optional[datetime] = None

class Lead(BaseModel):
    """
    Contact/consultation requests
    Collection: "lead"
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: Optional[str] = None
    source: Optional[str] = Field("website", description="Where the lead came from")
    service_interest: Optional[str] = None

# Example generic collections retained for reference
class User(BaseModel):
    name: str
    email: EmailStr
    address: Optional[str] = None
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
