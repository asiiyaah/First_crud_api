from fastapi import FastAPI
from database import init_db, get_connection
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
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        connection.close()

        return {
            "status": "ok",
            "db": "ok"
        }

    except Exception:
        return {
            "status": "ok",
            "db": "error"
        }

app.include_router(router)