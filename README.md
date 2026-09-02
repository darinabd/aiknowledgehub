# AI Knowledge Hub

> Turn PDF documents into a searchable, interactive knowledge library.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-RAG-412991?logo=openai&logoColor=white)](https://platform.openai.com/)

AI Knowledge Hub is a full-stack application for working with PDF documents. Users can create an account, build a private document library, generate summaries and study questions, and ask questions whose answers are grounded in the uploaded document.

## Features

- Secure registration and login with JWT authentication
- Personal document library for every user
- PDF upload, search, download, and deletion
- Automatic text extraction and chunking
- AI-generated document summaries
- AI-generated study questions with answers
- Document chat powered by retrieval-augmented generation (RAG)
- Responsive React dashboard and account settings
- Interactive API documentation provided by FastAPI

## How it works

1. A user uploads a PDF document (up to 50 MB).
2. The backend extracts the text and splits it into smaller chunks.
3. When the user asks a question, the application creates embeddings and selects the most relevant chunks using cosine similarity.
4. The selected context is sent to the OpenAI API to generate an answer grounded in the document.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, Vite 8, CSS |
| Backend | FastAPI, Python, Uvicorn |
| Database | SQLite, SQLAlchemy |
| Authentication | JWT, OAuth2 password flow, bcrypt |
| Document processing | pypdf |
| AI | OpenAI Responses API, `gpt-4.1-mini`, `text-embedding-3-small` |

## Project structure

```text
.
├── app/
│   ├── models/             # SQLAlchemy database models
│   ├── routers/            # Authentication, users, documents, and AI routes
│   ├── schemas/            # Pydantic request and response schemas
│   ├── services/           # PDF, file, text, embedding, and RAG logic
│   ├── database.py         # SQLite connection and session setup
│   ├── main.py             # FastAPI application entry point
│   └── security.py         # Password hashing and JWT authentication
├── frontend/
│   ├── public/             # Static assets
│   └── src/                # React application and API client
├── uploads/                # Local PDF storage (files are ignored by Git)
├── .env.example            # Environment variable template
├── migrate.py              # Migration helper for an existing local database
└── requirements.txt        # Python dependencies
```

## Getting started

### Prerequisites

- Python 3.9 or newer
- Node.js 20 or newer
- An OpenAI API key

### 1. Clone the repository

```bash
git clone https://github.com/darinabd/aiknowledgehub.git
cd aiknowledgehub
```

### 2. Configure the backend

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

```powershell
.venv\Scripts\activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Then add your values to `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_long_random_secret
```

Generate a secure `SECRET_KEY` with:

```bash
openssl rand -hex 32
```

> Never commit `.env` or publish real API keys. The file is already excluded by `.gitignore`.

Start the backend from the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- API: <http://127.0.0.1:8000>
- Swagger documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

### 3. Configure the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173> in your browser.

## Main API endpoints

All document, chat, and profile endpoints require a Bearer token.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Create an account |
| `POST` | `/auth/login` | Sign in and receive an access token |
| `GET` | `/users/me` | Get the current profile |
| `PUT` | `/users/me` | Update username or email |
| `PUT` | `/users/me/password` | Change the password |
| `POST` | `/documents/upload` | Upload and process a PDF |
| `GET` | `/documents/` | List and search documents |
| `GET` | `/documents/stats` | Get library statistics |
| `GET` | `/documents/{id}/download` | Download a document |
| `DELETE` | `/documents/{id}` | Delete a document |
| `POST` | `/chat/documents/{id}/ask` | Ask a question about a document |
| `POST` | `/chat/documents/{id}/summary` | Generate a summary |
| `POST` | `/chat/documents/{id}/questions` | Generate study questions |

## Local data

The development version stores data locally:

- SQLite data is stored in `ai_knowledge.db`.
- Uploaded PDFs are stored in `uploads/`.
- The access token is stored in the browser's local storage.

The database, uploaded documents, virtual environment, frontend dependencies, and secret environment file are excluded from Git.

If you are upgrading an older local database, run the migration helper once:

```bash
python migrate.py
```

## Current limitations

- Only PDF documents are supported.
- Files and the SQLite database are stored on the local machine.
- The frontend API address is currently configured for local development.
- Embeddings are generated when a question is asked rather than stored permanently.

## Roadmap

- Add persistent vector storage
- Support more document formats
- Add automated tests
- Make backend and frontend URLs configurable for deployment
- Add production deployment configuration

## Author

Created by [Darina](https://github.com/darinabd).
