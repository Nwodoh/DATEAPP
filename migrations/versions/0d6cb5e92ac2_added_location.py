"""Added Location

Revision ID: 0d6cb5e92ac2
Revises: c97dcf107201
Create Date: 2024-07-07 14:18:10.184297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0d6cb5e92ac2'
down_revision = 'c97dcf107201'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('orientation', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('interest', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('location', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('location')
        batch_op.drop_column('interest')
        batch_op.drop_column('orientation')

    # ### end Alembic commands ###
