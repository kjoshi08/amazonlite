from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.db.database import get_db
from src.db.models import Product
from src.modules.catalog.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)

router = APIRouter(prefix="/products", tags=["catalog"])


@router.get("", response_model=ProductListResponse)
def list_products(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None, min_length=1, max_length=200),
    active_only: bool = Query(True),
):
    query = db.query(Product)

    if active_only:
        query = query.filter(Product.is_active.is_(True))

    if q:
        like = f"%{q}%"
        query = query.filter((Product.name.ilike(like)) | (Product.sku.ilike(like)))

    total = query.with_entities(func.count(Product.id)).scalar() or 0
    items = (
        query.order_by(Product.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return ProductListResponse(items=items, limit=limit, offset=offset, total=total)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(status_code=409, detail="SKU already exists")

    product = Product(
        sku=payload.sku,
        name=payload.name,
        description=payload.description,
        price_cents=payload.price_cents,
        currency=payload.currency,
        stock_qty=payload.stock_qty,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(product, k, v)

    db.commit()
    db.refresh(product)
    return product


@router.post("/seed", response_model=dict)
def seed_products(db: Session = Depends(get_db)):
    samples = [
        {"sku": "AMZL-USB-C-01", "name": "USB-C Cable 1m", "description": "Fast charge USB-C cable", "price_cents": 999, "currency": "USD", "stock_qty": 120},
        {"sku": "AMZL-MOUSE-02", "name": "Wireless Mouse", "description": "Ergonomic wireless mouse", "price_cents": 2499, "currency": "USD", "stock_qty": 45},
        {"sku": "AMZL-KB-03", "name": "Mechanical Keyboard", "description": "Compact mechanical keyboard", "price_cents": 6999, "currency": "USD", "stock_qty": 18},
    ]

    created = 0
    for s in samples:
        exists = db.query(Product).filter(Product.sku == s["sku"]).first()
        if exists:
            continue
        db.add(Product(**s, is_active=True))
        created += 1

    db.commit()
    return {"seeded": created}
