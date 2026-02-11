from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import Product
from src.modules.cart.schemas import (
    CartAddItemRequest,
    CartSetQtyRequest,
    CartItem,
    CartResponse,
)
from src.modules.cart.service import get_cart, add_item, set_qty, clear_cart

router = APIRouter(prefix="/cart", tags=["cart"])


def _cart_response(user_id: str, cart_dict: dict[str, int]) -> CartResponse:
    items = [CartItem(product_id=int(pid), qty=int(qty)) for pid, qty in cart_dict.items()]
    return CartResponse(user_id=user_id, items=items)


@router.get("", response_model=CartResponse)
def read_cart(user_id: str = Query(..., min_length=1)):
    cart = get_cart(user_id)
    return _cart_response(user_id, {k: int(v) for k, v in cart.items()})


@router.post("/items", response_model=CartResponse)
def add_cart_item(
    payload: CartAddItemRequest,
    user_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    # Validate product exists so cart doesn't contain invalid product IDs
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart = add_item(user_id, payload.product_id, payload.qty)
    return _cart_response(user_id, {k: int(v) for k, v in cart.items()})


@router.put("/items", response_model=CartResponse)
def set_cart_item_qty(
    payload: CartSetQtyRequest,
    user_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart = set_qty(user_id, payload.product_id, payload.qty)
    return _cart_response(user_id, {k: int(v) for k, v in cart.items()})


@router.delete("", response_model=dict)
def delete_cart(user_id: str = Query(..., min_length=1)):
    clear_cart(user_id)
    return {"deleted": True}
