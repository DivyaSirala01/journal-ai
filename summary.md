# TODO-AI Project Summary

## What This Project Is
`TODO-AI` is a FastAPI-based backend for an AI-assisted todo/notes application.
It stores notes in SQLite and uses an LLM to automatically:
- categorize each task
- assign priority
- generate a short summary
- split complex requests into smaller actionable todo items

## Tech Stack
- **API framework:** FastAPI
- **ORM/DB access:** SQLAlchemy
- **Validation/response models:** Pydantic
- **Database:** SQLite (`sqllite.db`)
- **LLM integration:** LangChain `ChatOpenAI` (`gpt-5-nano`)
- **Environment config:** `python-dotenv`

## High-Level Architecture
- `main.py`: API routes and request handling logic
- `database.py`: SQLAlchemy engine/session/base setup
- `schema.py`: SQLAlchemy `NoteDB` table + Pydantic request/response schemas
- `llm.py`: LLM prompt logic for categorization and query decomposition
- `.env`: environment variables (expected to include OpenAI credentials)

Request flow:
1. Client sends task text (`/notes` or `/query`)
2. App calls LLM helpers in `llm.py`
3. LLM output is parsed into `content`(in case of a multihop query), `category`, `priority`, `summary`
4. Data is persisted into SQLite via SQLAlchemy
5. Structured Pydantic responses are returned

## Core Features
- Create, read, update, and delete individual notes
- List all notes with a total count
- Delete all notes in one call
- AI enrichment on create/update:
  - category (Work/Personal/Health/Shopping/Urgent/Other)
  - priority (High/Medium/Low)
  - summary (short text)
- Multi-hop query endpoint (`/query`) that expands a single broad query into multiple atomic tasks and stores all of them

## API Endpoints
- `GET /` - health/welcome message
- `GET /notes` - fetch all notes
- `GET /notes/{note_id}` - fetch one note
- `POST /notes` - create note with AI-generated metadata
- `PUT /notes/{note_id}` - update note and regenerate AI metadata
- `DELETE /notes/{note_id}` - delete one note
- `DELETE /notes` - delete all notes
- `POST /query` - optimize a broad query into multiple tasks and store them

## Data Model (`notes` table)
Fields stored for each note:
- `id` (int, primary key)
- `category` (string)
- `content` (string)
- `created_on` (datetime)
- `updated_on` (datetime, nullable)
- `priority` (string)
- `summary` (string)

## Schema Evolution Behavior
`schema.py` includes a lightweight migration helper (`_ensure_notes_columns`) that checks existing SQLite columns and adds missing non-primary-key columns using `ALTER TABLE`.  
This helps older local DB files stay compatible when new fields are introduced.

## LLM Integration Details
- `llm_categorization(content)` asks the model for strict JSON with `category`, `priority`, and `summary`
- `extract_llm_fields(content)` parses and sanitizes model output (including code-fenced JSON and noisy wrappers)
- `llm_query_optimization(content)` asks the model to return JSON `{ "queries": [...] }` and falls back to the original input if parsing fails

## How To Run
1. Create and activate a virtual environment
2. Install dependencies (`fastapi`, `sqlalchemy`, `pydantic`, `python-dotenv`, `langchain-openai`, and an ASGI server like `uvicorn` or `fastapi[standard]`)
3. Set required environment variables in `.env` (including OpenAI API key)
4. Start the server, for example:
   - `fastapi dev main.py`  
   or  
   - `uvicorn main:app --reload`

## Current Strengths
- Clean separation of concerns (API vs DB vs schema vs LLM logic)
- Strong typed request/response contracts
- Defensive parsing with graceful LLM fallback behavior
- End-to-end CRUD plus AI-based task enrichment

## Notable Caveats
- Database filename is `sqllite.db` (double `ll`), which may be intentional but easy to mistype
- No authentication/authorization layer
- No dependency lockfile or explicit requirements file in current folder
- LLM results are best-effort and can vary by model behavior
