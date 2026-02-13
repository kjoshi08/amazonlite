from fastapi import FastAPI

from src.modules.auth.router import router as auth_router
from src.modules.cart.router import router as cart_router
from src.modules.catalog.router import router as catalog_router
from src.modules.orders.router import router as orders_router
from src.modules.payments.router import router as payments_router

app = FastAPI(title="AmazonLite API", version="0.1.0")


@app.get("/health")
def health():
    return {"ok": True}


# routers MUST come after app is created
app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(payments_router)
