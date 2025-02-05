from datetime import datetime


detected_speeds = []

detected_vehicles = []

distance_between_lines = 4 # in meters

def set_distance(distance):
    global distance_between_lines
    distance_between_lines = distance

def convert_to_datetime_obj(datetime_string):
    #datetime object for better manipulation and math operations
    datetime_obj = datetime.strptime(datetime_string,"%Y-%m-%dT%H:%M:%S.%fZ")
    return datetime_obj

def save_vehicle_data(_id, _type, _timestamp, _line):
    #make dictionary with vehicle data and append it to list
    vehicle = {
    'id':_id,
    'type': _type,
    'timestamp':convert_to_datetime_obj(_timestamp),
    'line': _line
    }
    detected_vehicles.append(vehicle)

def save_vehicle_speed(_id, _type, _timestamp, _line, _speed):
    vehicle = {
    'id':_id,
    'type': _type,
    'timestamp':convert_to_datetime_obj(_timestamp),
    'line': _line,
    'speed': _speed
    }
    detected_speeds.append(vehicle)

def calculate_speed(vehicle_id,distance):
    #Filter vehicle data by ID
    vehicle_crossings = [v for v in detected_vehicles if v['id'] == vehicle_id]

    #Ensure vehicle has crossed two different lines
    if len(vehicle_crossings) >= 2:
        #sort vehicles by timestamp
        vehicle_crossings = sorted(vehicle_crossings, key=lambda v: v['timestamp'])

        #get the first and second crossing
        first_crossing = vehicle_crossings[0]
        second_crossing = vehicle_crossings[1]

        #calculate the time difference in seconds
        time_diff = second_crossing['timestamp'] - first_crossing['timestamp']
        #print(" s: ",distance_between_lines)
        print(" s: ",distance)
        print(" t: ",time_diff.seconds + time_diff.microseconds/1000000)
        if (time_diff.seconds + time_diff.microseconds/1000000) > 0: 
            #speed = (distance_between_lines/(time_diff.seconds + time_diff.microseconds/1000000)) * 3.6 #speed in Km/h
            speed = (distance/(time_diff.seconds + time_diff.microseconds/1000000)) * 3.6 #speed in Km/h
            return round(speed,2)
    return None

#calculates the average speed by vehicle type (minutlich)
#Add a clear option for the detected_speed list
def calculate_average_speed(_type):
    #speeds = []
    sum_of_speed = 0
    average_speed = 0
    #Filter vehicle data by type e.g. car, truck, bus, etc.
    vehicles_by_type = [v for v in detected_speeds if v['type'] == _type]

    for vehicle in vehicles_by_type:
        speed = vehicle['speed']
        sum_of_speed += speed
        #speeds.append(speed)
        
    if len(vehicles_by_type) > 0:
        #divide for e.g  total sum of cars speeds by total amount of cars 
        average_speed = sum_of_speed/len(vehicles_by_type)
        #round float to only one decimal
        average_speed = round(average_speed,1)
     
    return average_speed

#density is expressed as the amount
#of vehicles in a given section of the
#road tipically n of vehicles / km
def calculate_density(distance):
    
    #Filter vehicle amount by line that it has crossed
    crossed_line_1 = len([v for v in detected_speeds if v['line'] == 1])
    crossed_line_2 = len([v for v in detected_speeds if v['line'] == 2])
    

    if crossed_line_1 > crossed_line_2:
        n_of_vehicles = crossed_line_1 - crossed_line_2
    return n_of_vehicles/distance

