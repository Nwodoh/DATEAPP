"""Added likes

Revision ID: 0803c8b1f699
Revises: d1ac9091a220
Create Date: 2024-07-08 18:41:08.042294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0803c8b1f699'
down_revision = 'd1ac9091a220'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('likes',
    sa.Column('liker_id', sa.Integer(), nullable=True),
    sa.Column('liked_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['liked_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['liker_id'], ['users.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('likes')
    # ### end Alembic commands ###
