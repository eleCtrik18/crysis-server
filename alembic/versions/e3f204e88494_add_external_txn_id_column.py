"""Add: external txn id column

Revision ID: e3f204e88494
Revises: 90b92ad6e669
Create Date: 2023-08-10 19:21:59.203960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f204e88494'
down_revision = '90b92ad6e669'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('external_txn_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transactions', 'external_txn_id')
    # ### end Alembic commands ###
