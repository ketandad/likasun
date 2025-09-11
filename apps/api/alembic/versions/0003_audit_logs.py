"""audit logs table"""

from alembic import op
import sqlalchemy as sa

revision = "0003_audit_logs"
down_revision = "4da2ee42382d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actor", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("resource", sa.String(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
    )
    op.create_index("ix_audit_logs_ts_desc", "audit_logs", ["ts"], unique=False)
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_ts_desc", table_name="audit_logs")
    op.drop_table("audit_logs")
