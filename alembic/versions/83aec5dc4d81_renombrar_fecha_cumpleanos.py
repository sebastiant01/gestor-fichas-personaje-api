"""renombrar_fecha_cumpleanos

Revision ID: 83aec5dc4d81
Revises:
Create Date: 2026-06-06 16:32:09.729937

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "83aec5dc4d81"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name="fichas_personajes",
        column_name="fecha_cumpleaños",
        new_column_name="fecha_cumpleanos",
    )


def downgrade() -> None:
    op.alter_column(
        table_name="fichas_personajes",
        column_name="fecha_cumpleanos",
        new_column_name="fecha_cumpleaños",
    )
