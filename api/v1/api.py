from fastapi import APIRouter
from api.v1.endpoints import ekyc
from fastapi.staticfiles import StaticFiles

api_router = APIRouter()

api_router.include_router(ekyc.router, prefix='/ekyc', tags=['ekyc'])
api_router.mount("/ui", StaticFiles(directory="./api/build"), name="ui_build")
api_router.mount("/static", StaticFiles(directory="./api/build/static"), name="ui_static")