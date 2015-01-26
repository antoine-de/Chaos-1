"""Create associate_disruption_pt_object table

Revision ID: 1c1f548d6d52
Revises: 54d1cae0dd8a
Create Date: 2014-12-18 11:11:46.664746

"""

# revision identifiers, used by Alembic.
revision = '1c1f548d6d52'
down_revision = '54d1cae0dd8a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('associate_disruption_pt_object',
    sa.Column('disruption_id', postgresql.UUID(), nullable=False),
    sa.Column('pt_object_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['disruption_id'], ['disruption.id'], ),
    sa.ForeignKeyConstraint(['pt_object_id'], ['pt_object.id'], ),
    sa.PrimaryKeyConstraint('disruption_id', 'pt_object_id', name='disruption_pt_object_pk')
    )
    connection = op.get_bind()
    result = connection.execute('select pt.id as pt_id, dd.id as dis_id, dd.created_at as created_at,'
                                ' dd.localization_id as loc_id '
                                'from disruption as dd left OUTER join pt_object as pt '
                                'on pt.uri = dd.localization_id')
    for row in result:
        # Pt_object exist in database
        if row['pt_id']:
            pt_object_id = row['pt_id']
        else:
            # Pt_object not exist in database
            op.execute("INSERT INTO pt_object (created_at, id, type, uri) VALUES ('{}', '{}', '{}', '{}')".
                       format(row['created_at'], row['dis_id'], 'stop_area', row['loc_id']))
            pt_object_id = row['dis_id']

        op.execute("INSERT INTO associate_disruption_pt_object (disruption_id, pt_object_id) VALUES ('{}', '{}')".
                   format(row['dis_id'], pt_object_id))

    op.drop_column(u'disruption', 'localization_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'disruption', sa.Column('localization_id', sa.TEXT(), nullable=True))
    connection = op.get_bind()
    result = connection.execute('select pt.uri as pt_uri, ass.disruption_id as dis_id from pt_object as pt, '
                                'associate_disruption_pt_object as ass where pt.id=ass.pt_object_id')
    for row in result:
        if row['dis_id']:
            op.execute("UPDATE disruption set localization_id = '{}' where id = '{}'".
                       format(row['pt_uri'], row['dis_id']))
    op.drop_table('associate_disruption_pt_object')
    ### end Alembic commands ###