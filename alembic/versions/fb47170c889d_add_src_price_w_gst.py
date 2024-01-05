"""Add: src_price_w_gst

Revision ID: fb47170c889d
Revises: e3f204e88494
Create Date: 2023-08-11 02:44:13.228247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb47170c889d'
down_revision = 'e3f204e88494'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('gold24_prices', sa.Column('src_price_w_gst', sa.Float(), nullable=True))
    op.add_column('gold24_prices', sa.Column('src_price_wo_gst', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('gold24_prices', 'src_price_wo_gst')
    op.drop_column('gold24_prices', 'src_price_w_gst')
    # ### end Alembic commands ###
