from __future__ import annotations

from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import Payment, PaymentStatus, Order, OrderStatus

router = APIRouter(prefix="/payments", tags=["payments"])


def _serialize_payment(payment: Payment) -> Dict[str, Any]:
    return {
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "provider": "mock",
        "status": payment.status,
        "amount_cents": payment.amount_cents,
        "currency": payment.currency,
        "idempotency_key": payment.idempotency_key,
    }


@router.post("/pay")
def pay_order(
    order_id: int,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
):
    # 1) Order must exist
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 2) If already PAID, allow idempotent returns if key matches; otherwise create/return latest payment
    if idempotency_key:
        existing = (
            db.query(Payment)
            .filter(Payment.order_id == order_id, Payment.idempotency_key == idempotency_key)
            .first()
        )
        if existing:
            return _serialize_payment(existing)

    try:
        # Create payment (mock provider = always SUCCEEDED)
        payment = Payment(
            order_id=order_id,
            status=PaymentStatus.SUCCEEDED.value,
            amount_cents=order.total_cents,
            currency=order.currency,
            idempotency_key=idempotency_key,
        )
        db.add(payment)
        db.flush()  # assigns payment.id

        # Update order status -> PAID
        order.status = OrderStatus.PAID.value

        db.commit()
        db.refresh(payment)
        return _serialize_payment(payment)

    except IntegrityError:
        db.rollback()
        # unique constraint hit -> return existing payment for same (order_id, idempotency_key)
        if idempotency_key:
            existing = (
                db.query(Payment)
                .filter(Payment.order_id == order_id, Payment.idempotency_key == idempotency_key)
                .first()
            )
            if existing:
                return _serialize_payment(existing)
        raise
    except Exception:
        db.rollback()
        raise


@router.get("/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return _serialize_payment(payment)
