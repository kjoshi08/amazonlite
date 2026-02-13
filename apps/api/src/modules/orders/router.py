from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import Order, OrderItem, OrderStatus, Product
from src.modules.cart.service import clear_cart
from src.modules.cart.service import get_cart as get_cart_map

router = APIRouter(prefix="/orders", tags=["orders"])


def _serialize_order(db: Session, order: Order) -> Dict[str, Any]:
    items: List[OrderItem] = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_cents": order.total_cents,
        "currency": order.currency,
        "created_at": str(order.created_at),
        "items": [
            {
                "product_id": it.product_id,
                "sku": it.sku,
                "name": it.name,
                "qty": it.qty,
                "unit_price_cents": it.unit_price_cents,
                "line_total_cents": it.line_total_cents,
            }
            for it in items
        ],
    }


@router.post("/checkout")
def checkout(
    user_id: str,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
):
    # ✅ 1) Idempotency FIRST (so retries work even if cart was cleared)
    if idempotency_key:
        existing = (
            db.query(Order)
            .filter(Order.user_id == user_id, Order.idempotency_key == idempotency_key)
            .first()
        )
        if existing:
            return _serialize_order(db, existing)

    # ✅ 2) Then read cart
    cart_dict = get_cart_map(user_id)  # Dict[str, int]
    if not cart_dict:
        raise HTTPException(status_code=400, detail="Cart is empty")

    try:
        order = Order(
            user_id=user_id,
            status=OrderStatus.CREATED.value,
            total_cents=0,
            currency="USD",
            idempotency_key=idempotency_key,
        )
        db.add(order)
        db.flush()  # assigns order.id

        total = 0
        for pid_str, qty in cart_dict.items():
            product_id = int(pid_str)
            qty = int(qty)

            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

            line_total = product.price_cents * qty
            total += line_total

            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    sku=product.sku,
                    name=product.name,
                    qty=qty,
                    unit_price_cents=product.price_cents,
                    line_total_cents=line_total,
                )
            )

        order.total_cents = total
        db.commit()
        db.refresh(order)

        # Clear cart best-effort after successful commit
        try:
            clear_cart(user_id)
        except Exception:
            pass

        return _serialize_order(db, order)

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        # race: return existing if constraint hit
        if idempotency_key:
            existing = (
                db.query(Order)
                .filter(Order.user_id == user_id, Order.idempotency_key == idempotency_key)
                .first()
            )
            if existing:
                return _serialize_order(db, existing)
        raise
    except Exception:
        db.rollback()
        raise


@router.get("/{order_id}")
def get_order(order_id: int, user_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(db, order)


@router.get("")
def list_orders(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .limit(limit)
        .all()
    )
    return {"orders": [_serialize_order(db, o) for o in orders]}


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, user_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == OrderStatus.PAID.value:
        raise HTTPException(status_code=400, detail="Paid order cannot be cancelled (refund not implemented)")
    if order.status == OrderStatus.CANCELLED.value:
        return {"detail": "Order already cancelled", "order_id": order.id}

    order.status = OrderStatus.CANCELLED.value
    db.commit()
    return {"detail": "Order cancelled", "order_id": order.id}
