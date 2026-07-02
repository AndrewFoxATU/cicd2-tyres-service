"""Initial tyres schema.

Matches the schema that existing deployments already have (created by
postgres-init-tyres/tyres.sql or Base.metadata.create_all), so existing
databases are stamped at this revision instead of running it.

Revision ID: 0001
Revises:
Create Date: 2026-07-02

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tyres",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("brand", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("size", sa.String(), nullable=False),
        sa.Column("load_rate", sa.Integer(), nullable=False),
        sa.Column("speed_rate", sa.String(), nullable=False),
        sa.Column("season", sa.String(), nullable=False),
        sa.Column("supplier", sa.String(), nullable=False),
        sa.Column("fuel_efficiency", sa.String(), nullable=False),
        sa.Column("noise_level", sa.Integer(), nullable=False),
        sa.Column("weather_efficiency", sa.String(), nullable=False),
        sa.Column("ev_approved", sa.Boolean(), nullable=False),
        sa.Column("cost", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("retail_cost", sa.Numeric(10, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("tyres")
