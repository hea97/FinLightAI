"""add notification subscriptions and delivery history

Revision ID: 7a91d13c4b20
Revises: 3f6b74e52f2a
Create Date: 2026-07-06
"""
import hashlib
import hmac
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from config.settings import get_settings

revision: str = "7a91d13c4b20"
down_revision: Union[str, Sequence[str], None] = "3f6b74e52f2a"
branch_labels = None
depends_on = None


def _token_hash(token: str) -> str:
    settings = get_settings()
    secret = settings.notification_token_secret or settings.jwt_secret_key
    if not secret and settings.is_development():
        secret = "finlight-local-notification-secret"
    if not secret:
        raise RuntimeError("NOTIFICATION_TOKEN_SECRET is required")
    return hmac.new(secret.encode(), token.encode(), hashlib.sha256).hexdigest()


def _unsubscribe_token_hash(user_id: str, email: str) -> str:
    signature = _token_hash(f"unsubscribe:{user_id}:{email}")
    return _token_hash(f"{user_id}.{signature}")


def _index_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    return {index["name"] for index in sa.inspect(bind).get_indexes(table_name)}


def _create_email_subscriptions() -> None:
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


def _upgrade_legacy_email_subscriptions() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("email_subscriptions")}
    with op.batch_alter_table("email_subscriptions") as batch_op:
        if "daily_summary" not in columns:
            batch_op.add_column(sa.Column("daily_summary", sa.Boolean(), nullable=False, server_default=sa.true()))
        if "immediate_red" not in columns:
            batch_op.add_column(sa.Column("immediate_red", sa.Boolean(), nullable=False, server_default=sa.true()))
        if "immediate_yellow" not in columns:
            batch_op.add_column(sa.Column("immediate_yellow", sa.Boolean(), nullable=False, server_default=sa.true()))
        if "confirm_token_hash" not in columns:
            batch_op.add_column(sa.Column("confirm_token_hash", sa.String(length=64), nullable=True))
        if "unsubscribe_token_hash" not in columns:
            batch_op.add_column(sa.Column("unsubscribe_token_hash", sa.String(length=64), nullable=True))
        if "token_expires_at" not in columns:
            batch_op.add_column(sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True))
        if "unsubscribed_at" not in columns:
            batch_op.add_column(sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True))
        if "created_at" not in columns:
            batch_op.add_column(sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))

    if "created_at" not in columns and "consented_at" in columns:
        bind.execute(sa.text("update email_subscriptions set created_at = consented_at where created_at is null"))

    rows = bind.execute(sa.text("select user_id, email from email_subscriptions")).fetchall()
    for user_id, email in rows:
        bind.execute(
            sa.text(
                "update email_subscriptions "
                "set unsubscribe_token_hash = :token_hash "
                "where user_id = :user_id"
            ),
            {"token_hash": _unsubscribe_token_hash(user_id, email), "user_id": user_id},
        )

    indexes = _index_names("email_subscriptions")
    if "ix_email_subscriptions_email" not in indexes:
        op.create_index("ix_email_subscriptions_email", "email_subscriptions", ["email"])
    if "ix_email_subscriptions_status" not in indexes:
        op.create_index("ix_email_subscriptions_status", "email_subscriptions", ["status"])
    if "uq_email_subscriptions_confirm_token_hash" not in indexes:
        op.create_index(
            "uq_email_subscriptions_confirm_token_hash",
            "email_subscriptions",
            ["confirm_token_hash"],
            unique=True,
        )
    if "uq_email_subscriptions_unsubscribe_token_hash" not in indexes:
        op.create_index(
            "uq_email_subscriptions_unsubscribe_token_hash",
            "email_subscriptions",
            ["unsubscribe_token_hash"],
            unique=True,
        )


def _create_notification_deliveries() -> None:
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


def upgrade() -> None:
    table_names = set(sa.inspect(op.get_bind()).get_table_names())
    if "email_subscriptions" in table_names:
        _upgrade_legacy_email_subscriptions()
    else:
        _create_email_subscriptions()
    if "notification_deliveries" not in table_names:
        _create_notification_deliveries()


def downgrade() -> None:
    op.drop_table("notification_deliveries")
    op.drop_table("email_subscriptions")
