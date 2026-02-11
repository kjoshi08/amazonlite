from pydantic import BaseModel, Field


class CartAddItemRequest(BaseModel):
    product_id: int
    qty: int = Field(..., ge=1, le=50)


class CartSetQtyRequest(BaseModel):
    product_id: int
    qty: int = Field(..., ge=0, le=50)  # 0 = remove


class CartItem(BaseModel):
    product_id: int
    qty: int


class CartResponse(BaseModel):
    user_id: str
    items: list[CartItem]
