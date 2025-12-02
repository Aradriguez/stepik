from fastapi import APIRouter


router = APIRouter(
    prefix="/notes",
    tags=["notes"],
)


@router.get("/")
async def get_notes():
    return "Notes API is working"