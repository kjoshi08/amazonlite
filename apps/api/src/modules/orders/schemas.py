from pydantic import BaseModel
from typing import List


class OrderItemResponse(BaseModel):
    product_id: int
    sku: str
    name: str
    qty: int
    unit_price_cents: int
    line_total_cents: int


class OrderResponse(BaseModel):
    id: int
    user_id: str
    status: str
    total_cents: int
    currency: str
    items: List[OrderItemResponse]
