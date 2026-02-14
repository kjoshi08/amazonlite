from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models import Order, OrderStatus, Payment, PaymentStatus
from src.db.session import get_db

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/pay")
def pay_order(
    order_id: int,
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(
        default=None, convert_underscores=False, alias="Idempotency-Key"
    ),
):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")

    # 1) Idempotent read first
    existing = (
        db.query(Payment)
        .filter(Payment.order_id == order_id, Payment.idempotency_key == idempotency_key)
        .first()
    )
    if existing:
        return {
            "payment_id": existing.id,
            "order_id": existing.order_id,
            "status": existing.status,
            "amount": str(existing.amount),
            "currency": existing.currency,
            "idempotency_key": existing.idempotency_key,
            "created_at": existing.created_at.isoformat() if existing.created_at else None,
        }

    # 2) Validate order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == OrderStatus.CANCELLED.value:
        raise HTTPException(status_code=409, detail="Order is cancelled")

    # If already paid, only allow retry when same idempotency key existed (handled above)
    if order.status == OrderStatus.PAID.value:
        raise HTTPException(status_code=409, detail="Order is already paid")

    # 3) Create payment (DB stores dollars in Numeric)
    amount = (Decimal(order.total_cents) / Decimal("100")).quantize(Decimal("0.01"))

    payment = Payment(
        order_id=order.id,
        status=PaymentStatus.SUCCEEDED.value,
        amount=amount,
        currency=order.currency,
        idempotency_key=idempotency_key,
    )

    try:
        db.add(payment)

        # mark order paid in same transaction
        order.status = OrderStatus.PAID.value

        db.commit()
        db.refresh(payment)

    except IntegrityError:
        # Another request likely inserted the same (order_id, idempotency_key).
        # Return the winner row to keep behavior idempotent.
        db.rollback()
        winner = (
            db.query(Payment)
            .filter(Payment.order_id == order_id, Payment.idempotency_key == idempotency_key)
            .first()
        )
        if not winner:
            raise
        return {
            "payment_id": winner.id,
            "order_id": winner.order_id,
            "status": winner.status,
            "amount": str(winner.amount),
            "currency": winner.currency,
            "idempotency_key": winner.idempotency_key,
            "created_at": winner.created_at.isoformat() if winner.created_at else None,
        }

    except Exception:
        db.rollback()
        raise

    return {
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "status": payment.status,
        "amount": str(payment.amount),
        "currency": payment.currency,
        "idempotency_key": payment.idempotency_key,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
    }


@router.get("/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "status": payment.status,
        "amount": str(payment.amount),
        "currency": payment.currency,
        "idempotency_key": payment.idempotency_key,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
    }
