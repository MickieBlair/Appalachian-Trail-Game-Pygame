import json
from classes import *
from functions import *



def get_waypoint_data():

    with open(resource_path('waypoints.json')) as json_file:
        data = json.load(json_file)

    #print("DATA Type", type(data))
    return data


def get_random_images():

    with open(resource_path('random.json')) as json_file:
        data = json.load(json_file)

    #print(data)

    return data

def get_trail_images():

    with open(resource_path('trail_images.json')) as json_file:
        data = json.load(json_file)
    return data


def get_water_images():

    with open(resource_path('water.json')) as json_file:
        data = json.load(json_file)
    return data

def get_resupply_options():

    with open(resource_path('resupply_options.json')) as json_file:
        data = json.load(json_file)
    return data

def get_events():

    with open(resource_path('events.json')) as json_file:
        data = json.load(json_file)
    return data





##for x in data.values():
##    print(data[x])

#all_points = WaypointList(waypoint_list)
#print(waypoint_list)

#print(data["id_num"] == 1)





    
##    for item in data["Waypoints"]:
##        if item["category"] == "Water":
##            print(item["mile"], item["description"])

    
##    for item in data["Waypoints"]:
##        if item["category"] == "Water":
##            print(item["mile"], item["description"])

##waypoint_list = []
##
##for item in data["results"]:
##    #print(item)
##    waypoint = Waypoint(item["id_num"], item["actions"], item["mile"],
##                        item["description"], item["elevation"], item["category"],
##                        item["type"], item["distance"], item["food_storage"],
##                        item["image"], item["resupply_options"], item["comment"],
##                        item["state"], item["next_sleep"], item["next_water"],
##                        item["next_resupply"], item["coordinates"])
###    print(type(waypoint))
##
##    waypoint_list.append(waypoint)



##waypoint_list = []
##
##for item in data["results"]:
##    #print(item)
##    waypoint = Waypoint(item["id_num"], item["actions"], item["mile"],
##                        item["description"], item["elevation"], item["category"],
##                        item["type"], item["distance"], item["food_storage"],
##                        item["image"], item["resupply_options"], item["comment"],
##                        item["state"], item["next_sleep"], item["next_water"],
##                        item["next_resupply"], item["coordinates"])
###    print(type(waypoint))
##
##    waypoint_list.append(waypoint)

##    for point in all_points:
##        print(point)

##    return all_points

####def get_json_data():
##
##with open('ATWaypoints.json') as json_file:
##    data = json.load(json_file)
##
##
##    
####    for item in data["Waypoints"]:
####        if item["category"] == "Water":
####            print(item["mile"], item["description"])
##
##waypoint_list = []
##
##for item in data["results"]:
##    #print(item)
##    waypoint = Waypoint(item["id_num"], item["actions"], item["mile"],
##                        item["description"], item["elevation"], item["category"],
##                        item["type"], item["distance"], item["food_storage"],
##                        item["image"], item["resupply_options"], item["comment"],
##                        item["state"], item["next_sleep"], item["next_water"],
##                        item["next_resupply"], item["coordinates"])
###    print(type(waypoint))
##
##    waypoint_list.append(waypoint)
##
##
##
##print(type(data))
##
###all_points = WaypointList(waypoint_list)
###print(waypoint_list)
##
###print(data["id_num"] == 1)
##
##
##
##
##
##
####    for point in all_points:
####        print(point)
##
####    return all_points





    




