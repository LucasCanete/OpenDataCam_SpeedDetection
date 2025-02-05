from OpenDataCam import OpenDataCam
from Statistic import *
from MongoDB import MongoDB
import keyboard
import time
import argparse
from art import text2art
from rich.console import Console
from prettytable import PrettyTable

def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description="Vehicle Speed Estimation using OpenDataCam"
    )
    parser.add_argument(
        "--distance",
        default=10,
        help="Distance between screenlines in meters",
        type=int,
        nargs= '+' #multiple arguments allowed
    )
    
    parser.add_argument(
        "--db_upload_rate",
        default=30,
        help="Time in seconds after which upload data to db",
        type=int,
    )

    return parser.parse_args()


args = parse_arguments()
#set_distance(args.distance)


# Create a futuristic-style text art logo
logo = text2art("VES", font="slant")


# Print VES Logo with color
console = Console()
console.print(logo, style="bold cyan")  

#Dictionary to be uploaded to db
update_data = {
        "counterObservations":{
            "timestamp":0,
            "avrg_velocity_car":0,
            "avrg_velocity_truck":0,
            "avrg_velocity_bus":0,
            "avrg_velocity_person":0,
            "avrg_velocity_bicycle":0
            
        }
  
    }

#initialize opendatacam
cam = OpenDataCam('http://localhost:8080')

#automatically start recording 
response = cam.start_recording()

#wait 1 second. Avoid grabbing wrong recording ID
time.sleep(1)

UPLOAD_RATE = args.db_upload_rate
NUM_SCREENLINES = cam.get_number_of_areas()
DISTANCES = args.distance

column_info = ["Information", "Parameters"]

infoTable = PrettyTable()

if response.ok:
    print("Starting recording...")
    print()
    recording_id = cam.get_latest_recording_id()
    
    #initialize Database
    db = MongoDB("mongodb://127.0.0.1:27017",recording_id)
    db.init()
    
    infoTable.add_column(column_info[0],["RECORDING ID", "DB UPLOAD RATE [S]", "NUM SCREENLINES", "DISTANCES GIVEN"])
    infoTable.add_column(column_info[1],[recording_id, UPLOAD_RATE, NUM_SCREENLINES, DISTANCES])
    print(infoTable)
    print()

time.sleep(1)

#gets lists of dictionaries: each detected vehicle is a dictionary
vehicles = cam.get_counter_history(recording_id)
prev_size = len(vehicles)
print("Initial number of vehicles: ", prev_size)
print()


prev_time = time.time()
while True:

    #vehicles = cam.get_counter_history(recording_id)
    try:
        vehicles = db.get_counterHistory(recording_id)
    except KeyError:
        #recording has started but counterHistory section is not present in db because no vehicles counted yet
        vehicles = []
    print("index: ",prev_size)
    
    new_size = len(vehicles)
    
    if new_size > prev_size:
        print(f"Detected {new_size - prev_size} new vehicle(s).")
        
        for vehicle in vehicles[prev_size:]:
            area_id = vehicle['area']  #id of line or area that has been crossed

            id_ = vehicle['id']
            type_ = vehicle['name']
            timestamp = vehicle['timestamp']
            line_num = cam.get_area_name(recording_id,area_id)
        
            #changes format of timestamp
            formatted_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            save_vehicle_data(id_, type_, formatted_timestamp, line_num)
            
            print("vehicle saved! ID: " + str(id_) + "     line num: " + str(line_num) + " timestamp: "  + str(timestamp) )
            
	    #index to know which distance given as arguments to use take always line_num of even value
            d_index = int((line_num / 2) - 1) if line_num % 2 == 0 else None 
            #print("d_index: ", d_index)	

            if d_index != None:
                distance = args.distance[d_index]
                #print("chosen distance: ", distance )
                speed = calculate_speed(id_,distance)
                print("vehicle speed: ", speed)
                if speed != None:
                    save_vehicle_speed(id_, type_, formatted_timestamp, line_num, speed)
                    print("Speed: "+ str(speed)+" from " + type_ +"  ID "+ str(id_) + " saved!")
            
            
	    
        prev_size = new_size 


            
        #if 10 seconds have gone, upload average speeds to db and clear lists    
        if time.time() - prev_time >= UPLOAD_RATE:
            
            now = datetime.now()
            datetime_str = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            avrg_speed_car = int(calculate_average_speed('car'))
            avrg_speed_truck = int(calculate_average_speed('truck'))
            
            print()
            print("Updating DB at: " + datetime_str)
            
            speed_column = ["Vehicle","Average Speed"]
            speedTable = PrettyTable()
            speedTable.add_column(speed_column[0],['CAR','TRUCK'])
            speedTable.add_column(speed_column[1],[avrg_speed_car,avrg_speed_truck])
            print(speedTable)
            print()
            
            update_data["counterObservations"]["timestamp"] = now#convert_to_datetime_obj(datetime_str)#datetime_str
            update_data["counterObservations"]["avrg_velocity_car"] = avrg_speed_car#int(calculate_average_speed('car'))
            update_data["counterObservations"]["avrg_velocity_truck"] = avrg_speed_truck#int(calculate_average_speed('truck'))
            
            #upload to db
            db.push(update_data)
            
            #empty lists
            detected_vehicles.clear()
            detected_speeds.clear()
            
            prev_time = time.time()
        
    if keyboard.is_pressed('q'):
        print()
        print('Counting terminated')
        print(detected_speeds)
        break
    
    time.sleep(0.1) #small sleep to avoid high CPU usage

#automatically stop recording when script is interrupted
stop_response = cam.stop_recording()
if stop_response.ok:
    print("Recording stopped.")
    
print()
print("Recording ID: " + str(recording_id))
print()
print("Average Speed: " + str(calculate_average_speed('car')))
    

     
   
    


