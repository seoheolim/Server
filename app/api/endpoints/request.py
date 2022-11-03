import logging

from fastapi import APIRouter

logging.basicConfig(level=logging.INFO)
router = APIRouter()


@router.get("/greeting")
async def greeting():
    return "hi"
