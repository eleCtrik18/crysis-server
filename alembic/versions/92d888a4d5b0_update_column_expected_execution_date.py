"""Update: column expected_execution_date

Revision ID: 92d888a4d5b0
Revises: e5409541f943
Create Date: 2023-08-24 01:13:51.426252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92d888a4d5b0'
down_revision = 'e5409541f943'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.alter_column('mandate_notifications', 'expected_execution_date',
    #            existing_type=sa.VARCHAR(),
    #            type_=sa.DateTime(timezone=True),
    #            nullable=True)

    op.execute("ALTER TABLE mandate_notifications ALTER COLUMN expected_execution_date TYPE timestamp with time zone USING expected_execution_date::timestamp with time zone")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('mandate_notifications', 'expected_execution_date',
               existing_type=sa.DateTime(timezone=True),
               type_=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
