from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse


# --------------------------------------------------
# PROTECTED ROUTER
# --------------------------------------------------

router = APIRouter(
    prefix="/protected",
    tags=["Protected"]
)


# --------------------------------------------------
# PROFILE
# --------------------------------------------------

@router.get("/profile")
def profile(
    authorization: str | None = Header(
        default=None,
        alias="Authorization"
    )
):

    # Check whether Authorization header exists
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Access token required"
            }
        )

    # Check whether it starts with "Bearer "
    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={
                "error": "Access token required"
            }
        )

    # Extract token
    token = authorization.split(" ", 1)[1]

    # Check whether token actually exists
    if not token:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Access token required"
            }
        )

    # Stage 2:
    # We only check that a Bearer token exists.
    # We do NOT verify the token yet.
    # Token verification comes in Stage 3.

    return {
        "message": "Token received"
    }