from datetime import datetime
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from llm import extract_llm_fields, llm_query_optimization
from schema import Note, NoteCreate, NoteUpdate, NoteDB
from schema import NotesResponse, CreateNoteResponse, UpdateNoteResponse, MessageResponse, DeleteAllNotesResponse
from schema import QueryRequest, QueryResponse

app = FastAPI(title="LLM Integrated Notes App")

# Create Database Session Dependency
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FETCH - HOME
@app.get("/")
def read_root() -> dict:
    return {"message": "This is an LLM integrated Notes APP"}


#FETCH ALL NOTES
@app.get("/notes", response_model=NotesResponse)
def get_all_note(db: Session = Depends(get_db)) -> NotesResponse:
    notes = db.query(NoteDB).all()
    return NotesResponse(total_notes=len(notes), notes=notes)

#FETCH - SINGLE NOTE
@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, db: Session = Depends(get_db)) -> Note:
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note:
        return note
    raise HTTPException(status_code=404, detail="Note not found")


#CREATE
@app.post("/notes", response_model=CreateNoteResponse, status_code=201)
def new_note(new_note: NoteCreate, db: Session = Depends(get_db)) -> CreateNoteResponse:
    # LLM call
    category, priority, summary = extract_llm_fields(new_note.content)
    note = NoteDB(
        category=category,
        created_on=datetime.now(),
        updated_on=None,
        content=new_note.content,
        priority = priority,
        summary = summary,
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return CreateNoteResponse(message="New note added", note=note)

#UPDATE
@app.put("/notes/{note_id}", response_model=UpdateNoteResponse)
def update(note_id: int, new_note: NoteUpdate, db: Session = Depends(get_db)) -> UpdateNoteResponse:
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note doesn't exist")

    note.content = new_note.content
    note.updated_on = datetime.now()
    
    # LLM call
    category, priority, summary = extract_llm_fields(new_note.content)
    note.category = category
    note.priority = priority
    note.summary = summary
    
    db.commit()
    db.refresh(note)
    return UpdateNoteResponse(message="Note Data Updated", note=note)

#DELETE
@app.delete("/notes/{note_id}", response_model=MessageResponse)
def delete(note_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not present")

    db.delete(note)
    db.commit()
    return MessageResponse(message="Note deleted successfully")


# DELETE ALL NOTES
@app.delete("/notes", response_model=DeleteAllNotesResponse)
def delete_all_notes(db: Session = Depends(get_db)) -> DeleteAllNotesResponse:
    deleted_count = db.query(NoteDB).delete(synchronize_session=False)
    db.commit()
    return DeleteAllNotesResponse(
        message="All notes deleted successfully",
        deleted_count=deleted_count,
    )


## INTERNAL API : QUERY/endpoint
@app.post("/query", response_model=QueryResponse)
def query_notes(payload: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    optimized_queries = llm_query_optimization(payload.query)
    created_notes: list[NoteDB] = []

    for sub_query in optimized_queries:
        category, priority, summary = extract_llm_fields(sub_query)
        note = NoteDB(
            category=category,
            created_on=datetime.now(),
            updated_on=None,
            content=sub_query,
            priority=priority,
            summary=summary,
        )
        db.add(note)
        created_notes.append(note)

    db.commit()
    for note in created_notes:
        db.refresh(note)

    return QueryResponse(
        message="Multi-hop query optimized and stored successfully",
        total_created=len(created_notes),
        notes=created_notes,
    )