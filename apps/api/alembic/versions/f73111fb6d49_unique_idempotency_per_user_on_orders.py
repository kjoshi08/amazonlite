"""unique idempotency per user on orders

Revision ID: f73111fb6d49
Revises: af50a5cd81b1
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa  # noqa: F401

# revision identifiers, used by Alembic.
revision = "f73111fb6d49"
down_revision = "af50a5cd81b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old global unique constraint on orders.idempotency_key (if it exists)
    try:
        op.drop_constraint("orders_idempotency_key_key", "orders", type_="unique")
    except Exception:
        pass

    # Create composite unique constraint (user_id, idempotency_key)
    op.create_unique_constraint(
        "uq_orders_user_id_idempotency_key",
        "orders",
        ["user_id", "idempotency_key"],
    )


def downgrade() -> None:
    # Drop composite constraint
    op.drop_constraint(
        "uq_orders_user_id_idempotency_key",
        "orders",
        type_="unique",
    )

    # Restore old global unique constraint
    op.create_unique_constraint(
        "orders_idempotency_key_key",
        "orders",
        ["idempotency_key"],
    )
