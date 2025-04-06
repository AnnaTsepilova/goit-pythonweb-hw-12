"""Add user roles

Revision ID: 76f0c497879b
Revises: 511c0af5209b
Create Date: 2025-04-06 15:27:03.724842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '76f0c497879b'
down_revision: Union[str, None] = '511c0af5209b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define enum type
userrole_enum = postgresql.ENUM('USER', 'MODERATOR', 'ADMIN', name='userrole', create_type=False)

def upgrade() -> None:
    # Create enum type
    userrole_enum.create(op.get_bind())

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role', userrole_enum, nullable=False, server_default='USER'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    # ### end Alembic commands ###

    # Then drop enum type
    userrole_enum.drop(op.get_bind())
