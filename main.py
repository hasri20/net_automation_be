
from pydantic import BaseModel
from fastapi import FastAPI, status
from netmiko import ConnectHandler
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from database import get_database
from bson.objectid import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from json import loads
from os import path
from bson.json_util import  dumps

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

script_dir = path.dirname(__file__) 

db = get_database()

class NetworkDevice(BaseModel):
    device_type: str
    host: str
    username: str
    password: str



def serialize(data):
    
    def format_id(data):
        data['id'] = data['_id']['$oid']
        del data['_id']
        return data

    data = loads(dumps(data))
    if(type(data) is list):
        data = list(map(format_id, data))
        return data
    elif(type(data) is dict):
        data = format_id(data)
        return data



@app.get("/")
async def read_root():
    return {"Status": "Ok"}


@app.get("/devices")
async def get_all_devices():
    network_device_collection = db["network_device"]
    result = network_device_collection.find({}, {"interfaces":False, "ssh":False })
    data = serialize(result)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@app.get("/devices/{id}")
async def get_device_detail(id: str):
    oid = ObjectId(id)
    network_device_collection = db["network_device"]
    device = network_device_collection.find_one({"_id": oid}, { "ssh":False })
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Device {id} is not found")
    data = serialize(device)
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

    
@app.post("/devices")
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

