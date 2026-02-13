"""create payments

Revision ID: 99f5a7f50fa4
Revises: 8b9b03f4571f
"""

import sqlalchemy as sa

from alembic import op

revision = "99f5a7f50fa4"
down_revision = "8b9b03f4571f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ✅ Safe: only drop if constraint exists (fresh DB won't have it)
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'orders_idempotency_key_key'
          ) THEN
            ALTER TABLE orders DROP CONSTRAINT orders_idempotency_key_key;
          END IF;
        END $$;
        """
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PAID"),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "order_id",
            "idempotency_key",
            name="uq_payments_order_id_idempotency_key",
        ),
    )


def downgrade() -> None:
    op.drop_table("payments")
