"""SQLModel definitions for card embeddings."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class MJCardEmbedding(SQLModel, table=True):
    """Metadata for vector embeddings of card text fields.

    The actual vectors are stored in a sqlite-vec virtual table.
    This table tracks metadata for cache invalidation and model versioning.
    """

    __tablename__ = "mj_card_embedding"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(index=True)

    # What was embedded
    field_source: str = Field(index=True)  # "oracle", "flavor", "combined", "name_only"
    source_hash: str  # Hash of source text for change detection

    # Model info
    model_name: str = Field(index=True)  # e.g., "BAAI/bge-small-en-v1.5"
    dimensions: int = 384

    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.utcnow)
