"""change grade tables to composite primary key

Revision ID: 768567f4771b
Revises: b35d50a46821
Create Date: 2024-02-07 23:35:56.443882

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '768567f4771b'
down_revision = 'b35d50a46821'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('grade_assessment', schema=None) as batch_op:
        batch_op.drop_column('id')

    with op.batch_alter_table('grade_remark', schema=None) as batch_op:
        batch_op.drop_column('id')
    
    op.create_primary_key('pk_gradeassessment', 'grade_assessment', ['sid', 'assessment_id'])
    op.create_primary_key('pk_graderemark', 'grade_remark', ['sid', 'remark_id'])


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('grade_remark', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False))

    with op.batch_alter_table('grade_assessment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False))

    # ### end Alembic commands ###