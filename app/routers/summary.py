
from fastapi import APIRouter,status
from fastapi.responses import JSONResponse
from app.database import db
from json import loads
from bson.json_util import dumps

router = APIRouter()

@router.get("/summary/count-device")
async def get_devices_count():
    network_device_collection = db["network_device"]
    result = network_device_collection.aggregate([
        {
            "$group":{'_id':"$hardware",'count':{'$sum':1}}
        },
        { 
            '$project':
            {
                "_id": 0,
                "model" : "$_id",
                "count": 1
            }
        }
    ])
    data = loads(dumps(result))
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)


@router.get("/summary/count-status")
async def get_devices_count():
    network_device_collection = db["network_device"]
    result = network_device_collection.aggregate([
        {
        "$group":{
            '_id':'$isValid',
            'count':{'$sum':1},
            },
        },
        {
        '$project':{
            '_id':0,
            'value': {
                    '$cond': {
                        'if': { '$eq': ["$_id", True] },
                        'then': "Reachable",
                        'else': "Unreachable"
                    }
                },
            'count':1
            }
        }
    ])  

    data = loads(dumps(result))

    
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

