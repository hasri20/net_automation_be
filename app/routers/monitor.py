
from fastapi import APIRouter,status,HTTPException
from fastapi.responses import JSONResponse
from easysnmp import Session
from bson.objectid import ObjectId
from app.database import db
from math import ceil

router = APIRouter()

@router.get("/monitor/memory/{id}")
async def monitor(id: str):

    oid = ObjectId(id)
    network_device_collection = db["network_device"]
    device = network_device_collection.find_one({"_id": oid})
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Device {id} is not found")
  

    memoryUsed = "1.3.6.1.4.1.9.9.48.1.1.1.5.1"
    memoryFree= "1.3.6.1.4.1.9.9.48.1.1.1.6.1"

    try:
        session = Session(hostname=device['ssh']['host'], community='public', version=2)
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
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to collect SNMP from devices")
    
@router.get("/monitor/cpu/{id}")
async def monitorCpu(id: str):

    oid = ObjectId(id)
    network_device_collection = db["network_device"]
    device = network_device_collection.find_one({"_id": oid})
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Device {id} is not found")
  
    try:
        cpuUsage5seconds='1.3.6.1.4.1.9.9.109.1.1.1.1.6.1'
        session = Session(hostname=device['ssh']['host'], community='public', version=2)
        cpuUsage = session.get(cpuUsage5seconds)

        return JSONResponse(status_code=status.HTTP_200_OK, content={'usage':cpuUsage.value})
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to collect SNMP from devices")