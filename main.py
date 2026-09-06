from fastapi import FastAPI

from auth_routes import router as auth_router
from database import init_db, get_connection
from routes import router
import redis


# --------------------------------------------------
# CREATE FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="Task API",
    version="1.0"
)


# --------------------------------------------------
# REDIS
# --------------------------------------------------

redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

redis_client.ping()
print("Redis: PONG")


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

init_db()


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

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


# --------------------------------------------------
# TASK ROUTES
# --------------------------------------------------

app.include_router(router)


# --------------------------------------------------
# AUTH ROUTES
# --------------------------------------------------

app.include_router(auth_router)