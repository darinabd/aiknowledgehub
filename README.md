# AI Knowledge Hub — Backend

FastAPI + SQLAlchemy + SQLite backend for the AI Knowledge Hub document
management platform.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# one-time migration if you're reusing an existing ai_knowledge.db
python migrate.py

uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs
at `http://127.0.0.1:8000/docs`.

Copy `.env.example` to `.env` and set a real `SECRET_KEY` before deploying
anywhere beyond your own machine.

## API overview

### Auth
| Method | Path            | Description                          |
|--------|-----------------|---------------------------------------|
| POST   | `/auth/register`| Create a new account                  |
| POST   | `/auth/login`   | Form login (`username`=email), returns JWT |

### Users
| Method | Path              | Description              |
|--------|-------------------|---------------------------|
| GET    | `/users/me`        | Current user profile     |
| PUT    | `/users/me`        | Update username/email    |
| PUT    | `/users/me/password`| Change password          |

### Documents (all require `Authorization: Bearer <token>`)
| Method | Path                        | Description                                 |
|--------|-----------------------------|----------------------------------------------|
| POST   | `/documents/upload`          | Upload a PDF                                |
| GET    | `/documents/`                | List documents — `?search=&file_type=&sort_by=created_at\|filename\|size&order=asc\|desc` |
| GET    | `/documents/stats`           | Totals for the dashboard cards              |
| GET    | `/documents/{id}`            | Document details                            |
| GET    | `/documents/{id}/download`   | Download the original file                  |
| DELETE | `/documents/{id}`            | Delete a document                           |

## Notes / next steps
- Only PDFs are accepted on upload (`application/pdf`), capped at 50MB.
- Files are stored on disk under `uploads/` with a UUID filename; the
  original filename is kept in the database for display and download.
- `page_count` is extracted automatically via `pypdf` on upload.
- The architecture keeps document text extraction (`pdf_service.py`)
  separate from storage (`file_service.py`), so adding an AI chat / RAG
  layer later just means adding an embeddings step here and a new
  `/documents/{id}/ask` endpoint — no rework needed.
