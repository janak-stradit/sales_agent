"""rename_banks_to_accounts_remove_1nf_tables

Revision ID: f4cd119c6dbd
Revises: e1d428444c88
Create Date: 2026-08-17 20:12:06.907105

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f4cd119c6dbd'
down_revision: Union[str, Sequence[str], None] = 'e1d428444c88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    1. Drop all FK constraints referencing banks or bank_lobs.
    2. Rename tables: banks → accounts, bank_lobs → account_lobs, etc.
    3. Rename bank_id columns → account_id across child tables.
    4. Recreate FK constraints referencing accounts/account_lobs.
    5. Add parent_lob_name column to account_lobs if not exists.
    6. Drop 1NF side tables: bank_technologies, bank_taxonomies.
    """

    # ── Step 1: Drop ALL FK constraints that reference banks or bank_lobs ──
    op.drop_constraint('contacts_bank_id_fkey', 'contacts', type_='foreignkey')
    op.drop_constraint('contacts_lob_id_fkey', 'contacts', type_='foreignkey')
    op.drop_constraint('funding_events_bank_id_fkey', 'funding_events', type_='foreignkey')
    op.drop_constraint('bank_lobs_bank_id_fkey', 'bank_lobs', type_='foreignkey')
    op.drop_constraint('bank_lobs_parent_lob_id_fkey', 'bank_lobs', type_='foreignkey')
    op.drop_constraint('bank_products_services_bank_id_fkey', 'bank_products_services', type_='foreignkey')
    op.drop_constraint('bank_products_services_lob_id_fkey', 'bank_products_services', type_='foreignkey')
    op.drop_constraint('bank_market_segments_bank_id_fkey', 'bank_market_segments', type_='foreignkey')
    op.drop_constraint('bank_market_segments_lob_id_fkey', 'bank_market_segments', type_='foreignkey')
    op.drop_constraint('bank_technology_initiatives_bank_id_fkey', 'bank_technology_initiatives', type_='foreignkey')
    op.drop_constraint('bank_technology_initiatives_lob_id_fkey', 'bank_technology_initiatives', type_='foreignkey')
    op.drop_constraint('data_source_evidence_bank_id_fkey', 'data_source_evidence', type_='foreignkey')
    op.drop_constraint('data_source_evidence_lob_id_fkey', 'data_source_evidence', type_='foreignkey')
    op.drop_constraint('tool_execution_logs_bank_id_fkey', 'tool_execution_logs', type_='foreignkey')
    op.drop_constraint('pipeline_runs_bank_id_fkey', 'pipeline_runs', type_='foreignkey')
    op.drop_constraint('sales_trigger_signals_bank_id_fkey', 'sales_trigger_signals', type_='foreignkey')
    op.drop_constraint('sales_trigger_signals_lob_id_fkey', 'sales_trigger_signals', type_='foreignkey')
    op.drop_constraint('social_intelligence_bank_id_fkey', 'social_intelligence', type_='foreignkey')

    # ── Step 2: Rename tables ─────────────────────────────────
    op.rename_table('banks', 'accounts')
    op.rename_table('bank_lobs', 'account_lobs')
    op.rename_table('bank_products_services', 'account_products_services')
    op.rename_table('bank_market_segments', 'account_market_segments')
    op.rename_table('bank_technology_initiatives', 'account_technology_initiatives')

    # ── Step 3: Rename bank_id → account_id in ALL child tables ──
    op.alter_column('contacts', 'bank_id', new_column_name='account_id')
    op.alter_column('funding_events', 'bank_id', new_column_name='account_id')
    op.alter_column('account_lobs', 'bank_id', new_column_name='account_id')
    op.alter_column('account_products_services', 'bank_id', new_column_name='account_id')
    op.alter_column('account_market_segments', 'bank_id', new_column_name='account_id')
    op.alter_column('account_technology_initiatives', 'bank_id', new_column_name='account_id')
    op.alter_column('data_source_evidence', 'bank_id', new_column_name='account_id')
    op.alter_column('tool_execution_logs', 'bank_id', new_column_name='account_id')
    op.alter_column('pipeline_runs', 'bank_id', new_column_name='account_id')
    op.alter_column('sales_trigger_signals', 'bank_id', new_column_name='account_id')
    op.alter_column('social_intelligence', 'bank_id', new_column_name='account_id')

    # ── Step 4: Recreate FK constraints referencing new table names ──
    op.create_foreign_key('contacts_account_id_fkey', 'contacts', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('contacts_lob_id_fkey', 'contacts', 'account_lobs', ['lob_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('funding_events_account_id_fkey', 'funding_events', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('account_lobs_account_id_fkey', 'account_lobs', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('account_lobs_parent_lob_id_fkey', 'account_lobs', 'account_lobs', ['parent_lob_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('account_products_services_account_id_fkey', 'account_products_services', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('account_products_services_lob_id_fkey', 'account_products_services', 'account_lobs', ['lob_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('account_market_segments_account_id_fkey', 'account_market_segments', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('account_market_segments_lob_id_fkey', 'account_market_segments', 'account_lobs', ['lob_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('account_technology_initiatives_account_id_fkey', 'account_technology_initiatives', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('account_technology_initiatives_lob_id_fkey', 'account_technology_initiatives', 'account_lobs', ['lob_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('data_source_evidence_account_id_fkey', 'data_source_evidence', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('data_source_evidence_lob_id_fkey', 'data_source_evidence', 'account_lobs', ['lob_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('tool_execution_logs_account_id_fkey', 'tool_execution_logs', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('pipeline_runs_account_id_fkey', 'pipeline_runs', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('sales_trigger_signals_account_id_fkey', 'sales_trigger_signals', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('sales_trigger_signals_lob_id_fkey', 'sales_trigger_signals', 'account_lobs', ['lob_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('social_intelligence_account_id_fkey', 'social_intelligence', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')

    # ── Step 5: Add parent_lob_name column to account_lobs if missing ──
    op.execute("ALTER TABLE account_lobs ADD COLUMN IF NOT EXISTS parent_lob_name VARCHAR(255)")

    # ── Step 6: Drop 1NF side tables ──────────────────────────
    op.drop_table('bank_technologies')
    op.drop_table('bank_taxonomies')


def downgrade() -> None:
    """Reverse the migration."""
    # Recreate 1NF tables
    op.create_table('bank_technologies',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('bank_id', sa.UUID(), nullable=False),
        sa.Column('technology_name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('vendor', sa.String(255), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('bank_taxonomies',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('bank_id', sa.UUID(), nullable=False),
        sa.Column('code_type', sa.String(50), nullable=False),
        sa.Column('code_value', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # Rename tables back
    op.rename_table('account_technology_initiatives', 'bank_technology_initiatives')
    op.rename_table('account_market_segments', 'bank_market_segments')
    op.rename_table('account_products_services', 'bank_products_services')
    op.rename_table('account_lobs', 'bank_lobs')
    op.rename_table('accounts', 'banks')

    # Rename columns back
    for table in ['contacts', 'funding_events', 'bank_lobs', 'bank_products_services',
                  'bank_market_segments', 'bank_technology_initiatives',
                  'data_source_evidence', 'tool_execution_logs', 'pipeline_runs',
                  'sales_trigger_signals', 'social_intelligence']:
        op.alter_column(table, 'account_id', new_column_name='bank_id')
