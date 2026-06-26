"""add coowner permissions

Revision ID: 20260627_001
Revises: 
Create Date: 2026-06-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260627_001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем новые поля для разрешений совладельцев
    op.add_column('coowners', sa.Column('can_start_stop', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('coowners', sa.Column('can_view_logs', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('coowners', sa.Column('can_edit_files', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('coowners', sa.Column('can_manage_deps', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('coowners', sa.Column('can_view_settings', sa.Boolean(), nullable=False, server_default='1'))


def downgrade() -> None:
    # Удаляем добавленные поля
    op.drop_column('coowners', 'can_view_settings')
    op.drop_column('coowners', 'can_manage_deps')
    op.drop_column('coowners', 'can_edit_files')
    op.drop_column('coowners', 'can_view_logs')
    op.drop_column('coowners', 'can_start_stop')
