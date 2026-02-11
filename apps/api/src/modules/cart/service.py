import json
from typing import Dict

from src.db.redis_client import get_redis

CART_TTL_SECONDS = 60 * 60 * 24  # 24 hours


def _cart_key(user_id: str) -> str:
    return f"cart:{user_id}"


def get_cart(user_id: str) -> Dict[str, int]:
    r = get_redis()
    raw = r.get(_cart_key(user_id))
    if not raw:
        return {}
    return json.loads(raw)


def save_cart(user_id: str, cart: Dict[str, int]) -> None:
    r = get_redis()
    r.setex(_cart_key(user_id), CART_TTL_SECONDS, json.dumps(cart))


def add_item(user_id: str, product_id: int, qty: int) -> Dict[str, int]:
    cart = get_cart(user_id)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + qty
    save_cart(user_id, cart)
    return cart


def set_qty(user_id: str, product_id: int, qty: int) -> Dict[str, int]:
    cart = get_cart(user_id)
    key = str(product_id)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    save_cart(user_id, cart)
    return cart


def clear_cart(user_id: str) -> None:
    r = get_redis()
    r.delete(_cart_key(user_id))
