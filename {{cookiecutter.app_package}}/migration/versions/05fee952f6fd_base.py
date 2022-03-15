"""base migration.

Revision ID: 05fee952f6fd
Revises:
Create Date: 2022-01-01 12:13:52.152200

"""
from alembic import op
from sqlalchemy import Column, DateTime, Integer, String, func

# revision identifiers, used by Alembic.
revision = "051ee932f6d1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "foo",
        Column("id", Integer, primary_key=True),
        Column("type", String(20), nullable=False),
        Column("created_at", DateTime, nullable=False, server_default=func.now()),
        Column(
            "updated_at",
            DateTime,
            nullable=False,
            server_default=func.now(),
            server_onupdate=func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("foo")
