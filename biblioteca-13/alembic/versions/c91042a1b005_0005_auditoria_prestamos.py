"""0005_auditoria_prestamos

Revision ID: c91042a1b005
Revises: e844032e4080
Create Date: 2026-10-28 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c91042a1b005'
down_revision: Union[str, Sequence[str], None] = 'e844032e4080'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'prestamos',
        sa.Column('registrado_por_id', sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f('ix_prestamos_registrado_por_id'),
        'prestamos',
        ['registrado_por_id'],
        unique=False,
    )
    op.create_foreign_key(
        'fk_prestamos_registrado_por_id_usuarios',
        'prestamos',
        'usuarios',
        ['registrado_por_id'],
        ['id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'fk_prestamos_registrado_por_id_usuarios',
        'prestamos',
        type_='foreignkey',
    )
    op.drop_index(
        op.f('ix_prestamos_registrado_por_id'),
        table_name='prestamos',
    )
    op.drop_column('prestamos', 'registrado_por_id')

