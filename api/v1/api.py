from fastapi import APIRouter
from api.v1.endpoints import ekyc

api_router = APIRouter()

api_router.include_router(ekyc.router, prefix='/ekyc', tags=['ekyc'])
