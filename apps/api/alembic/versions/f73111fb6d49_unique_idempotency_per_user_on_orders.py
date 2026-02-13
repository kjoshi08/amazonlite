"""unique idempotency per user on orders

Revision ID: f73111fb6d49
Revises: af50a5cd81b1
"""

from alembic import op

revision = "f73111fb6d49"
down_revision = "af50a5cd81b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ✅ Make safe on fresh DB + existing DB
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
            WHERE t.relname = 'orders'
              AND c.conname = 'orders_idempotency_key_key'
          ) THEN
            ALTER TABLE orders DROP CONSTRAINT orders_idempotency_key_key;
          END IF;

          -- Create new composite unique constraint, only if it doesn't exist
          IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            WHERE t.relname = 'orders'
              AND c.conname = 'uq_orders_user_id_idempotency_key'
          ) THEN
            ALTER TABLE orders
              ADD CONSTRAINT uq_orders_user_id_idempotency_key
              UNIQUE (user_id, idempotency_key);
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
            WHERE t.relname = 'orders'
              AND c.conname = 'uq_orders_user_id_idempotency_key'
          ) THEN
            ALTER TABLE orders DROP CONSTRAINT uq_orders_user_id_idempotency_key;
          END IF;
        END $$;
        """
    )
