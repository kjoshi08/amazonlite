"""add currency to payments

Revision ID: aaa2490e1b7a
Revises: c4afb1b6384a
Create Date: 2026-02-13
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aaa2490e1b7a"
down_revision: str | None = "c4afb1b6384a"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "payments",
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="USD"),
    )
    op.alter_column("payments", "currency", server_default=None)


def downgrade() -> None:
    op.drop_column("payments", "currency")
