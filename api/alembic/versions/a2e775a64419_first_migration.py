"""First Migration

Revision ID: a2e775a64419
Revises: 
Create Date: 2024-06-10 17:57:40.193531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2e775a64419'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genres',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('libelle', sa.String(length=200), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_genres_id'), 'genres', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=300), nullable=True),
    sa.Column('username', sa.String(length=30), nullable=True),
    sa.Column('password', sa.String(length=300), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('first_connection', sa.DateTime(), nullable=True),
    sa.Column('last_connection', sa.DateTime(), nullable=True),
    sa.Column('registered_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('movies',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('movieGenreId', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('cover_image', sa.String(length=300), nullable=True),
    sa.Column('description', sa.String(length=300), nullable=True),
    sa.Column('release_year', sa.String(length=4), nullable=True),
    sa.Column('running_time', sa.String(length=12), nullable=True),
    sa.Column('age_limit', sa.String(length=2), nullable=True),
    sa.Column('movie_type', sa.String(length=5), nullable=True),
    sa.Column('zip_file', sa.String(length=200), nullable=True),
    sa.Column('rate', sa.Float(), nullable=True),
    sa.Column('views', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['movieGenreId'], ['genres.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_movies_id'), 'movies', ['id'], unique=False)
    op.create_table('comments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('parentId', sa.Integer(), nullable=True),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('movieId', sa.Integer(), nullable=True),
    sa.Column('content', sa.String(length=300), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['movieId'], ['movies.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parentId'], ['comments.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)
    op.create_table('download_links',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('movieId', sa.Integer(), nullable=True),
    sa.Column('link', sa.String(length=500), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['movieId'], ['movies.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_download_links_id'), 'download_links', ['id'], unique=False)
    op.create_table('favorites',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('movieId', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['movieId'], ['movies.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_favorites_id'), 'favorites', ['id'], unique=False)
    op.create_table('genre_movies',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('genreId', sa.Integer(), nullable=True),
    sa.Column('movieId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['genreId'], ['genres.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['movieId'], ['movies.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_genre_movies_id'), 'genre_movies', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_genre_movies_id'), table_name='genre_movies')
    op.drop_table('genre_movies')
    op.drop_index(op.f('ix_favorites_id'), table_name='favorites')
    op.drop_table('favorites')
    op.drop_index(op.f('ix_download_links_id'), table_name='download_links')
    op.drop_table('download_links')
    op.drop_index(op.f('ix_comments_id'), table_name='comments')
    op.drop_table('comments')
    op.drop_index(op.f('ix_movies_id'), table_name='movies')
    op.drop_table('movies')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_genres_id'), table_name='genres')
    op.drop_table('genres')
    # ### end Alembic commands ###
