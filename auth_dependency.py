from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse

from supabase_client import supabase


# --------------------------------------------------
# HTTP BEARER SECURITY
# --------------------------------------------------

security = HTTPBearer(
    auto_error=False
)


# --------------------------------------------------
# GET CURRENT USER
# --------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):

    # --------------------------------------------------
    # CHECK TOKEN
    # --------------------------------------------------

    if credentials is None:
        return JSONResponse(
            status_code=401,
            content={
                "error": "Access token required"
            }
        )

    # --------------------------------------------------
    # GET TOKEN
    # --------------------------------------------------

    token = credentials.credentials

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