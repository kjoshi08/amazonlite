"""add currency to payments

Revision ID: aaa2490e1b7a
Revises: c4afb1b6384a
Create Date: 2026-02-13
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aaa2490e1b7a"
down_revision: str | None = "c4afb1b6384a"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Add column only if it doesn't already exist
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='payments' AND column_name='currency'
          ) THEN
            ALTER TABLE payments
              ADD COLUMN currency VARCHAR(8) NOT NULL DEFAULT 'USD';
          END IF;
        END$$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='payments' AND column_name='currency'
          ) THEN
            ALTER TABLE payments DROP COLUMN currency;
          END IF;
        END$$;
        """
    )
