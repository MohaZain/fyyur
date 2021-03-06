"""empty message

Revision ID: 625e0570b4d0
Revises: 6c79d1e54328
Create Date: 2021-06-27 12:55:07.119455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '625e0570b4d0'
down_revision = '6c79d1e54328'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', sa.String(length=120), nullable=True))
    op.drop_column('venue', 'genre')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genre', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###
