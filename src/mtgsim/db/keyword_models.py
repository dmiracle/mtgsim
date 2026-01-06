"""SQLModel models for MTG keywords."""

from sqlmodel import Field, SQLModel


class Keyword(SQLModel, table=True):
    """MTG keyword entry."""

    id: int | None = Field(default=None, primary_key=True)
    keyword: str = Field(index=True)
    type: str = Field(index=True)  # 'abilityWords', 'keywordAbilities', 'keywordActions'
