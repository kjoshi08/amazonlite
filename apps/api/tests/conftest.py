import os
import time
import uuid

import httpx
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def wait_for_api(timeout_s: int = 30) -> None:
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        try:
            r = httpx.get(f"{BASE_URL}/health", timeout=2.0)
            if r.status_code == 200:
                return
            last = f"status={r.status_code} body={r.text}"
        except Exception as e:
            last = repr(e)
        time.sleep(1)
    raise RuntimeError(f"API not ready after {timeout_s}s. Last error: {last}")


@pytest.fixture(scope="session", autouse=True)
def _api_ready():
    wait_for_api(timeout_s=60)


@pytest.fixture()
def user_id() -> str:
    return f"test_{uuid.uuid4().hex[:8]}"


@pytest.fixture()
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


def ensure_product_id(client: httpx.Client) -> int:
    """
    Return a valid product id.
    Supports unknown /products response shapes and falls back to probing /products/{id}.
    """

    def extract_first_id(payload):
        # If it's already a list of products
        if isinstance(payload, list) and payload:
            if isinstance(payload[0], dict) and "id" in payload[0]:
                return int(payload[0]["id"])
            return None

        # If it's a dict, check common keys
        if isinstance(payload, dict):
            for key in ("products", "items", "data", "results"):
                v = payload.get(key)
                if isinstance(v, list) and v:
                    if isinstance(v[0], dict) and "id" in v[0]:
                        return int(v[0]["id"])

            # Last resort: find any list-of-dicts with "id"
            for v in payload.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0]:
                    return int(v[0]["id"])

        return None

    # 1) Try list endpoint
    r = client.get("/products")
    r.raise_for_status()
    pid = extract_first_id(r.json())
    if pid is not None:
        return pid

    # 2) Try seed + list again
    client.post("/products/seed")
    r2 = client.get("/products")
    r2.raise_for_status()
    pid2 = extract_first_id(r2.json())
    if pid2 is not None:
        return pid2

    # 3) Fallback: probe /products/{id} for a valid product
    for i in range(1, 51):
        ri = client.get(f"/products/{i}")
        if ri.status_code == 200:
            body = ri.json()
            if isinstance(body, dict) and "id" in body:
                return int(body["id"])
            pid3 = extract_first_id(body)
            if pid3 is not None:
                return pid3

    raise RuntimeError("No products found via /products or /products/{id} after seeding.")
