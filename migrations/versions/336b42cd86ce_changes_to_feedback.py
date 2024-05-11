"""changes to feedback

Revision ID: 336b42cd86ce
Revises: e3c412b20f3f
Create Date: 2024-05-11 17:22:40.519096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '336b42cd86ce'
down_revision = 'e3c412b20f3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('feedbacks', schema=None) as batch_op:
        batch_op.drop_column('username')

    # ### end Alembic commands ###