from fastapi import APIRouter


# --------------------------------------------------
# PUBLIC ROUTER
# --------------------------------------------------

router = APIRouter(
    prefix="/public",
    tags=["Public"]
)


# --------------------------------------------------
# PUBLIC INFO
# --------------------------------------------------

@router.get("/info")
def public_info():

    return {
        "message": "Welcome stranger! This info is public."
    }