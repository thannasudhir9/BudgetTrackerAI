"""recreate_user_budget_table

Revision ID: a2eee88b8c00
Revises: 8665357b6518
Create Date: 2024-12-03 00:28:56.387156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2eee88b8c00'
down_revision = '8665357b6518'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_budget', schema=None) as batch_op:
        batch_op.add_column(sa.Column('monthly_budget', sa.Numeric(precision=10, scale=2), nullable=True))
        batch_op.add_column(sa.Column('quarterly_budget', sa.Numeric(precision=10, scale=2), nullable=True))
        batch_op.add_column(sa.Column('yearly_budget', sa.Numeric(precision=10, scale=2), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.drop_column('budget_type')
        batch_op.drop_column('amount')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_budget', schema=None) as batch_op:
        batch_op.add_column(sa.Column('amount', sa.NUMERIC(precision=10, scale=2), nullable=False))
        batch_op.add_column(sa.Column('budget_type', sa.VARCHAR(length=10), nullable=False))
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('yearly_budget')
        batch_op.drop_column('quarterly_budget')
        batch_op.drop_column('monthly_budget')

    # ### end Alembic commands ###