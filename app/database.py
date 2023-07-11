from pymongo import MongoClient
from pymongo.errors import OperationFailure

CONNECTION_STRING = "mongodb://localhost:27017/"

connection = MongoClient(CONNECTION_STRING)

try:
    connection.admin.command('ping')
    print('Connected to DB')

except OperationFailure as err:
    print(f"Data Base Connection failed. Error: {err}")


db = connection['network_app']
