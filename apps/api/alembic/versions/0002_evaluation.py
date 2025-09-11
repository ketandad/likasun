"""evaluation run and result updates

Revision ID: 0002_evaluation
Revises: 0001_initial
Create Date: 2024-05-20
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_evaluation"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evaluation_runs",
        sa.Column("run_id", sa.String(), primary_key=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("controls_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assets_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("results_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False, server_default="running"),
        sa.Column("error", sa.Text(), nullable=True),
    )

    op.add_column("results", sa.Column("run_id", sa.String(), nullable=True))
    op.add_column("results", sa.Column("meta", sa.JSON(), nullable=False, server_default=sa.text("'{}'")))
    op.create_index("ix_results_run_id", "results", ["run_id"], unique=False)
    op.create_index("ix_results_control_id", "results", ["control_id"], unique=False)
    op.create_index("ix_results_asset_id", "results", ["asset_id"], unique=False)
    op.create_index("ix_results_status", "results", ["status"], unique=False)
    op.create_index("ix_results_evaluated_at", "results", ["evaluated_at"], unique=False)
    op.create_index(
        "ix_results_control_asset_eval",
        "results",
        ["control_id", "asset_id", "evaluated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_results_control_asset_eval", table_name="results")
    op.drop_index("ix_results_evaluated_at", table_name="results")
    op.drop_index("ix_results_status", table_name="results")
    op.drop_index("ix_results_asset_id", table_name="results")
    op.drop_index("ix_results_control_id", table_name="results")
    op.drop_index("ix_results_run_id", table_name="results")
    op.drop_column("results", "meta")
    op.drop_column("results", "run_id")
    op.drop_table("evaluation_runs")
