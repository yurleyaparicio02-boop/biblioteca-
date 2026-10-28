"""0002_multa_pagada

Revision ID: 5578096e22f8
Revises: 78820a306705
Create Date: 2026-10-28 17:18:43.050316

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5578096e22f8'
down_revision: Union[str, Sequence[str], None] = '78820a306705'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "prestamos",
        sa.Column(
            "multa_pagada",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.execute("UPDATE prestamos SET multa_pagada = true WHERE multa = 0")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("prestamos", "multa_pagada")