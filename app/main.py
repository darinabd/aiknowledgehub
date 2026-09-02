from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, documents, users, chat
from app.database import engine, Base
from app import models  

app = FastAPI(
    title="AI Knowledge Hub",
    description="AI document management system",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
def home():
    return {"message": "AI Knowledge Hub is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
