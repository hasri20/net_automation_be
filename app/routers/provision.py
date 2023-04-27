
from fastapi import APIRouter,status,HTTPException
from fastapi.responses import JSONResponse
from app.database import db
from app.utils import serialize
from bson.objectid import ObjectId
from netmiko import ConnectHandler

router = APIRouter()

template_dir = 'template_files/'

@router.get("/provision")
async def get_all_template():

    configuration_template_collection = db["configuration_template"]    
    template_files = configuration_template_collection.find()
    data = serialize(template_files)

    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.post("/provision/{file_id}/{device_id}")
async def provision_configuration(file_id: str, device_id: str):
    file_oid = ObjectId(file_id)
    device_oid = ObjectId(device_id)

    configuration_template_collection = db["configuration_template"]
    
    template_file = configuration_template_collection.find_one({"_id": file_oid})
    
    if template_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Template file {id} is not found")
  
    current_template = serialize(template_file)

    network_device_collection = db["network_device"]
    device = network_device_collection.find_one({"_id": device_oid})

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
    connection.send_config_from_file(template_dir + current_template['filename'])
    connection.disconnect()
    

    return JSONResponse(status_code=status.HTTP_200_OK, content={'status':"Success"})
