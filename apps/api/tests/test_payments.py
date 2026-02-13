from tests.conftest import ensure_product_id


def test_payment_idempotency_per_order(client, user_id):
    product_id = ensure_product_id(client)

    # Create order
    client.post(
        f"/cart/items?user_id={user_id}", json={"product_id": product_id, "qty": 1}
    ).raise_for_status()

    idem_order = f"order_key_pay_{user_id}"
    order_resp = client.post(
        f"/orders/checkout?user_id={user_id}", headers={"Idempotency-Key": idem_order}
    )
    order_resp.raise_for_status()
    order = order_resp.json()
    order_id = int(order["id"])

    # Pay twice with same idempotency key -> same payment id
    idem_pay = f"pay_key_{user_id}"
    p1 = client.post(f"/payments/pay?order_id={order_id}", headers={"Idempotency-Key": idem_pay})
    p1.raise_for_status()
    pay1 = p1.json()
    assert pay1["order_id"] == order_id
    assert pay1["idempotency_key"] == idem_pay

    p2 = client.post(f"/payments/pay?order_id={order_id}", headers={"Idempotency-Key": idem_pay})
    p2.raise_for_status()
    pay2 = p2.json()

    assert pay1["payment_id"] == pay2["payment_id"]
    assert pay2["status"] in (
        "SUCCEEDED",
        "FAILED",
    )  # depending on fail_rate default, usually SUCCEEDED
