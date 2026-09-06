from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from supabase_client import supabase


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

    # --------------------------------------------------
    # CHECK AUTHORIZATION HEADER
    # --------------------------------------------------

    if not authorization:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Access token required"
            }
        )

    # --------------------------------------------------
    # CHECK BEARER FORMAT
    # --------------------------------------------------

    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={
                "error": "Access token required"
            }
        )

    # --------------------------------------------------
    # EXTRACT TOKEN
    # --------------------------------------------------

    token = authorization.split(" ", 1)[1]

    if not token:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Access token required"
            }
        )

    # --------------------------------------------------
    # VERIFY TOKEN WITH SUPABASE
    # --------------------------------------------------

    try:

        response = supabase.auth.get_user(token)

        user = response.user

        if user is None:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Invalid or expired token"
                }
            )

    except Exception:

        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid or expired token"
            }
        )

    # --------------------------------------------------
    # RETURN SAFE USER INFORMATION
    # --------------------------------------------------

    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }