"""empty message

Revision ID: b0e0725e275f
Revises: 2de75316c34a
Create Date: 2023-06-06 19:20:51.259348

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0e0725e275f'
down_revision = '2de75316c34a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('favorite_people',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('people_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['people_id'], ['people.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('favorite', schema=None) as batch_op:
        batch_op.drop_constraint('favorite_people_id_fkey', type_='foreignkey')
        batch_op.drop_column('people_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('favorite', schema=None) as batch_op:
        batch_op.add_column(sa.Column('people_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('favorite_people_id_fkey', 'people', ['people_id'], ['id'])

    op.drop_table('favorite_people')
    # ### end Alembic commands ###
