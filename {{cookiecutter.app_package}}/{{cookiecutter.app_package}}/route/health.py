from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def root() -> dict[str, str]:
    return {"message": "ok"}
