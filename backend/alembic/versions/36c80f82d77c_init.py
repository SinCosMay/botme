"""init

Revision ID: 36c80f82d77c
Revises:
Create Date: 2026-04-01 03:28:21.384519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "36c80f82d77c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "problems",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("cf_contest_id", sa.Integer(), nullable=True),
        sa.Column("cf_index", sa.String(length=16), nullable=True),
        sa.Column("lc_problem_id", sa.String(length=64), nullable=True),
        sa.Column("lc_slug", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("companies", sa.JSON(), nullable=True),
        sa.Column("source_last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "cf_contest_id", "cf_index", name="uq_problem_cf"),
        sa.UniqueConstraint("platform", "lc_slug", name="uq_problem_lc"),
    )
    op.create_index(op.f("ix_problems_platform"), "problems", ["platform"], unique=False)
    op.create_index(op.f("ix_problems_rating"), "problems", ["rating"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("discord_id", sa.String(length=64), nullable=False),
        sa.Column("cf_handle", sa.String(length=64), nullable=False),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rating", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_solved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cf_handle"),
        sa.UniqueConstraint("discord_id"),
    )
    op.create_index(op.f("ix_users_cf_handle"), "users", ["cf_handle"], unique=True)
    op.create_index(op.f("ix_users_discord_id"), "users", ["discord_id"], unique=True)

    op.create_table(
        "assignments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("problem_id", sa.String(length=36), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "problem_id", "status", name="uq_user_problem_assignment_status"),
    )
    op.create_index(op.f("ix_assignments_problem_id"), "assignments", ["problem_id"], unique=False)
    op.create_index(op.f("ix_assignments_status"), "assignments", ["status"], unique=False)
    op.create_index(op.f("ix_assignments_user_id"), "assignments", ["user_id"], unique=False)

    op.create_table(
        "submissions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("problem_id", sa.String(length=36), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("cf_submission_id", sa.String(length=64), nullable=True),
        sa.Column("proof_url", sa.String(length=500), nullable=True),
        sa.Column("verdict", sa.String(length=32), nullable=False),
        sa.Column("solved_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("xp_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bonus_xp_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cf_submission_id"),
        sa.UniqueConstraint("user_id", "problem_id", name="uq_user_problem_submission"),
    )
    op.create_index(op.f("ix_submissions_platform"), "submissions", ["platform"], unique=False)
    op.create_index(op.f("ix_submissions_problem_id"), "submissions", ["problem_id"], unique=False)
    op.create_index(op.f("ix_submissions_user_id"), "submissions", ["user_id"], unique=False)

    op.create_table(
        "user_platform_stats",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("solved_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_solved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "platform"),
    )

    op.create_table(
        "rating_history",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("old_rating", sa.Integer(), nullable=False),
        sa.Column("new_rating", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rating_history_user_id"), "rating_history", ["user_id"], unique=False)

    op.create_table(
        "xp_history",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_xp_history_user_id"), "xp_history", ["user_id"], unique=False)

    op.create_table(
        "followup_questions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("problem_id", sa.String(length=36), nullable=False),
        sa.Column("question_type", sa.String(length=32), nullable=False),
        sa.Column("prompt", sa.String(length=1000), nullable=False),
        sa.Column("expected_answer", sa.JSON(), nullable=False),
        sa.Column("bonus_xp", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_followup_questions_problem_id"), "followup_questions", ["problem_id"], unique=False)

    op.create_table(
        "followup_attempts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("submission_id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=36), nullable=False),
        sa.Column("user_answer", sa.String(length=2000), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("awarded_xp", sa.Integer(), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["followup_questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_followup_attempts_question_id"), "followup_attempts", ["question_id"], unique=False)
    op.create_index(op.f("ix_followup_attempts_submission_id"), "followup_attempts", ["submission_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_followup_attempts_submission_id"), table_name="followup_attempts")
    op.drop_index(op.f("ix_followup_attempts_question_id"), table_name="followup_attempts")
    op.drop_table("followup_attempts")

    op.drop_index(op.f("ix_followup_questions_problem_id"), table_name="followup_questions")
    op.drop_table("followup_questions")

    op.drop_index(op.f("ix_xp_history_user_id"), table_name="xp_history")
    op.drop_table("xp_history")

    op.drop_index(op.f("ix_rating_history_user_id"), table_name="rating_history")
    op.drop_table("rating_history")

    op.drop_table("user_platform_stats")

    op.drop_index(op.f("ix_submissions_user_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_problem_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_platform"), table_name="submissions")
    op.drop_table("submissions")

    op.drop_index(op.f("ix_assignments_user_id"), table_name="assignments")
    op.drop_index(op.f("ix_assignments_status"), table_name="assignments")
    op.drop_index(op.f("ix_assignments_problem_id"), table_name="assignments")
    op.drop_table("assignments")

    op.drop_index(op.f("ix_users_discord_id"), table_name="users")
    op.drop_index(op.f("ix_users_cf_handle"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_problems_rating"), table_name="problems")
    op.drop_index(op.f("ix_problems_platform"), table_name="problems")
    op.drop_table("problems")
