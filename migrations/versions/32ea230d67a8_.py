"""Create tag table

Revision ID: 32ea230d67a8
Revises: 570f97ecea5
Create Date: 2014-07-29 13:57:33.395737

"""

# revision identifiers, used by Alembic.
revision = '32ea230d67a8'
down_revision = '570f97ecea5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('is_visible', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tag')
    ### end Alembic commands ###
