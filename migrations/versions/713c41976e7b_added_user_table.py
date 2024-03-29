"""added user table

Revision ID: 713c41976e7b
Revises: d29ed3605243
Create Date: 2024-01-23 01:14:19.990871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '713c41976e7b'
down_revision = 'd29ed3605243'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('hashed_password', sa.String(length=200), nullable=False),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
