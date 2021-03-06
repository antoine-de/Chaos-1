"""Add priority and effect to the severities

Revision ID: 405df13d41fe
Revises: 1894217a6b3f
Create Date: 2014-07-03 07:59:03.390155

"""

# revision identifiers, used by Alembic.
revision = '405df13d41fe'
down_revision = '1894217a6b3f'

from alembic import op
import sqlalchemy as sa

SeverityEffect = sa.Enum('blocking', name='severity_effect')

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    SeverityEffect.create(op.get_bind())
    op.add_column('severity', sa.Column('effect', SeverityEffect, nullable=True))
    op.add_column('severity', sa.Column('priority', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('severity', 'priority')
    op.drop_column('severity', 'effect')
    SeverityEffect.drop(op.get_bind())
    ### end Alembic commands ###
