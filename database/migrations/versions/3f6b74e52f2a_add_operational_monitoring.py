"""add operational monitoring

Revision ID: 3f6b74e52f2a
Revises: 09c4a8b3721a
Create Date: 2026-07-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "3f6b74e52f2a"
down_revision: Union[str, Sequence[str], None] = "09c4a8b3721a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("data_provider_status") as batch_op:
        batch_op.add_column(
            sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(sa.Column("first_failed_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "data_refresh_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("trigger", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("counts", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_refresh_runs_started_at", "data_refresh_runs", ["started_at"])
    op.create_index("ix_data_refresh_runs_status", "data_refresh_runs", ["status"])
    op.create_table(
        "provider_health_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=True),
        sa.Column("provider", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["data_refresh_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_provider_health_events_checked_at", "provider_health_events", ["checked_at"])
    op.create_index("ix_provider_health_events_provider", "provider_health_events", ["provider"])
    op.create_index("ix_provider_health_events_run_id", "provider_health_events", ["run_id"])
    op.create_index("ix_provider_health_events_status", "provider_health_events", ["status"])


def downgrade() -> None:
    op.drop_table("provider_health_events")
    op.drop_table("data_refresh_runs")
    with op.batch_alter_table("data_provider_status") as batch_op:
        batch_op.drop_column("last_success_at")
        batch_op.drop_column("first_failed_at")
        batch_op.drop_column("consecutive_failures")
