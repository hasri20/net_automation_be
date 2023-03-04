from pymongo import MongoClient

def get_database():
 
   CONNECTION_STRING = "mongodb://localhost:27017/"
 
   client = MongoClient(CONNECTION_STRING)

   try:
      print('Connected to DB')
   except Exception:
      print("Unable to connect to the server.")


   return client['test']
  