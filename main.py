from fastapi import FastAPI

from database import init_db
from routes import router


app = FastAPI(
    title="Task API",
    version="1.0"
)


init_db()


@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


app.include_router(router)