"""empty message

Revision ID: e97c1e028c84
Revises: 8b624a1b0fec
Create Date: 2019-02-03 17:48:37.353587

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e97c1e028c84'
down_revision = '8b624a1b0fec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('email', table_name='user')
    op.drop_column('user', 'email')
    op.drop_column('user', 'password')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password', mysql.VARCHAR(length=128), nullable=True))
    op.add_column('user', sa.Column('email', mysql.VARCHAR(length=128), nullable=True))
    op.create_index('email', 'user', ['email'], unique=True)
    # ### end Alembic commands ###