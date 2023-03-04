
from pydantic import BaseModel
from fastapi import FastAPI
from netmiko import ConnectHandler
from database import get_database

app = FastAPI()
db = get_database()

class NetworkDevice(BaseModel):
    host: str
    username: str
    password: str

@app.get("/")
async def read_root():
    return {"Status": "Ok"}


@app.get("/devices")
async def read_item():
    return {"item_id":  "q"}


@app.post("/devices")
def insert_item(network_device: NetworkDevice):
    try:
        # net_connect = ConnectHandler(
        #     device_type= 'cisco_ios', 
        #     host= network_device.host, 
        #     username= network_device.username,
        #     password= network_device.password
        # )
        network_device_collection = db["network_device"]
        network_device_collection.insert_one()


        return {"item_id":  "q"}
    except Exception as e:
        return(e.message)



    return {"test":1}