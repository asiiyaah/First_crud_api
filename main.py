from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from auth_routes import router as auth_router
from protected_routes import router as protected_router
from public_routes import router as public_router

from database import init_db, get_connection
from routes import router

import redis

from llm.routes import router as llm_router


app = FastAPI(
    title="Task API",
    version="1.0",
)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(
    request: Request,
    exc: RequestValidationError,
):
    # The LLM assignment requires malformed AI input to be a 400 that names
    # the offending field. Keep the existing API behaviour unchanged elsewhere.
    if request.url.path == "/ai/triage":
        first_error = exc.errors()[0] if exc.errors() else {}
        location = first_error.get("loc", ())
        field = (
            location[-1]
            if location and location[-1] != "body"
            else "text"
        )

        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid request",
                "field": field,
                "message": first_error.get(
                    "msg",
                    "Invalid request.",
                ),
            },
        )

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# --------------------------------------------------
# REDIS
# --------------------------------------------------

redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True,
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
        "endpoints": ["/tasks"],
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
            "db": "ok",
        }

    except Exception:
        return {
            "status": "ok",
            "db": "error",
        }


# --------------------------------------------------
# TASK ROUTES
# --------------------------------------------------

app.include_router(router)


# --------------------------------------------------
# AUTH ROUTES
# --------------------------------------------------

app.include_router(auth_router)


# --------------------------------------------------
# PROTECTED ROUTES
# --------------------------------------------------

app.include_router(protected_router)


# --------------------------------------------------
# PUBLIC ROUTES
# --------------------------------------------------

app.include_router(public_router)

# --------------------------------------------------
# AI ROUTES
# --------------------------------------------------

app.include_router(llm_router)
