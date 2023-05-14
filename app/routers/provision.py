
from fastapi import APIRouter, status, HTTPException, UploadFile, Form
from fastapi.responses import JSONResponse
from app.database import db
from app.utils import serialize
from bson.objectid import ObjectId
from netmiko import ConnectHandler
from datetime import datetime
from app.models import ConfigurationTemplate

router = APIRouter()

template_dir = 'template_files/'


@router.get("/provision")
async def get_all_template():

    configuration_template_collection = db["configuration_template"]
    template_files = configuration_template_collection.find()
    data = serialize(template_files)

    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.get("/provision/{file_id}")
async def get_all_template(file_id: str):
    oid = ObjectId(file_id)
    configuration_template_collection = db["configuration_template"]
    template_files = configuration_template_collection.find_one({"_id": oid})
    if template_files is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Template file {id} is not found")

    data = serialize(template_files)
    template_file_content = open(
        template_dir + template_files['filename'], 'r').read()
    return JSONResponse(status_code=status.HTTP_200_OK, content=template_file_content)


@router.post("/provision")
async def upload_template_configuration(file: UploadFile,
                                        filename: str = Form(...),
                                        title: str = Form(...),
                                        description: str = Form(...),
                                        device_type: str = Form(...)):

    content = await file.read()

    f = open(template_dir + filename, "wb")
    f.write(content)
    f.close()

    current_datetime = datetime.now().replace(microsecond=0)

    data = {
        "filename": filename,
        "inserted_at": current_datetime,
        "title": title,
        "description": description,
        "device_type": device_type
    }

    configuration_template_collection = db["configuration_template"]
    new_template = configuration_template_collection.insert_one(data)

    inserted_template = configuration_template_collection.find_one(
        {"_id": new_template.inserted_id})
    data = serialize(inserted_template)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=data)


@router.post("/provision/{file_id}/{device_id}")
async def provision_configuration(file_id: str, device_id: str):
    file_oid = ObjectId(file_id)
    device_oid = ObjectId(device_id)

    configuration_template_collection = db["configuration_template"]

    template_file = configuration_template_collection.find_one({
                                                               "_id": file_oid})

    if template_file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Template file {id} is not found")

    current_template = serialize(template_file)

    network_device_collection = db["network_device"]
    device = network_device_collection.find_one({"_id": device_oid})

    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device {id} is not found")
    current_device = serialize(device)

    try:
        connection = ConnectHandler(
            device_type=current_device['ssh']['device_type'],
            host=current_device['ssh']['host'],
            username=current_device['ssh']['username'],
            password=current_device['ssh']['password'],
            session_log='netmiko_session.log'
        )
    except Exception as e:
        print(e)
        network_device_collection.update_one(
            {"_id": device_oid}, {"$set": {"isValid": False}})
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to devices")

    connection.enable()
    connection.send_config_from_file(
        template_dir + current_template['filename'])
    connection.disconnect()

    return JSONResponse(status_code=status.HTTP_200_OK, content={'status': "Success"})
