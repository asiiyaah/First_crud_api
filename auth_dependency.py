from fastapi import Header
from fastapi.responses import JSONResponse

from supabase_client import supabase


# --------------------------------------------------
# GET CURRENT USER
# --------------------------------------------------

def get_current_user(
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

        return user

    except Exception:

        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid or expired token"
            }
        )