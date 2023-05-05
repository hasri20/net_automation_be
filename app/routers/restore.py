
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from app.database import db
from app.utils import serialize
from bson.objectid import ObjectId
from netmiko import ConnectHandler

router = APIRouter()

backup_dir = 'backup_files/'


@router.post("/restore/{backup_file_id}")
async def restore_device_config(backup_file_id: str):

    backup_file_oid = ObjectId(backup_file_id)

    backup_file_collection = db['backup_file']
    backup_file = backup_file_collection.find_one({"_id": backup_file_oid})

    if backup_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Backup file {id} is not found")
    current_backup_file = serialize(backup_file)

    network_device_id = ObjectId(current_backup_file['device_id']['$oid'])
    network_device_collection = db['network_device']
    network_device = network_device_collection.find_one(
        {"_id": network_device_id})

    if network_device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Network device {id} is not found")
    current_network_device = serialize(network_device)

    try:
        connection = ConnectHandler(
            device_type=current_network_device['ssh']['device_type'],
            host=current_network_device['ssh']['host'],
            username=current_network_device['ssh']['username'],
            password=current_network_device['ssh']['password'],
            session_log='netmiko_session.log'
        )
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to devices")

    try:
        connection.enable()
        connection.send_config_from_file(
            backup_dir + current_backup_file['filename'])
        connection.disconnect()
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to push command")

    return JSONResponse(status_code=status.HTTP_200_OK, content={'status': "Success"})
