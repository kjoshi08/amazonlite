"""unique idempotency per order on payments

Revision ID: 958819f7a6c6
Revises: db6a3dee28ac
"""

from alembic import op

revision = "958819f7a6c6"
down_revision = "db6a3dee28ac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ✅ Safe: create constraint only if it doesn't already exist
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            WHERE t.relname = 'payments'
              AND c.conname = 'uq_payments_order_id_idempotency_key'
          ) THEN
            ALTER TABLE payments
              ADD CONSTRAINT uq_payments_order_id_idempotency_key
              UNIQUE (order_id, idempotency_key);
          END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # ✅ Safe downgrade: drop only if exists
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            WHERE t.relname = 'payments'
              AND c.conname = 'uq_payments_order_id_idempotency_key'
          ) THEN
            ALTER TABLE payments DROP CONSTRAINT uq_payments_order_id_idempotency_key;
          END IF;
        END $$;
        """
    )
