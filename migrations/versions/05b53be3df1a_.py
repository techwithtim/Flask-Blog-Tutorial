"""empty message

Revision ID: 05b53be3df1a
Revises: e3e2601b7244
Create Date: 2021-10-22 22:57:31.507543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05b53be3df1a'
down_revision = 'e3e2601b7244'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('graves', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cemeteriesfk', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'cemeteries', ['cemeteriesfk'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('graves', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('cemeteriesfk')

    # ### end Alembic commands ###
