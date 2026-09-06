import os

from fastapi import FastAPI
from dotenv import load_dotenv
from supabase import create_client, Client

from database import init_db, get_connection
from routes import router

import redis


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# CREATE FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="Task API",
    version="1.0"
)


# --------------------------------------------------
# CREATE SUPABASE CLIENT
# --------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Supabase client initialized" ,  flush=True)


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