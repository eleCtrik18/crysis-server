"""Add: Dob column

Revision ID: 192c56b60f20
Revises: 68779f616326
Create Date: 2023-07-31 18:22:28.387034

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '192c56b60f20'
down_revision = '68779f616326'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('dob', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'dob')
    # ### end Alembic commands ###