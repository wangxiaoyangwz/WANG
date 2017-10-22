"""empty message

Revision ID: b3ba53ef8e76
Revises: 5d589b4b2969
Create Date: 2017-10-22 15:47:44.790000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3ba53ef8e76'
down_revision = '5d589b4b2969'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('title', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'title')
    # ### end Alembic commands ###