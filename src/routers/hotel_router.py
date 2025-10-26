from fastapi import APIRouter

router = APIRouter()

@router.get("/hotels")
async def get_hotels():
    return {"message": "Hotel recommendations will appear here"}