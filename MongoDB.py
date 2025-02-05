from pymongo import MongoClient
from OpenDataCam import OpenDataCam
from bson import ObjectId



class MongoDB:

    def __init__(self,client_addr,recording_id):
        self.client_addr = client_addr
        self.recording_id = ObjectId(recording_id)

    #change client adress
    def set_client_address(self,addr):
        self.client_addr = client_addr

    #change recording id
    def set_recording_id(self,id): 
        self.recording_id = ObjectId(recording_id)
       

    def init(self):
        self.client = MongoClient(self.client_addr)
        self.db = self.client.opendatacam
        self.collection = self.db.recordings

        self.recording = self.collection.find_one({"_id":self.recording_id})

        #recording found
        if self.recording:
            return True

        #recording not found
        else: 
            return False

    #add a new set to an existing recording    
    def set(self, set_data):
        status = True
        #Data uploaded succesfully
        if self.recording:
            self.collection.update_one({"_id":self.recording_id},{"$set":set_data})
        #Error recording not found
        else:
            status = False

        return status

    #append new data to an existing set using push
    def push(self, push_data):
        status = True;
        #Data updated succesfully
        if self.recording:
            self.collection.update_one({"_id":self.recording_id},{"$push":push_data})
        #Error recording not found
        else:
            status = False

        return status

    #finds a recording given an id
    def find_recording(self,recording_id):
        return self.collection.find_one({"_id":ObjectId(recording_id)})
        
    
    #gets counterHistory from actual recording
    def get_counterHistory(self, recording_id):
        recording = self.find_recording(recording_id)
        if recording:
            counterHistory = recording["counterHistory"]
            return counterHistory



#Example
"""

update_data = {
        "CounterObservations":{
            "timestamp":3,
            "avrg_velocity_car":19,
            "avrg_velocity_truck":7.1,
            "avrg_velocity_bus":17,
            "avrg_velocity_person":0,
            "avrg_velocity_bicycle":0
            
        }
  
    }
cam = OpenDataCam('http://localhost:8080')

recording_id = cam.get_latest_recording_id()

db = MongoDB("mongodb://127.0.0.1:27017",recording_id)
db.init()

if db.push(update_data):
    print("Data uploaded succesfully.")
else:
    print("Data cannot be uploaded.")
"""
