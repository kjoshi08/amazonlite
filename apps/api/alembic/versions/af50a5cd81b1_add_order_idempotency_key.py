"""add order idempotency key

Revision ID: af50a5cd81b1
Revises: 99f5a7f50fa4
"""


from alembic import op

revision = "af50a5cd81b1"
down_revision = "99f5a7f50fa4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ✅ Safe on fresh DB and existing DB:
    # Add column only if it does NOT already exist.
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'orders'
              AND column_name = 'idempotency_key'
          ) THEN
            ALTER TABLE orders ADD COLUMN idempotency_key VARCHAR(128);
          END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # ✅ Safe downgrade: drop column only if it exists
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'orders'
              AND column_name = 'idempotency_key'
          ) THEN
            ALTER TABLE orders DROP COLUMN idempotency_key;
          END IF;
        END $$;
        """
    )
