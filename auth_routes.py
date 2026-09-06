from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from supabase_client import supabase


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