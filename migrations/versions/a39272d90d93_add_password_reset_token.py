"""Add password_reset_token

Revision ID: a39272d90d93
Revises: 76f0c497879b
Create Date: 2025-04-06 17:25:11.393425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a39272d90d93'
down_revision: Union[str, None] = '76f0c497879b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_reset_token', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'password_reset_token')
    # ### end Alembic commands ###
