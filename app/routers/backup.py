
from fastapi import APIRouter,status,HTTPException
from fastapi.responses import JSONResponse
from app.database import db
from json import loads
from bson.json_util import dumps
from app.utils import serialize
from bson.objectid import ObjectId
from netmiko import ConnectHandler
from datetime import datetime


router = APIRouter()


@router.get("/backup")
async def get_all_backup():
    backup_file_collection = db["backup_file"]
    result = backup_file_collection.find({})
    data = serialize(result)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.post("/backup/{id}")
async def create_device_backup(id: str):    
    oid = ObjectId(id)
    network_device_collection = db["network_device"]
    device = network_device_collection.find_one({"_id": oid})

    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Device {id} is not found")
    currentDevice = serialize(device)

    try:
        connection = ConnectHandler(
            device_type= currentDevice['ssh']['device_type'], 
            host= currentDevice['ssh']['host'], 
            username= currentDevice['ssh']['username'],
            password= currentDevice['ssh']['password'],
            session_log= 'netmiko_session.log'
        )
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to devices")
    
    connection.enable()
    running_config = connection.send_command('show run')

    connection.disconnect()
    
    current_dateTime = datetime.now().replace(microsecond=0)
    
    filename = f"{currentDevice['hostname']} - {current_dateTime} - backup.txt"

    f = open(filename, "w")
    f.write(running_config)
    f.close()


    data = {
        "device_id": oid,
        "filename": filename,
        "inserted_at": current_dateTime
    }
    backup_files_collection = db["backup_file"]

    inserted_backup_file =  backup_files_collection.insert_one(data)    
    inserted_device = backup_files_collection.find_one({"_id": inserted_backup_file.inserted_id})
    data = serialize(inserted_device)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

