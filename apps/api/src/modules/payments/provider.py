import random


# Simulates an external payment gateway
# In real systems: Stripe/Adyen/etc (network calls, retries, timeouts)
def authorize(amount_cents: int) -> tuple[bool, str]:
    # 98% success rate
    ok = random.random() < 0.98
    return ok, ("authorized" if ok else "failed")


def capture(amount_cents: int) -> tuple[bool, str]:
    ok = random.random() < 0.99
    return ok, ("captured" if ok else "failed")
