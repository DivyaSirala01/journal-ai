from typing import Any, List, Optional, Literal
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, inspect, text

from database import Base, engine


class NoteDB(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    updated_on = Column(DateTime, nullable=True)
    priority = Column(String, nullable=False)
    summary = Column[str](String, nullable=False)

Base.metadata.create_all(bind=engine) #Creating table


def _ensure_notes_columns() -> None:
    """
    Add newly introduced columns for existing SQLite databases.
    This prevents runtime 500 errors when table schema lags behind model changes.
    """
    inspector = inspect(engine)
    if "notes" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("notes")}
    alter_statements = []

    for column in NoteDB.__table__.columns:
        if column.name in existing_columns:
            continue
        if column.primary_key:
            # SQLite cannot reliably add a new PK column with ALTER TABLE.
            continue

        compiled_type = column.type.compile(dialect=engine.dialect)
        nullable_sql = "" if column.nullable else " NOT NULL"
        default_sql = _build_default_sql(column.default.arg if column.default else None)

        alter_statements.append(
            f"ALTER TABLE notes ADD COLUMN {column.name} {compiled_type}{nullable_sql}{default_sql}"
        )

    if not alter_statements:
        return

    with engine.begin() as connection:
        for statement in alter_statements:
            connection.execute(text(statement))


def _build_default_sql(default_value: Any) -> str:
    if default_value is None:
        return ""
    if isinstance(default_value, str):
        escaped = default_value.replace("'", "''")
        return f" DEFAULT '{escaped}'"
    if isinstance(default_value, bool):
        return f" DEFAULT {1 if default_value else 0}"
    return f" DEFAULT {default_value}"


_ensure_notes_columns()


class NoteBaseRequest(BaseModel):
    content: str = Field(..., min_length=1, description="The text content of the note")


class NoteCreate(NoteBaseRequest):
    pass


class NoteUpdate(NoteBaseRequest):
    pass


class Note(BaseModel):
    id: int
    category: str
    content: str
    created_on: datetime
    updated_on: Optional[datetime] = None
    priority: str
    summary: str

    class Config:
        from_attributes = True #FastAPI converts SQLAlchemy objects into Pydantic responses


class NotesResponse(BaseModel):
    total_notes: int
    notes: List[Note]


class MessageResponse(BaseModel):
    message: str


class DeleteAllNotesResponse(MessageResponse):
    message : str
    deleted_count: int


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query text")


class QueryResponse(MessageResponse):
    total_created: int
    notes: List[Note]


class CreateNoteResponse(MessageResponse):
    note: Note


class UpdateNoteResponse(MessageResponse):
    note: Note


