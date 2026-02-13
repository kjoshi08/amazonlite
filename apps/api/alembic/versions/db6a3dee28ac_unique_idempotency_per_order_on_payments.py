"""unique idempotency per order on payments

Revision ID: db6a3dee28ac
Revises: f73111fb6d49
"""

from alembic import op

revision = "db6a3dee28ac"
down_revision = "f73111fb6d49"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ✅ Safe on fresh DB + existing DB:
    # - Drop old single-column unique (if it exists)
    # - Create new composite unique (if it doesn't exist)
    op.execute(
        """
        DO $$
        BEGIN
          -- Drop old constraint (single-column), only if it exists
          IF EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            WHERE t.relname = 'payments'
              AND c.conname = 'payments_idempotency_key_key'
          ) THEN
            ALTER TABLE payments DROP CONSTRAINT payments_idempotency_key_key;
          END IF;

          -- Create new composite unique constraint, only if it doesn't exist
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
    # ✅ Safe downgrade: drop composite constraint only if it exists
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
