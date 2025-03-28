"""Removed default date.

Revision ID: b97a66497cd8
Revises: 30166ebb660e
Create Date: 2024-07-11 19:56:37.603523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b97a66497cd8'
down_revision = '30166ebb660e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('date_of_birth',
               existing_type=sa.DATE(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('date_of_birth',
               existing_type=sa.DATE(),
               nullable=False)

    # ### end Alembic commands ###
