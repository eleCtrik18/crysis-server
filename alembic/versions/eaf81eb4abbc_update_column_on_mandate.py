"""Update: Column on Mandate

Revision ID: eaf81eb4abbc
Revises: 120ba428c0a1
Create Date: 2023-08-18 14:29:49.656622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eaf81eb4abbc"
down_revision = "120ba428c0a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "mandates", sa.Column("txn_no", sa.String(), nullable=False, default="test")
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("mandates", "txn_no")
    # ### end Alembic commands ###
