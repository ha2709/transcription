"""create_relationship

Revision ID: e5455a885c2b
Revises: 142e6f372739
Create Date: 2024-09-08 15:48:55.016965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5455a885c2b'
down_revision: Union[str, None] = '142e6f372739'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tasks', 'task_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_index('ix_tasks_id', table_name='tasks')
    op.drop_column('tasks', 'id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.create_index('ix_tasks_id', 'tasks', ['id'], unique=False)
    op.alter_column('tasks', 'task_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###