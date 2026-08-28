from fastapi import FastAPI
from database import init_db, get_connection
from routes import router
import redis

app = FastAPI(
    title="Task API",
    version="1.0"
)

redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

redis_client.ping()
print("Redis: PONG")

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