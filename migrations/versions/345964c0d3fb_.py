"""empty message

Revision ID: 345964c0d3fb
Revises: d3702b3be6a4
Create Date: 2021-10-18 00:13:55.721915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '345964c0d3fb'
down_revision = 'd3702b3be6a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('housing_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('movein', sa.Date(), nullable=True),
    sa.Column('moveout', sa.Date(), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('city', sa.Text(), nullable=True),
    sa.Column('state', sa.Text(), nullable=True),
    sa.Column('zip', sa.Text(), nullable=True),
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

    op.drop_table('housing_history')
    # ### end Alembic commands ###