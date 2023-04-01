from fastapi import APIRouter
from app.utils import serialize
from fastapi import  status
from netmiko import ConnectHandler
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from bson.objectid import ObjectId
from app.database import db
from app.models import NetworkDevice, NetworkDeviceUpdate

router = APIRouter()

@router.get("/devices")
async def get_all_devices():
    network_device_collection = db["network_device"]
    result = network_device_collection.find({}, {"interfaces":False, "ssh":False })
    data = serialize(result)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

@router.get("/devices/{id}")
async def get_device_detail(id: str):
    oid = ObjectId(id)
    network_device_collection = db["network_device"]
    device = network_device_collection.find_one({"_id": oid}, { "ssh":False })
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Device {id} is not found")
    data = serialize(device)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)
    
@router.post("/devices")
async def insert_device(network_device: NetworkDevice):
    try:
        connection = ConnectHandler(
            device_type= network_device.device_type, 
            host= network_device.host, 
            username= network_device.username,
            password= network_device.password
        )
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to devices")
    
    version = connection.send_command('show version', use_textfsm= True)[0]
    interfaces = connection.send_command('show interface', use_textfsm= True)

    connection.disconnect()

    data = {
        "hostname": version['hostname'],
        "rommon": version['rommon'],
        "version": version['version'],
        "serial": version['serial'][0],
        "hardware": version['hardware'][0],
        "interfaces": interfaces,
        "ssh":{
            "device_type":network_device.device_type,
            "host": network_device.host,
            "username":network_device.username,
            "password":network_device.password,
        },
        "isValid":True
    }

    network_device_collection = db["network_device"]
    new_device =  network_device_collection.insert_one(data)
    inserted_device = network_device_collection.find_one({"_id": new_device.inserted_id})
    data = serialize(inserted_device)
    return JSONResponse(status_code= status.HTTP_201_CREATED, content= data)

@router.put("/devices/{id}")
async def update_device(id: str, network_device: NetworkDeviceUpdate):
    oid = ObjectId(id)
    network_device_collection = db["network_device"]

    if(network_device.use_payload):
        ssh = {
            "device_type":network_device.device_type,
            "host": network_device.host,
            "username":network_device.username,
            "password":network_device.password,
        }
    else:
        device = network_device_collection.find_one({"_id": oid})
        currentDevice = serialize(device)
        ssh = currentDevice['ssh']
    
    try:
        print(ssh)
        connection = ConnectHandler(
            device_type= ssh['device_type'],
                host= ssh['host'], 
                username= ssh['username'],
                password= ssh['password']
        )
    except Exception as e:
        print(e)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to devices")
    

    version = connection.send_command('show version', use_textfsm= True)[0]
    interfaces = connection.send_command('show interface', use_textfsm= True)

    connection.disconnect()

    data = {
        "hostname": version['hostname'],
        "rommon": version['rommon'],
        "version": version['version'],
        "serial": version['serial'][0],
        "hardware": version['hardware'][0],
        "interfaces": interfaces,
        "ssh":ssh,
        "isValid":True
    }

    network_device_collection.update_one({"_id":oid},{"$set": data})
    new_inserted_device = network_device_collection.find_one({"_id": oid})
    new_data = serialize(new_inserted_device)
    return JSONResponse(status_code= status.HTTP_201_CREATED, content= new_data)

@router.delete("/devices/{id}")
async def delete_device(id: str):
    oid = ObjectId(id)
    network_device_collection = db["network_device"]
    result = network_device_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Device {id} is not found")

    return JSONResponse(status_code=status.HTTP_200_OK, content="Delete Success")
    