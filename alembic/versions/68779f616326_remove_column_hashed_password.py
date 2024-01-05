"""Remove column hashed password

Revision ID: 68779f616326
Revises: f896f822af6e
Create Date: 2023-07-31 17:42:05.395971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68779f616326'
down_revision = 'f896f822af6e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'hashed_password')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
