from json import loads
from bson.json_util import dumps

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
