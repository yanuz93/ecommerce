"""empty message

Revision ID: a7021e9755a4
Revises: 89dc0da3122e
Create Date: 2019-08-25 09:44:57.012899

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a7021e9755a4'
down_revision = '89dc0da3122e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sellers', 'city',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    op.alter_column('sellers', 'postcode',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('sellers', 'province',
               existing_type=mysql.VARCHAR(length=30),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sellers', 'province',
               existing_type=mysql.VARCHAR(length=30),
               nullable=False)
    op.alter_column('sellers', 'postcode',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('sellers', 'city',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    # ### end Alembic commands ###
