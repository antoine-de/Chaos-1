"""
Add an attribut notification_date in the table impact

Revision ID: e33962db5d9
Revises: d3eacac50a6
Create Date: 2017-02-22 12:05:44.682015

"""

# revision identifiers, used by Alembic.
revision = 'e33962db5d9'
down_revision = 'd3eacac50a6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('impact', sa.Column('notification_date', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('impact', 'notification_date')
