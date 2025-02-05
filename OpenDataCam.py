import requests



class OpenDataCam:

    def __init__ (self,addr):
        self.addr = addr

    def get_config(self):
        info = requests.get(self.addr + '/config')
        return info.json()

    def start_recording(self):
        start_response = requests.get(self.addr + '/recording/start')
        return start_response

    def stop_recording(self):
        stop_response = requests.get(self.addr + '/recording/stop')
        return stop_response

    #gets whole information of the counter including the lines drawn (areas)
    def get_counter_data(self, recording_id):
        return requests.get(self.addr + '/recording/' + recording_id + '/counter')

    #gets only a list of dictionaries with info of detected objects
    def get_counter_history(self, recording_id):
        response = requests.get(self.addr + '/recording/' + recording_id + '/counter')
        response = response.json()
        #At the beginning when nothing is counted detections has no Key "counterHistory"
        try:
            detections = response['counterHistory']
        except KeyError:
            detections = []
        return detections

    #gets the name of the line drawn on opendatacam: usually 1, 2, 3...
    def get_area_name(self,recording_id,area_id):
        response = self.get_counter_data(recording_id)
        response = response.json()
        area = response['areas'][area_id] 
        return area['name']
    
    def get_number_of_areas(self):
        response = requests.get(self.addr + '/counter/areas')
        response = response.json()
        return len(response)
        
    def get_recording(self, recording_id):
        print('Getting Recording data...')
        print(self.addr + '/recording/' + recording_id)
        get_response = requests.get(self.addr + '/recording/' + recording_id )
        return get_response

    def get_latest_recording_id(self):
        recordings_lists = requests.get(self.addr + '/recordings?offset=0&limit=1')
        recordings_lists = recordings_lists.json()
        recording = recordings_lists['recordings']
        return recording[0]['_id']

    def delete_recording(self, recording_id):
        print("Deleting recording...")
        print(self.addr + '/recording/' + recording_id)
        requests.delete(self.addr + '/recording/' + recording_id)



       






