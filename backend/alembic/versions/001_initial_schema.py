"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-03-03
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users (must be first — other tables reference it)
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("auth_provider", sa.String(20), nullable=False),
        sa.Column("auth_provider_id", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_active_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # User preferences
    op.create_table(
        "user_preferences",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("preferred_genres", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("disliked_genres", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("favorite_actors", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("favorite_directors", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("preferred_decades", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column(
            "streaming_services", postgresql.ARRAY(sa.String(50)), nullable=True
        ),
        sa.Column("content_rating_max", sa.String(10), nullable=True),
        sa.Column(
            "language_preferences", postgresql.ARRAY(sa.String(10)), nullable=True
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Movies (must exist before streaming_availability and watch_history)
    op.create_table(
        "movies",
        sa.Column("tmdb_id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("original_title", sa.String(500), nullable=True),
        sa.Column("overview", sa.Text(), nullable=True),
        sa.Column("release_date", sa.String(10), nullable=True),
        sa.Column("genres", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("genre_names", postgresql.ARRAY(sa.String(50)), nullable=True),
        sa.Column("vote_average", sa.Numeric(3, 1), nullable=True),
        sa.Column("vote_count", sa.Integer(), nullable=True),
        sa.Column("popularity", sa.Numeric(10, 3), nullable=True),
        sa.Column("runtime", sa.Integer(), nullable=True),
        sa.Column("poster_path", sa.String(255), nullable=True),
        sa.Column("backdrop_path", sa.String(255), nullable=True),
        sa.Column("original_language", sa.String(10), nullable=True),
        sa.Column("director_names", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("cast_names", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("content_rating", sa.String(10), nullable=True),
        sa.Column("keywords", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column(
            "last_synced_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Streaming availability
    op.create_table(
        "streaming_availability",
        sa.Column(
            "tmdb_id",
            sa.Integer(),
            sa.ForeignKey("movies.tmdb_id"),
            primary_key=True,
        ),
        sa.Column("service", sa.String(50), primary_key=True),
        sa.Column("region", sa.String(5), primary_key=True),
        sa.Column("available_since", sa.String(10), nullable=True),
        sa.Column("leaving_on", sa.String(10), nullable=True),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Watch history
    op.create_table(
        "watch_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "tmdb_id",
            sa.Integer(),
            sa.ForeignKey("movies.tmdb_id"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("rating", sa.SmallInteger(), nullable=True),
        sa.Column("source", sa.String(30), nullable=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Groups (must exist before recommendation_sessions and group_members)
    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("join_code", sa.String(8), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Group members
    op.create_table(
        "group_members",
        sa.Column(
            "group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("groups.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            primary_key=True,
        ),
        sa.Column("preferences", postgresql.JSONB(), nullable=True),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Recommendation sessions
    op.create_table(
        "recommendation_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("groups.id"),
            nullable=True,
        ),
        sa.Column("mode", sa.String(10), nullable=False, server_default="solo"),
        sa.Column("preferences", postgresql.JSONB(), nullable=False),
        sa.Column("recommendations", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("final_selection", sa.Integer(), nullable=True),
        sa.Column("turn_count", sa.SmallInteger(), server_default=sa.text("1")),
        sa.Column("satisfaction_rating", sa.SmallInteger(), nullable=True),
        sa.Column("total_tokens_used", sa.Integer(), nullable=True),
        sa.Column("model_used", sa.String(50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Analytics events
    op.create_table(
        "analytics_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("properties", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Indexes for common queries
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_watch_history_user_id", "watch_history", ["user_id"])
    op.create_index("ix_watch_history_tmdb_id", "watch_history", ["tmdb_id"])
    op.create_index("ix_groups_join_code", "groups", ["join_code"])
    op.create_index(
        "ix_recommendation_sessions_user_id",
        "recommendation_sessions",
        ["user_id"],
    )
    op.create_index(
        "ix_analytics_events_event_type", "analytics_events", ["event_type"]
    )
    op.create_index(
        "ix_analytics_events_created_at", "analytics_events", ["created_at"]
    )


def downgrade() -> None:
    op.drop_table("analytics_events")
    op.drop_table("recommendation_sessions")
    op.drop_table("group_members")
    op.drop_table("groups")
    op.drop_table("watch_history")
    op.drop_table("streaming_availability")
    op.drop_table("movies")
    op.drop_table("user_preferences")
    op.drop_table("users")
