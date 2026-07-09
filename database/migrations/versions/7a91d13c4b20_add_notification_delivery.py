"""add notification subscriptions and delivery history

Revision ID: 7a91d13c4b20
Revises: 3f6b74e52f2a
Create Date: 2026-07-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "7a91d13c4b20"
down_revision: Union[str, Sequence[str], None] = "3f6b74e52f2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_subscriptions",
        sa.Column("user_id", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("daily_summary", sa.Boolean(), nullable=False),
        sa.Column("immediate_red", sa.Boolean(), nullable=False),
        sa.Column("immediate_yellow", sa.Boolean(), nullable=False),
        sa.Column("confirm_token_hash", sa.String(length=64), nullable=True),
        sa.Column("unsubscribe_token_hash", sa.String(length=64), nullable=False),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("confirm_token_hash"),
        sa.UniqueConstraint("unsubscribe_token_hash"),
    )
    op.create_index("ix_email_subscriptions_email", "email_subscriptions", ["email"])
    op.create_index("ix_email_subscriptions_status", "email_subscriptions", ["status"])
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=80), nullable=True),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("notification_type", sa.String(length=40), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("dedupe_key", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("duplicate_count", sa.Integer(), nullable=False),
        sa.Column("last_duplicate_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("channel", "dedupe_key", name="uq_notification_delivery_channel_dedupe"),
    )
    for column in ("user_id", "channel", "notification_type", "status", "provider_message_id"):
        op.create_index(f"ix_notification_deliveries_{column}", "notification_deliveries", [column])


def downgrade() -> None:
    op.drop_table("notification_deliveries")
    op.drop_table("email_subscriptions")
