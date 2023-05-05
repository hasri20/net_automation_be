
from fastapi import APIRouter, status
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
            "$group": {'_id': "$hardware", 'count': {'$sum': 1}}
        },
        {
            '$project':
            {
                "_id": 0,
                "model": "$_id",
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
            "$group": {
                '_id': '$isValid',
                'count': {'$sum': 1},
            },
        },
        {
            '$project': {
                '_id': 0,
                'value': {
                    '$cond': {
                        'if': {'$eq': ["$_id", True]},
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


@router.get("/summary/interface-rank")
async def get_interfaces_rank():
    network_device_collection = db["network_device"]
    result = network_device_collection.find(
        {}, {'interfaces': 1, 'hostname': 1})

    data = loads(dumps(result))
    flat = []

    for router in data:
        for interface in router['interfaces']:
            info = interface
            info['hostname'] = router['hostname']

            if (interface['input_packets'] == '' or interface['input_packets'] == None):
                interface['input_packets'] = 0

            if (interface['output_packets'] == '' or interface['output_packets'] == None):
                interface['output_packets'] = 0

            info['total'] = int(interface['input_packets']) + \
                int(interface['output_packets'])
            flat.append(info)

    flat.sort(key=lambda x: x['total'], reverse=True)
    return JSONResponse(status_code=status.HTTP_200_OK, content=flat)
