from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from services.custom import CustomerResponse, CustomerRequestBase64
from services.ekycsvc import EkycService

router = APIRouter()


@router.post('/detectwithstream', response_model=CustomerResponse)
async def detect_with_stream(file: UploadFile = File(...), ekycsvc: EkycService = Depends()):
    try:
        response = ekycsvc.predict(file.file)
        print(response)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f'Server error with {e}')
    return CustomerResponse(**response)


@router.post('/detectwithbase64', response_model=CustomerResponse)
async def detect_with_base64(req: CustomerRequestBase64, ekycsvc: EkycService = Depends()):
    try:
        response = ekycsvc.predict(req.file, is_base64=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Server error with {e}')
    return CustomerResponse(**response)

