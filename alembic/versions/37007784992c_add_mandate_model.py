"""Add: mandate model

Revision ID: 37007784992c
Revises: fb47170c889d
Create Date: 2023-08-16 15:15:42.595904

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '37007784992c'
down_revision = 'fb47170c889d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mandates',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('recurrence', sa.String(), nullable=True),
    sa.Column('recur_day', sa.String(), nullable=True),
    sa.Column('recur_date', sa.Integer(), nullable=True),
    sa.Column('attached_vpa_id', sa.String(), nullable=True),
    sa.Column('mandate_ref', sa.String(), nullable=False),
    sa.Column('start_date', sa.String(), nullable=False),
    sa.Column('end_date', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('pattern', sa.String(), nullable=False),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mandates_id'), 'mandates', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_mandates_id'), table_name='mandates')
    op.drop_table('mandates')
    # ### end Alembic commands ###
