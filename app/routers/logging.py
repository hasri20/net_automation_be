
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from app.database import db
from app.utils import serialize
from bson.objectid import ObjectId
from netmiko import ConnectHandler

router = APIRouter()


@router.post("/logging/{device_id}")
async def create_device_logging(device_id: str):    
    oid = ObjectId(device_id)
    network_device_collection = db["network_device"]
    device = network_device_collection.find_one({"_id": oid})

    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Device {id} is not found")
    current_device = serialize(device)

    try:
        connection = ConnectHandler(
            device_type= current_device['ssh']['device_type'], 
            host= current_device['ssh']['host'], 
            username= current_device['ssh']['username'],
            password= current_device['ssh']['password'],
            session_log= 'netmiko_session.log'
        )
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to devices")
    
    connection.enable()
    running_config = connection.send_command('show logging', use_textfsm =True)
    connection.disconnect()

    
    return JSONResponse(status_code=status.HTTP_200_OK, content=running_config)

