from typing import List, Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price_cents: int
    currency: str = "USD"
    stock_qty: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = None
    currency: Optional[str] = None
    stock_qty: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    price_cents: int
    currency: str
    stock_qty: int
    is_active: bool

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    limit: int
    offset: int
    total: int
