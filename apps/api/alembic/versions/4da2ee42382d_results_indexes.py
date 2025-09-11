"""results indexes"""

from alembic import op
import sqlalchemy as sa

revision = "4da2ee42382d"
down_revision = "0002_evaluation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_results_run_id_status", "results", ["run_id", "status"], unique=False
    )
    op.create_index(
        "ix_results_frameworks", "results", ["frameworks"], postgresql_using="gin"
    )
    op.create_index(
        "ix_assets_tags", "assets", ["tags"], postgresql_using="gin"
    )


def downgrade() -> None:
    op.drop_index("ix_assets_tags", table_name="assets", postgresql_using="gin")
    op.drop_index("ix_results_frameworks", table_name="results", postgresql_using="gin")
    op.drop_index("ix_results_run_id_status", table_name="results")
