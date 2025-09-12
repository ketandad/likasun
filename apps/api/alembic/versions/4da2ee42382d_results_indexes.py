"""results indexes"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "4da2ee42382d"
down_revision = "0002_evaluation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Skip JSONB/index ops if using SQLite (for Codespaces/dev)
    from sqlalchemy import inspect
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        # SQLite: skip JSONB/index migration
        return
    # First convert JSON to JSONB
    op.alter_column('results', 'frameworks',
                   type_=postgresql.JSONB,
                   postgresql_using='frameworks::jsonb')
    # Create index with jsonb_path_ops
    op.create_index('ix_results_frameworks', 'results',
                   ['frameworks'], 
                   postgresql_using='gin',
                   postgresql_ops={'frameworks': 'jsonb_path_ops'})


def downgrade() -> None:
    op.drop_index('ix_results_frameworks')
    op.alter_column('results', 'frameworks',
                   type_=sa.JSON)
