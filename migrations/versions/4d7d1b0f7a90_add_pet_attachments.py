"""add pet attachments

Revision ID: 4d7d1b0f7a90
Revises: f5c3f0c1e2ab
Create Date: 2026-03-24 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4d7d1b0f7a90"
down_revision: Union[str, Sequence[str], None] = "f5c3f0c1e2ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pet_attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pet_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=True),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("is_image", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["pet_id"], ["pets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index(op.f("ix_pet_attachments_id"), "pet_attachments", ["id"], unique=False)
    op.create_index(op.f("ix_pet_attachments_pet_id"), "pet_attachments", ["pet_id"], unique=False)
    op.create_index(
        op.f("ix_pet_attachments_storage_key"),
        "pet_attachments",
        ["storage_key"],
        unique=True,
    )
    op.create_index(
        op.f("ix_pet_attachments_uploaded_by_id"),
        "pet_attachments",
        ["uploaded_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_pet_attachments_uploaded_by_id"), table_name="pet_attachments")
    op.drop_index(op.f("ix_pet_attachments_storage_key"), table_name="pet_attachments")
    op.drop_index(op.f("ix_pet_attachments_pet_id"), table_name="pet_attachments")
    op.drop_index(op.f("ix_pet_attachments_id"), table_name="pet_attachments")
    op.drop_table("pet_attachments")
