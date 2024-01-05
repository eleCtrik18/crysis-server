"""Update: Mandate Notification to support mandate txn id

Revision ID: 0042bf032529
Revises: fbbfd5ab93c0
Create Date: 2023-08-25 19:52:19.818729

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0042bf032529'
down_revision = 'fbbfd5ab93c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mandate_notifications', sa.Column('mandate_transaction_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'mandate_notifications', 'mandate_transactions', ['mandate_transaction_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'mandate_notifications', type_='foreignkey')
    op.drop_column('mandate_notifications', 'mandate_transaction_id')
    # ### end Alembic commands ###
