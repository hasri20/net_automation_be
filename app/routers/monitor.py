
from fastapi import APIRouter,status
from fastapi.responses import JSONResponse
from easysnmp import Session
from math import ceil

router = APIRouter()

@router.get("/monitor/{hostname}")
async def monitor(hostname: str):
    memory = {}
    session = Session(hostname=hostname, community='public', version=2)
    memoryUsed = "1.3.6.1.4.1.9.9.48.1.1.1.5.1"
    memoryFree= "1.3.6.1.4.1.9.9.48.1.1.1.6.1"

    memoryUsedResult = session.get(memoryUsed)
    memoryFreeResult = session.get(memoryFree)

    memoryUsed = int(memoryUsedResult.value)
    memoryFree = int(memoryFreeResult.value)
    total = memoryUsed+memoryFree
    memory = {
        "used": memoryUsed,
        "free": memoryFree,
        "usedPercentage": ceil(memoryUsed / total * 100)
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=memory)
