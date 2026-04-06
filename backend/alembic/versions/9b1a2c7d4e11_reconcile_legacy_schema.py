"""Reconcile legacy schema drift.

Revision ID: 9b1a2c7d4e11
Revises: 36c80f82d77c
Create Date: 2026-04-02
"""

from typing import Any, Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b1a2c7d4e11"
down_revision: Union[str, Sequence[str], None] = "36c80f82d77c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(inspector: Any, table_name: str) -> bool:
	return table_name in inspector.get_table_names()


def _column_exists(inspector: Any, table_name: str, column_name: str) -> bool:
	if not _table_exists(inspector, table_name):
		return False
	return column_name in {col["name"] for col in inspector.get_columns(table_name)}


def _index_exists(inspector: Any, table_name: str, index_name: str) -> bool:
	if not _table_exists(inspector, table_name):
		return False
	return index_name in {idx["name"] for idx in inspector.get_indexes(table_name)}


def upgrade() -> None:
	bind = op.get_bind()
	inspector = sa.inspect(bind)

	if _table_exists(inspector, "users"):
		with op.batch_alter_table("users") as batch_op:
			if not _column_exists(inspector, "users", "level"):
				batch_op.add_column(sa.Column("level", sa.Integer(), nullable=False, server_default="1"))
			if not _column_exists(inspector, "users", "current_streak"):
				batch_op.add_column(sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"))
			if not _column_exists(inspector, "users", "longest_streak"):
				batch_op.add_column(sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"))
			if not _column_exists(inspector, "users", "last_solved_at"):
				batch_op.add_column(sa.Column("last_solved_at", sa.DateTime(timezone=True), nullable=True))
			if not _column_exists(inspector, "users", "created_at"):
				batch_op.add_column(sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
			if not _column_exists(inspector, "users", "updated_at"):
				batch_op.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

	if _table_exists(inspector, "problems"):
		with op.batch_alter_table("problems") as batch_op:
			if not _column_exists(inspector, "problems", "platform"):
				batch_op.add_column(sa.Column("platform", sa.String(length=20), nullable=False, server_default="codeforces"))
			if not _column_exists(inspector, "problems", "cf_contest_id"):
				batch_op.add_column(sa.Column("cf_contest_id", sa.Integer(), nullable=True))
			if not _column_exists(inspector, "problems", "cf_index"):
				batch_op.add_column(sa.Column("cf_index", sa.String(length=16), nullable=True))
			if not _column_exists(inspector, "problems", "lc_problem_id"):
				batch_op.add_column(sa.Column("lc_problem_id", sa.String(length=64), nullable=True))
			if not _column_exists(inspector, "problems", "lc_slug"):
				batch_op.add_column(sa.Column("lc_slug", sa.String(length=255), nullable=True))
			if not _column_exists(inspector, "problems", "tags"):
				batch_op.add_column(sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")))
			if not _column_exists(inspector, "problems", "companies"):
				batch_op.add_column(sa.Column("companies", sa.JSON(), nullable=True))
			if not _column_exists(inspector, "problems", "source_last_seen_at"):
				batch_op.add_column(sa.Column("source_last_seen_at", sa.DateTime(timezone=True), nullable=True))
			if not _column_exists(inspector, "problems", "created_at"):
				batch_op.add_column(sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
			if not _column_exists(inspector, "problems", "updated_at"):
				batch_op.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))

		if not _index_exists(inspector, "problems", "ix_problems_platform"):
			op.create_index("ix_problems_platform", "problems", ["platform"], unique=False)
		if not _index_exists(inspector, "problems", "ix_problems_rating"):
			op.create_index("ix_problems_rating", "problems", ["rating"], unique=False)

	inspector = sa.inspect(bind)

	if not _table_exists(inspector, "assignments"):
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

	if not _table_exists(inspector, "submissions"):
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

	if not _table_exists(inspector, "user_platform_stats"):
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

	if not _table_exists(inspector, "rating_history"):
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

	if not _table_exists(inspector, "xp_history"):
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

	if not _table_exists(inspector, "followup_questions"):
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

	if not _table_exists(inspector, "followup_attempts"):
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


def downgrade() -> None:
	# Irreversible safety migration for legacy DB reconciliation.
	pass
