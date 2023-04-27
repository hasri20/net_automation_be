from json import loads
from bson.json_util import dumps

def serialize(data):   
    def format_id(data):

        if '_id' in data:
            data['id'] = data['_id']['$oid']
        if 'created_at' in data:
            data['created_at'] = data['created_at']['$date']
        del data['_id']
        return data

    data = loads(dumps(data))
    if(type(data) is list):
        data = list(map(format_id, data))
        return data
    elif(type(data) is dict):
        data = format_id(data)
        return data
