"""0006_imagen_libro

Revision ID: a1b2c3d4e6f7
Revises: c91042a1b005
Create Date: 2026-11-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e6f7'
down_revision: Union[str, Sequence[str], None] = 'c91042a1b005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Solo el enlace seguro de Cloudinary (secure_url), no el archivo.
    op.add_column(
        'libros',
        sa.Column('imagen_url', sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('libros', 'imagen_url')
