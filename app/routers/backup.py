
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from app.database import db
from app.utils import serialize
from bson.objectid import ObjectId
from netmiko import ConnectHandler
from datetime import datetime

router = APIRouter()

backup_dir = 'backup_files/'

@router.get("/backup")
async def get_all_backup():
    backup_file_collection = db["backup_file"]
    result = backup_file_collection.aggregate([
        {
            '$lookup':{
                'from':'network_device',
                'localField':'device_id',
                'foreignField':'_id',
                'as':'device',
            }
        },{
            '$project':{
                "hostname" : { '$first' : "$device.hostname" },
                "filename": 1,
                "created_at":"$inserted_at"
            }
        }
    ])
    data = serialize(result)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

@router.get("/backup/{backup_file_id}")
async def get_backup_file_details(backup_file_id: str):
    oid = ObjectId(backup_file_id)
    backup_file_collection = db["backup_file"]
    backup_file = backup_file_collection.find_one({"_id": oid})
    if backup_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Backup file {id} is not found")
    data = serialize(backup_file)

    backup_file_content = open(backup_dir + data['filename'], 'r').read()

    return JSONResponse(status_code=status.HTTP_200_OK, content=backup_file_content)


@router.post("/backup/{device_id}")
async def create_device_backup(device_id: str):    
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
    running_config = connection.send_command('show run')

    connection.disconnect()
    
    current_datetime = datetime.now().replace(microsecond=0)
    
    filename = f"{current_device['hostname']} - {current_datetime} - backup.txt"

    f = open(backup_dir + filename, "w")
    f.write(running_config)
    f.close()


    data = {
        "device_id": oid,
        "filename": filename,
        "inserted_at": current_datetime
    }
    backup_files_collection = db["backup_file"]

    inserted_backup_file =  backup_files_collection.insert_one(data)    
    inserted_device = backup_files_collection.find_one({"_id": inserted_backup_file.inserted_id})
    data = serialize(inserted_device)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

