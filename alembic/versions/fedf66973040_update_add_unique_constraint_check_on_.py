"""Update: add unique constraint check on notification

Revision ID: fedf66973040
Revises: 96b44b2e66c6
Create Date: 2023-09-01 17:32:37.720566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fedf66973040'
down_revision = '96b44b2e66c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('mandate_notifications', 'seq_no',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.create_unique_constraint(None, 'mandate_notifications', ['mandate_id', 'seq_no'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'mandate_notifications', type_='unique')
    op.alter_column('mandate_notifications', 'seq_no',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
