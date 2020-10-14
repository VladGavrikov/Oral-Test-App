"""final db

Revision ID: 7dfa3bd93f58
Revises: 
Create Date: 2020-10-02 23:42:13.912107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7dfa3bd93f58'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('unit',
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('description', sa.String(length=50), nullable=True),
    sa.Column('mark1Criteria', sa.String(length=50), nullable=True),
    sa.Column('mark2Criteria', sa.String(length=50), nullable=True),
    sa.Column('mark3Criteria', sa.String(length=50), nullable=True),
    sa.Column('mark4Criteria', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('test',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('due_time', sa.Time(), nullable=True),
    sa.Column('isFinalized', sa.Boolean(), nullable=True),
    sa.Column('unit_id', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['unit_id'], ['unit.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit_id', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('firstName', sa.String(length=64), nullable=True),
    sa.Column('LastName', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('isTeacher', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['unit_id'], ['unit.name'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('question',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('path', sa.String(length=140), nullable=True),
    sa.Column('test_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['test_id'], ['test.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_mark',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('test_id', sa.Integer(), nullable=True),
    sa.Column('unit_id', sa.String(length=20), nullable=True),
    sa.Column('mark', sa.Integer(), nullable=True),
    sa.Column('testWasStarted', sa.Boolean(), nullable=True),
    sa.Column('feedbackReleased', sa.Boolean(), nullable=True),
    sa.Column('hasBeenMarked', sa.Boolean(), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('due_time', sa.Time(), nullable=True),
    sa.Column('mark1', sa.Integer(), nullable=True),
    sa.Column('mark2', sa.Integer(), nullable=True),
    sa.Column('mark3', sa.Integer(), nullable=True),
    sa.Column('mark4', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['test_id'], ['test.id'], ),
    sa.ForeignKeyConstraint(['unit_id'], ['unit.name'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('answer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('feedback',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('path', sa.String(length=140), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('answer_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['answer_id'], ['answer.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('feedback')
    op.drop_table('answer')
    op.drop_table('test_mark')
    op.drop_table('question')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('test')
    op.drop_table('unit')
    # ### end Alembic commands ###
