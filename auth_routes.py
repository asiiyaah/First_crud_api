from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from supabase_client import supabase
from auth_dependency import get_current_user


# --------------------------------------------------
# AUTH ROUTER
# --------------------------------------------------

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class AuthRequest(BaseModel):
    email: str
    password: str


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@router.post("/signup", status_code=201)
def signup(data: AuthRequest):

    # Check for missing fields
    if not data.email or not data.password:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Email and password are required"
            }
        )

    try:

        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if response.user is None:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Signup failed"
                }
            )

        return {
            "id": response.user.id,
            "email": response.user.email
        }

    except Exception as e:

        return JSONResponse(
            status_code=400,
            content={
                "error": str(e)
            }
        )


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@router.post("/login")
def login(data: AuthRequest):

    # Check for missing fields
    if not data.email or not data.password:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Email and password are required"
            }
        )

    try:

        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        if response.session is None:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Invalid login credentials"
                }
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception:

        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid login credentials"
            }
        )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@router.post(
    "/logout",
    status_code=204
)
def logout(
    user=Depends(get_current_user)
):

    # If authentication failed,
    # return the error response.
    if isinstance(user, JSONResponse):
        return user

    # Sign out the authenticated user
    supabase.auth.sign_out()

    # 204 means there is no response body.
    return None