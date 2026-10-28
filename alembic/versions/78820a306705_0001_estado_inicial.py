"""0001_estado_inicial

Revision ID: 78820a306705
Revises: 
Create Date: 2026-10-28 15:39:44.432915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78820a306705'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('autores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('nacionalidad', sa.String(length=60), nullable=True),
    sa.Column('anio_nacimiento', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nombre')
    )
    op.create_table('categorias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=50), nullable=False),
    sa.Column('descripcion', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nombre')
    )
    op.create_table('socios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('telefono', sa.String(length=15), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=False),
    sa.Column('fecha_alta', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('libros',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('titulo', sa.String(length=150), nullable=False),
    sa.Column('isbn', sa.String(length=13), nullable=False),
    sa.Column('anio_publicacion', sa.Integer(), nullable=False),
    sa.Column('ejemplares', sa.Integer(), nullable=False),
    sa.Column('autor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['autor_id'], ['autores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_libros_autor_id'), 'libros', ['autor_id'], unique=False)
    op.create_index(op.f('ix_libros_isbn'), 'libros', ['isbn'], unique=True)
    op.create_index(op.f('ix_libros_titulo'), 'libros', ['titulo'], unique=False)
    op.create_table('libro_categoria',
    sa.Column('libro_id', sa.Integer(), nullable=False),
    sa.Column('categoria_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['categoria_id'], ['categorias.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['libro_id'], ['libros.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('libro_id', 'categoria_id')
    )
    op.create_table('prestamos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('libro_id', sa.Integer(), nullable=False),
    sa.Column('socio_id', sa.Integer(), nullable=False),
    sa.Column('fecha_prestamo', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
    sa.Column('fecha_limite', sa.Date(), nullable=False),
    sa.Column('fecha_devolucion', sa.Date(), nullable=True),
    sa.Column('multa', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['libro_id'], ['libros.id'], ),
    sa.ForeignKeyConstraint(['socio_id'], ['socios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prestamos_fecha_devolucion'), 'prestamos', ['fecha_devolucion'], unique=False)
    op.create_index(op.f('ix_prestamos_fecha_limite'), 'prestamos', ['fecha_limite'], unique=False)
    op.create_index(op.f('ix_prestamos_libro_id'), 'prestamos', ['libro_id'], unique=False)
    op.create_index(op.f('ix_prestamos_socio_id'), 'prestamos', ['socio_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_prestamos_socio_id'), table_name='prestamos')
    op.drop_index(op.f('ix_prestamos_libro_id'), table_name='prestamos')
    op.drop_index(op.f('ix_prestamos_fecha_limite'), table_name='prestamos')
    op.drop_index(op.f('ix_prestamos_fecha_devolucion'), table_name='prestamos')
    op.drop_table('prestamos')
    op.drop_table('libro_categoria')
    op.drop_index(op.f('ix_libros_titulo'), table_name='libros')
    op.drop_index(op.f('ix_libros_isbn'), table_name='libros')
    op.drop_index(op.f('ix_libros_autor_id'), table_name='libros')
    op.drop_table('libros')
    op.drop_table('socios')
    op.drop_table('categorias')
    op.drop_table('autores')