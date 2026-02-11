from tests.conftest import ensure_product_id


def test_checkout_idempotency_per_user(client, user_id):
    product_id = ensure_product_id(client)

    # Add item to cart (flat JSON expected by your /cart/items endpoint)
    r = client.post(
        f"/cart/items?user_id={user_id}",
        json={"product_id": product_id, "qty": 2},
    )
    r.raise_for_status()

    # Use a UNIQUE idempotency key per test run to avoid collisions with old DB rows
    idem = f"order_key_{user_id}"

    # Checkout once
    r1 = client.post(
        f"/orders/checkout?user_id={user_id}",
        headers={"Idempotency-Key": idem},
    )
    r1.raise_for_status()
    order1 = r1.json()

    assert "id" in order1
    assert order1["user_id"] == user_id
    assert order1["status"] in ("CREATED", "PAID", "CANCELLED")
    assert isinstance(order1.get("items", []), list)
    assert len(order1["items"]) >= 1

    # Checkout again with same idempotency key -> must return same order
    r2 = client.post(
        f"/orders/checkout?user_id={user_id}",
        headers={"Idempotency-Key": idem},
    )
    r2.raise_for_status()
    order2 = r2.json()

    assert order1["id"] == order2["id"]
    assert order2["user_id"] == user_id
