"""Create: user kyc details table

Revision ID: 90b92ad6e669
Revises: 397c3c5bd636
Create Date: 2023-08-07 19:40:40.696069

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '90b92ad6e669'
down_revision = '397c3c5bd636'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_kyc_details',
    sa.Column('kyc_verified_on', sa.DateTime(timezone=True), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('kyc_verified_by', sa.String(), nullable=False),
    sa.Column('kyc_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('kyc_number', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('kyc_request_id', sa.String(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_kyc_details_id'), 'user_kyc_details', ['id'], unique=False)
    op.create_index(op.f('ix_user_kyc_details_kyc_number'), 'user_kyc_details', ['kyc_number'], unique=False)
    op.drop_index('ix_user_kyc_detailses_id', table_name='user_kyc_detailses')
    op.drop_index('ix_user_kyc_detailses_kyc_number', table_name='user_kyc_detailses')
    op.drop_table('user_kyc_detailses')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_kyc_detailses',
    sa.Column('kyc_verified_on', postgresql.TIMESTAMP(timezone=True), server_default=sa.text("timezone('utc'::text, CURRENT_TIMESTAMP)"), autoincrement=False, nullable=False),
    sa.Column('kyc_verified_by', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('kyc_data', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('kyc_number', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('kyc_request_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text("timezone('utc'::text, CURRENT_TIMESTAMP)"), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_kyc_detailses_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='user_kyc_detailses_pkey')
    )
    op.create_index('ix_user_kyc_detailses_kyc_number', 'user_kyc_detailses', ['kyc_number'], unique=False)
    op.create_index('ix_user_kyc_detailses_id', 'user_kyc_detailses', ['id'], unique=False)
    op.drop_index(op.f('ix_user_kyc_details_kyc_number'), table_name='user_kyc_details')
    op.drop_index(op.f('ix_user_kyc_details_id'), table_name='user_kyc_details')
    op.drop_table('user_kyc_details')
    # ### end Alembic commands ###
