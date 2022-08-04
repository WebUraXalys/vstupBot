import pymongo
import os
# Preparing for using MongoDB
username = os.getenv('user_name')
pwd = os.getenv('pwd')
client = pymongo.MongoClient(f"mongodb://{username}:{pwd}@130.61.64.244/vst", tls=True,
                             tlsAllowInvalidCertificates=True)
db = client.vst
coll = db.specs

list_of = []
file = open("File.txt", "w")
for value in coll.find():
    list_of.append(value['name'])
file.write(list_of)