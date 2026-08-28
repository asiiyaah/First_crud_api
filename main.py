from fastapi import FastAPI
from routes import router
from database import init_db

app = FastAPI(title="Task API")

init_db()

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router)