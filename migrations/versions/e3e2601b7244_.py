"""empty message

Revision ID: e3e2601b7244
Revises: 
Create Date: 2021-10-22 22:30:32.459745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3e2601b7244'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cemeteries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('city', sa.Text(), nullable=True),
    sa.Column('state', sa.Text(), nullable=True),
    sa.Column('zip', sa.Text(), nullable=True),
    sa.Column('phone', sa.Text(), nullable=True),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('userid', sa.Integer(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('date_created', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('graves',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('relationship', sa.Text(), nullable=True),
    sa.Column('birthdate', sa.Text(), nullable=True),
    sa.Column('birthplace', sa.Text(), nullable=True),
    sa.Column('deathdate', sa.Text(), nullable=True),
    sa.Column('deathplace', sa.Text(), nullable=True),
    sa.Column('plot', sa.Text(), nullable=True),
    sa.Column('fag_id', sa.Text(), nullable=True),
    sa.Column('fag_url', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('obituary', sa.Text(), nullable=True),
    sa.Column('pictureURL', sa.Text(), nullable=True),
    sa.Column('userid', sa.Integer(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('date_created', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['avatar'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    op.drop_table('graves')
    op.drop_table('cemeteries')
    # ### end Alembic commands ###