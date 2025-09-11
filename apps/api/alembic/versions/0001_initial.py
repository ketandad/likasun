"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2024-05-20

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("cloud", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("config", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "evidence", sa.JSON(), nullable=False, server_default=sa.text("'{}'")
        ),
        sa.Column("ingest_source", sa.String(), nullable=False),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_assets_asset_id", "assets", ["asset_id"], unique=False)

    op.create_table(
        "controls",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("control_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column(
            "applies_to", sa.JSON(), nullable=False, server_default=sa.text("'{}'")
        ),
        sa.Column("logic", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "frameworks", sa.JSON(), nullable=False, server_default=sa.text("'{}'")
        ),
        sa.Column("fix", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )
    op.create_index("ix_controls_control_id", "controls", ["control_id"], unique=True)

    op.create_table(
        "results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("control_id", sa.String(), nullable=False),
        sa.Column("control_title", sa.String(), nullable=False),
        sa.Column("asset_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column(
            "frameworks", sa.JSON(), nullable=False, server_default=sa.text("'{}'")
        ),
        sa.Column(
            "evidence", sa.JSON(), nullable=False, server_default=sa.text("'{}'")
        ),
        sa.Column("fix", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "evaluated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("doc_id", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("parties", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("renewal_date", sa.Date(), nullable=True),
        sa.Column(
            "obligations", sa.JSON(), nullable=False, server_default=sa.text("'{}'")
        ),
        sa.Column("clauses", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("risk_score", sa.Integer(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )
    op.create_index("ix_documents_doc_id", "documents", ["doc_id"], unique=True)

    op.create_table(
        "actors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("mfa", sa.Boolean(), nullable=False),
        sa.Column("roles", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )
    op.create_index("ix_actors_actor_id", "actors", ["actor_id"], unique=True)

    op.create_table(
        "vendors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vendor_id", sa.String(), nullable=False),
        sa.Column("product", sa.String(), nullable=False),
        sa.Column("scopes", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "data_classes", sa.JSON(), nullable=False, server_default=sa.text("'{}'")
        ),
        sa.Column("dpia_status", sa.String(), nullable=False),
        sa.Column("risk", sa.String(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )
    op.create_index("ix_vendors_vendor_id", "vendors", ["vendor_id"], unique=True)

    op.create_table(
        "exceptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("control_id", sa.String(), nullable=False),
        sa.Column(
            "selector", sa.JSON(), nullable=False, server_default=sa.text("'{}'")
        ),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(), nullable=False),
    )

    op.create_table(
        "meta",
        sa.Column("key", sa.String(), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
    )

    user_role = sa.Enum("admin", "auditor", "viewer", name="userrole")
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", user_role, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
    op.drop_table("meta")
    op.drop_table("exceptions")
    op.drop_index("ix_vendors_vendor_id", table_name="vendors")
    op.drop_table("vendors")
    op.drop_index("ix_actors_actor_id", table_name="actors")
    op.drop_table("actors")
    op.drop_index("ix_documents_doc_id", table_name="documents")
    op.drop_table("documents")
    op.drop_table("results")
    op.drop_index("ix_controls_control_id", table_name="controls")
    op.drop_table("controls")
    op.drop_index("ix_assets_asset_id", table_name="assets")
    op.drop_table("assets")
