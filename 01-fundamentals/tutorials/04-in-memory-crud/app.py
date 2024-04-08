"""Lesson 04: a complete small CRUD API with an isolated application state."""
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    body: str = Field(min_length=1, max_length=1000)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    body: str | None = Field(default=None, min_length=1, max_length=1000)


class Note(NoteCreate):
    id: int


def create_app() -> FastAPI:
    app = FastAPI(title="Notes | In-Memory CRUD")
    notes: dict[int, Note] = {}
    next_id = 1

    @app.post("/notes", response_model=Note, status_code=status.HTTP_201_CREATED)
    def create_note(payload: NoteCreate):
        nonlocal next_id
        note = Note(id=next_id, **payload.model_dump())
        notes[next_id] = note
        next_id += 1
        return note

    @app.get("/notes", response_model=list[Note])
    def list_notes():
        return list(notes.values())

    @app.get("/notes/{note_id}", response_model=Note)
    def get_note(note_id: int):
        if note_id not in notes:
            raise HTTPException(status_code=404, detail="Note not found")
        return notes[note_id]

    @app.patch("/notes/{note_id}", response_model=Note)
    def update_note(note_id: int, payload: NoteUpdate):
        if note_id not in notes:
            raise HTTPException(status_code=404, detail="Note not found")
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return notes[note_id]
        if any(value is None for value in updates.values()):
            raise HTTPException(status_code=422, detail="Use a non-null value to update a field")
        updated = notes[note_id].model_copy(update=updates)
        notes[note_id] = updated
        return updated

    @app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_note(note_id: int):
        if note_id not in notes:
            raise HTTPException(status_code=404, detail="Note not found")
        del notes[note_id]
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
