"""Add a new column category in the table cause

Revision ID: 1b9a20f9a38f
Revises: 1c1f548d6d52
Create Date: 2014-12-30 11:24:27.400651

"""

# revision identifiers, used by Alembic.
revision = '1b9a20f9a38f'
down_revision = '1c1f548d6d52'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cause', sa.Column('category', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cause', 'category')
    ### end Alembic commands ###
