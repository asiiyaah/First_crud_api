from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from auth_dependency import get_current_user


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
    user=Depends(get_current_user)
):

    # If dependency returned an error response,
    # return it directly.
    if isinstance(user, JSONResponse):
        return user

    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@router.get("/dashboard")
def dashboard(
    user=Depends(get_current_user)
):

    # If dependency returned an error response,
    # return it directly.
    if isinstance(user, JSONResponse):
        return user

    return {
        "message": "Welcome to your protected dashboard",
        "user_id": user.id
    }