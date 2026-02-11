"""unique idempotency per order on payments

Revision ID: db6a3dee28ac
Revises: f73111fb6d49
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa  # noqa: F401

# revision identifiers, used by Alembic.
revision = "db6a3dee28ac"
down_revision = "f73111fb6d49"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old global unique constraint on payments.idempotency_key (if it exists)
    # Postgres default naming for UNIQUE(idempotency_key) is: payments_idempotency_key_key
    try:
        op.drop_constraint("payments_idempotency_key_key", "payments", type_="unique")
    except Exception:
        pass

    # Create composite unique constraint: (order_id, idempotency_key)
    op.create_unique_constraint(
        "uq_payments_order_id_idempotency_key",
        "payments",
        ["order_id", "idempotency_key"],
    )


def downgrade() -> None:
    # Drop composite constraint
    op.drop_constraint(
        "uq_payments_order_id_idempotency_key",
        "payments",
        type_="unique",
    )

    # Restore old global unique constraint
    op.create_unique_constraint(
        "payments_idempotency_key_key",
        "payments",
        ["idempotency_key"],
    )

