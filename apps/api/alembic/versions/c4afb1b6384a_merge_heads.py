"""merge heads

Revision ID: c4afb1b6384a
Revises: 958819f7a6c6, db6a3dee28ac
Create Date: 2026-02-10 00:35:06.943532

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c4afb1b6384a'
down_revision = ('958819f7a6c6', 'db6a3dee28ac')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
