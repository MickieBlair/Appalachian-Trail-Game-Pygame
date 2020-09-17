import sys
import os

import pygame as pg
from functions import *
from constants import *
from enum import Enum
from pygame import gfxdraw
from datajson import *
import random
import math
import datetime as date


#self.screen.blit(self.background,(0,0))
pg.init()



#self.image_normal = pg.transform.scale(image_normal, (width, height))

class GameState(Enum):
    MENU = 0
    WELCOME = 1
    PLAYERMENU = 2
    PLAYGAME = 3
    GAMEOVER = 4
    QUIT = -1


class Hydration_Event_Display:

    def __init__(self, screen, waypoint_object, player, all_events):
        self.screen = screen
        self.waypoint_object = waypoint_object
        self.player = player
        self.all_events = all_events
        self.events = get_events()
        self.event = self.events['17']
        self.title = self.event['event']
        self.comment = self.event['comment'].split(", ")        
        self.player.player_stats.update_energy_percentage()



        self.displayImage = pg.transform.scale(pg.image.load(resource_path("images/blankPO.png")),
                                               (400, 275))
        self.frameImage = pg.transform.scale(pg.image.load(resource_path("images/picframe.png")),
                                               (430, 350))

    def draw(self):
        self.screen.blit(self.displayImage,(246,153))
        self.screen.blit(self.frameImage,(227,135))

        
        label = pg.font.SysFont("impact", 25)
        med_label = pg.font.SysFont("impact", 20)
        TextSurf, TextRect = text_objects(self.title, label, pg.Color("black"))
        TextRect.center = (442, 200)
        self.screen.blit(TextSurf, TextRect)

        y = 235
        for item in self.comment:
            TextSurf, TextRect = text_objects(item, med_label, pg.Color("black"))
            TextRect.center = (442, y)
            self.screen.blit(TextSurf, TextRect)
            y+=30





class MileageCounter:
    def __init__(self, screen, player, running = True, display_status = True ):
##        self.done = False
        self.player= player
        self.screen = screen
        self.display = display_status
        self.running = True
        self.update_delay = 1100
        self.last_update = pg.time.get_ticks()
        self.mile = self.player.mile
        
        self.sign = None
        

    def pause(self, status):
        self.running = status

    def update(self):
    
        now = pg.time.get_ticks()

        if now - self.last_update > self.update_delay:
            self.last_update = now

            if self.running:
                self.mile += .1
                self.mile = round(self.mile,1)
                self.player.mile = round(self.mile,1)
                self.player.player_stats.current_mile = self.player.mile
                self.player.today_miles += .1

                if self.player.liters > 0:
                    self.player.liters -= .02
                    if self.player.liters <= 0:
                        self.player.liters = 0
                        self.player.player_stats.last_drink = self.player.mile
                        self.player.player_stats.out_of_water = True
                        self.player.player_stats.out_of_water_times +=1
                        


                if not self.player.player_stats.energy_exempt:

                    if self.player.player_stats.energy > 0:
                        self.player.player_stats.energy -= self.player.player_stats.energy_deduction
                        
                           
                    if self.player.player_stats.energy < 0:                    
                        self.player.player_stats.energy = 0
                    else:
                        self.player.player_stats.energy = round(self.player.player_stats.energy,1)

                self.player.player_stats.player_health()
                


class Player_Stats:
    def __init__(self):
        self.health = 100
        self.energy = 100
        self.starting_health =  100
        
        self.last_zero_mile = 0.0
        self.miles_since_last_zero = 0
        self.mile_health_deduction = self.miles_since_last_zero//10

        self.last_laundry_mile = 0.0
        self.miles_since_last_laundry = 0
        self.laundry_health_deduction = 0

        self.energy_consumption_rate = 0
        self.shelters_only_adjust = 0
        self.hiking_pole_adjust = 0
        self.sock_adjust = 0
        self.injury_adjust = 0
        self.hydration_adjust = 0

        self.total_drink_deduction = 0

        
        self.energy_percent = 1 + self.shelters_only_adjust
        self.energy_deduction = 0
        
        

        self.shelters_only = False        
        self.next_resupply = None
        self.energy_exempt = False
        self.exemption_ends = 0

        self.camp_occurences = 0
        self.list_camp = ["bear", "tent"]
        self.camp_choice = ""
        self.tent_choice = [1,2,3]
        self.entire_tent = False
        
        self.others_list = [6, 7, 8, 9, 10]
        self.others_choice = ""
        self.injury_list = [11, 12, 13, 14, 15]
        self.injury_choice = ""

        self.health_status = "Healthy"
        self.zeros_to_full_health = 0
        self.injury_deduction = 0
        self.level_of_dehydration_adjust = 0

        self.other_event_occurences = 0
        self.injury_event_occurences = 0
        
        
        
        
        self.chance_injury = .10
        self.base_chance_injury = .10      
        self.shoe_chance_injury = 0
        self.hiking_pole_injury = 0
        self.sock_injury = 0

        self.to_buy = [("Tent", False), ("Tent Poles", False), ("Repair Tape", False),
                       ("Hiking Poles", False), ("Shoes", False), ("Socks", False)]


        self.all_event_list = []


        self.zeros_in_row = 0
        self.total_zeros = 0

        self.out_of_water = False
        self.water_warning_acknowledged = False
        self.last_drink = 0
        self.current_mile = 0
        self.miles_since_last_drink = 0
        self.drink_deduction = 0
        self.out_of_water_times = 0
        

    def player_health(self):

        self.level_of_dehydration_adjust = self.out_of_water_times * 10
        
            
        #print("Before")
        #print("mile_health", self.mile_health_deduction)
        #print("injury_deduction", self.injury_deduction)
        #print("self.drink_deduction", self.drink_deduction)
        #print("self.last_drink", self.last_drink)

        self.miles_since_last_drink = self.current_mile - self.last_drink

                            
        if self.out_of_water:
            self.hydration_adjust = .15
            self.drink_deduction = math.ceil(self.miles_since_last_drink * 3)
        else:
            self.hydration_adjust = 0
            self.drink_deduction = 0
            
        self.laundry_health_deduction = self.miles_since_last_laundry//5 
        self.mile_health_deduction = self.miles_since_last_zero//10 #1 for every 10 miles traveled since last zero

        #print("In player health")
        #print("self.mile_health_deduction", self.mile_health_deduction)
        #print("self.injury_deduction", self.injury_deduction)
        #print("self.miles_since_last_zero", self.miles_since_last_zero)

        health = 100 - self.mile_health_deduction - self.injury_deduction \
                 - self.drink_deduction - self.level_of_dehydration_adjust\
                 - self.laundry_health_deduction

        if health < 0:
            health = 0

        #print("After")
        #print("mile_health", self.mile_health_deduction)
        #print("injury_deduction", self.injury_deduction)
        #print("self.drink_deduction", self.drink_deduction)
        #print("self.last_drink", self.last_drink)

        #print("self.laundry_health_deduction", self.laundry_health_deduction)
        

        self.health = int(health)


        


    def update_health_status(self):
        if self.zeros_in_row == self.zeros_to_full_health:
            self.health_status = "Healthy"
            self.injury_deduction = 0
            self.injury_adjust = 0

        self.player_health()
            

    def update_energy_percentage(self):
        #print()
        #print("Before Player Stats self.energy_percent", self.energy_percent)
        #print("self.shelters_only_adjust", self.shelters_only_adjust)
        #print("self.hiking_pole_adjust", self.hiking_pole_adjust)
        #print("self.sock_adjust", self.sock_adjust)
        #print("self.injury_adjust", self.injury_adjust)
        #print("self.hydration_adjust", self.hydration_adjust)        
        #print("self.energy_deduction", self.energy_deduction)
        
        #print("consumption_rate", self.energy_consumption_rate)
        

        
        self.energy_percent = 1 + self.shelters_only_adjust
        self.energy_deduction = 0

        if self.shelters_only:
            self.shelters_only_adjust = .10
        else:
            self.shelters_only_adjust = 0.0
            

        self.energy_percent = 1 + self.shelters_only_adjust + self.hiking_pole_adjust\
                              + self.sock_adjust  + self.injury_adjust + self.hydration_adjust

        self.energy_deduction = self.energy_consumption_rate * self.energy_percent
        #print()
        #print("Player Stats self.energy_percent", self.energy_percent)
        #print("self.shelters_only_adjust", self.shelters_only_adjust)
        #print("self.hiking_pole_adjust", self.hiking_pole_adjust)
        #print("self.sock_adjust", self.sock_adjust)
        #print("self.injury_adjust", self.injury_adjust)
        #print("self.hydration_adjust", self.hydration_adjust)  
        #print("Player Stats energy_deduction", self.energy_deduction)
        #print("consumption_rate", self.energy_consumption_rate)

    def update_chance_injury(self):
        #print()
        #print("Before Player Stats self.chance_injury", self.chance_injury)
        #print("self.shoe_chance_injury", self.shoe_chance_injury)
        #print("self.hiking_pole_injury", self.hiking_pole_injury)
        #print("self.sock_injury", self.sock_injury)
        
        
        self.chance_injury = self.base_chance_injury + self.shoe_chance_injury\
                             + self.hiking_pole_injury + self.sock_injury
        #print()
        #print("After Player Stats self.chance_injury", self.chance_injury)
        #print("self.shoe_chance_injury", self.shoe_chance_injury)
        #print("self.hiking_pole_injury", self.hiking_pole_injury)
        #print("self.sock_injury", self.sock_injury)


    def update_shelter_only_status(self):
        #print()
        #print("In update shelter status", self.all_event_list)

        if self.to_buy[0][1] == True:
            self.entire_tent = True
            self.to_buy[1] = ("Tent Poles", False)

        if self.to_buy[0][1] == True or self.to_buy[1][1] == True:
            self.shelters_only = True
            
        else:
            self.shelters_only = False
            
            
        #print()
        #print("Player Stats self.shelters_only", self.shelters_only)


            
            
        
        

    

    
        
        
class Random_Event_Display:

    def __init__(self, screen, waypoint_object, player, all_events, type_event):        
        
        self.screen = screen
        self.waypoint_object = waypoint_object
        self.player = player
        self.all_events = all_events
        self.events = get_events()
        self.type_of_event = type_event
        self.player.player_stats.camp_choice == ""
        self.player.player_stats.others_choice == ""
        self.player.player_stats.injury_choice == ""
        
        self.event = None
        
        #print("\nNext Category", self.waypoint_object.category)
        #print("Type", self.type_of_event)

        self.displayImage = pg.transform.scale(pg.image.load(resource_path("images/blankPO.png")),
                                               (400, 275))
        self.frameImage = pg.transform.scale(pg.image.load(resource_path("images/picframe.png")),
                                               (430, 350))

        self.rr_event = self.events['1']
        self.shoe_event = self.events['16']
        self.bear_event = self.events['5']
        self.socks = self.events['8']
        self.hiking_pole = self.events['9']        
        self.tent_pole_event = self.events['10']
        self.ankle_event = self.events['11']
        self.noro_event = self.events['12']
        self.ivy_event = self.events['13']
        self.blisters_event = self.events['14']
        self.food_p_event = self.events['15']
        self.injury_event = False
        self.sleep_event = ""
        self.others_event = 0
        self.sleep_number = 0
        self.title = "None"
        self.comment = []
        self.event_category()

    def event_category(self):

        if self.type_of_event == "Camp":
            #print("Camp Event")
            self.camp_event_selection()

        elif self.type_of_event == "Road Magic":
            #print("Road Magic")
            self.event_selection()

        elif self.type_of_event == "Shoes":
            #print("Shoes")            
            self.event_selection()

        elif self.type_of_event == "Other":
            #print("Other")
            self.other_event_selection()

        elif self.type_of_event == "Injury":
            #print("Injury")
            self.injury_event_selection()

        elif self.type_of_event == "Hydration":
            #print("Hydration")
            self.event_selection()

    def injury_event_selection(self):
        
        random_choice = random.choice(self.player.player_stats.injury_list)
        
        self.player.player_stats.injury_list.remove(random_choice)

        if random_choice == 11:
            self.event = self.ankle_event
            self.player.player_stats.all_event_list.append(("Injury", random_choice))
            self.player.player_stats.injury_choice = "Ankle"
            self.player.player_stats.injury_deduction = 20
        

        elif random_choice == 12:
            self.event = self.noro_event
            self.player.player_stats.all_event_list.append(("Injury", random_choice))
            self.player.player_stats.injury_choice = "Noro"
            self.player.player_stats.injury_deduction = 20
        

        elif random_choice == 13:
            self.event = self.ivy_event
            self.player.player_stats.all_event_list.append(("Injury", random_choice))
            self.player.player_stats.injury_choice = "Ivy"
            self.player.player_stats.injury_deduction = 15
        

        elif random_choice == 14:
            self.event = self.blisters_event
            self.player.player_stats.all_event_list.append(("Injury", random_choice))
            self.player.player_stats.injury_choice = "Blister"
            self.player.player_stats.injury_deduction = 15
        

        elif random_choice == 15:
            self.event = self.food_p_event
            self.player.player_stats.all_event_list.append(("Injury", random_choice))
            self.player.player_stats.injury_choice = "Food_P"
            self.player.player_stats.injury_deduction = 20



        self.event_selection()
        

    def other_event_selection(self):
        self.player.player_stats.other_event_occurences += 1
        #print("Other Event List", self.player.player_stats.others_list)

        random_choice = random.choice(self.player.player_stats.others_list)
        self.event = self.events[str(random_choice)]
        self.player.player_stats.others_list.remove(random_choice)

        if random_choice == 6:
            self.player.snacks +=2
            self.player.player_stats.all_event_list.append(("Other", random_choice))
            self.player.player_stats.others_choice = "Snacks"

        elif random_choice == 7:
            self.player.lunch +=1
            self.player.player_stats.all_event_list.append(("Other", random_choice))
            self.player.player_stats.others_choice = "Lunch"

        elif random_choice == 10:
            self.player.player_stats.all_event_list.append(("Other", random_choice))
            self.player.player_stats.others_choice = "Tent_Poles"

        elif random_choice == 9:            
            self.player.player_stats.all_event_list.append(("Other", random_choice))
            self.player.player_stats.others_choice = "Hiking_Poles"

        elif random_choice == 8:            
            self.player.player_stats.all_event_list.append(("Other", random_choice))
            self.player.player_stats.others_choice = "Socks"


        #print("After Other", self.player.player_stats.others_list)

        self.event_selection()

    def camp_event_selection(self):
        #print("Camp Event Selection")

        if len(self.player.player_stats.list_camp) == 2:
            event = random.choice(self.player.player_stats.list_camp)                
            
            if event == "bear":
                self.player.player_stats.camp_choice = event
                self.player.player_stats.list_camp.remove(event)
            else:
                self.player.player_stats.camp_choice = "tent"
                event = min(self.player.player_stats.tent_choice)
                self.player.player_stats.tent_choice.remove(event)
                self.event = self.events[str(int(event) + 1)]
                self.player.player_stats.all_event_list.append(("Tent",(int(event) + 1)))
                
                if len(self.player.player_stats.tent_choice) == 0:
                    self.player.player_stats.list_camp.remove("tent")
            

        elif len(self.player.player_stats.list_camp) == 1:
            event = random.choice(self.player.player_stats.list_camp)                
            
            if event == "bear":
                self.player.player_stats.camp_choice = event
                self.player.player_stats.list_camp.remove(event)
            elif event == "tent":
                self.player.player_stats.camp_choice = "tent"
                event = min(self.player.player_stats.tent_choice)
                self.player.player_stats.tent_choice.remove(event)
                self.event = self.events[str(int(event) + 1)]
                self.player.player_stats.all_event_list.append(("Tent",(int(event) + 1)))
                
                if len(self.player.player_stats.tent_choice) == 0:
                    self.player.player_stats.list_camp.remove("tent")

        self.event_selection()

    
    def event_selection(self):
        to_buy = []
##        print("in event selection")

        if self.type_of_event == "Camp":
            if self.player.player_stats.camp_choice == "bear":            
                self.event = self.bear_event
                self.player.player_stats.all_event_list.append(("Camp", 5))
                self.title = self.event['event']
                self.comment = self.event['comment'].split(", ")
                self.player.player_stats.energy_exempt = True
                self.next_resupply = Next_Resupply_Waypoint(self.player, self.waypoint_object)
                self.next_resupply.update(self.waypoint_object)
                self.player.player_stats.exemption_ends = int(self.next_resupply.next_resupply_waypoint.id_num)
                self.sleep_event = "bear"

            elif self.player.player_stats.camp_choice == "tent":
                if self.event['add_to_list'] == "Tent":
                    self.player.player_stats.to_buy[0] = ("Tent", True)
                elif self.event['add_to_list'] == "Repair Tape":
                    self.player.player_stats.to_buy[2] = ("Repair Tape", True)

                self.title = self.event['event']
                self.comment = self.event['comment'].split(", ")

        elif self.type_of_event == "Road Magic":
            self.event = self.events['1']
            self.player.player_stats.all_event_list.append(1)
            self.title = self.event['event']
            self.comment = self.event['comment'].split(", ")
            self.sleep_event = "magic"

        elif self.type_of_event == "Shoes":
            self.event = self.shoe_event
            self.player.player_stats.all_event_list.append(16)
            self.title = self.event['event']
            self.player.player_stats.to_buy[4] = ("Shoes", True)
            self.comment = self.event['comment'].split(", ")
            self.player.player_stats.shoe_chance_injury = .15

        elif self.type_of_event == "Other":
            if self.player.player_stats.others_choice == "Tent_Poles":
                self.event = self.tent_pole_event
                self.title = self.event['event']
                self.comment = self.event['comment'].split(", ")
                self.player.player_stats.shelters_only = True
                self.sleep_event = "tent_poles"
                self.player.player_stats.to_buy[1] = ("Tent Poles", True)

            elif self.player.player_stats.others_choice == "Hiking_Poles":
                self.event = self.hiking_pole
                self.player.player_stats.to_buy[3] = ("Hiking Poles", True)
                self.player.player_stats.hiking_pole_injury = .25
                self.player.player_stats.hiking_pole_adjust = .15
                self.title = self.event['event']
                self.comment = self.event['comment'].split(", ")

            elif self.player.player_stats.others_choice == "Socks":
                self.event = self.socks
                self.player.player_stats.to_buy[5] = ("Socks", True)
                self.player.player_stats.sock_injury = .05
                self.player.player_stats.sock_adjust = .05
                self.title = self.event['event']
                self.comment = self.event['comment'].split(", ")

            elif self.player.player_stats.others_choice == "Snacks":
                self.event = self.events['6']
                self.title = self.event['event']
                self.comment = self.event['comment'].split(", ")

            elif self.player.player_stats.others_choice == "Lunch":
                self.event = self.events['7']
                self.title = self.event['event']
                self.comment = self.event['comment'].split(", ")

        elif self.type_of_event == "Injury":
            self.title = self.event['event']
            self.comment = self.event['comment'].split(", ")
            if self.player.player_stats.injury_choice == "Ankle":
                self.player.player_stats.health_status = "Injured"
                self.player.player_stats.zeros_to_full_health = 3
                self.player.player_stats.injury_adjust = .15
                
        

            elif self.player.player_stats.injury_choice == "Noro":
                self.player.player_stats.health_status = "Injured"
                self.player.player_stats.zeros_to_full_health = 4
                self.player.player_stats.injury_adjust = .15
        

            elif self.player.player_stats.injury_choice == "Ivy":
                self.player.player_stats.health_status = "Injured"
                self.player.player_stats.zeros_to_full_health = 2
                self.player.player_stats.injury_adjust = .15
        

            elif self.player.player_stats.injury_choice == "Blister":
                self.player.player_stats.health_status = "Injured"
                self.player.player_stats.zeros_to_full_health = 2
                self.player.player_stats.injury_adjust = .15
        

            elif self.player.player_stats.injury_choice == "Food_P":
                self.player.player_stats.health_status = "Injured"
                self.player.player_stats.zeros_to_full_health = 2
                self.player.player_stats.injury_adjust = .15

        elif self.type_of_event == "Hydration":
            self.event = self.events['17']
            self.title = self.event['event']
            self.comment = self.event['comment'].split(", ")
            self.player.player_stats.hydration_adjust = .15

        self.player.player_stats.update_shelter_only_status()
        self.player.player_stats.update_chance_injury()
        self.player.player_stats.update_energy_percentage()

    
    def draw(self):
                    
        self.screen.blit(self.displayImage,(246,153))
        self.screen.blit(self.frameImage,(227,135))

        
        label = pg.font.SysFont("impact", 25)
        med_label = pg.font.SysFont("impact", 20)
        TextSurf, TextRect = text_objects(self.title, label, pg.Color("black"))
        TextRect.center = (442, 200)
        self.screen.blit(TextSurf, TextRect)

        y = 235
        for item in self.comment:
            TextSurf, TextRect = text_objects(item, med_label, pg.Color("black"))
            TextRect.center = (442, y)
            self.screen.blit(TextSurf, TextRect)
            y+=30



class Random_Events:
    def __init__(self):
        self.dictionary = get_waypoint_data()
        self.events = get_events()
        self.roads_resupplies =[]           
        self.shelter_camp = []
        self.shoes = []        
        self.others = []
        self.final_list = []
        self.get_lists()

    def get_lists(self):
        rr_index = 1
        s_index = 1
        shoe_index = 1
        rest_index = 1
        
        for i in self.dictionary:
            
            if self.dictionary[i]['category'] == "Road" or self.dictionary[i]['category'] == "Resupply":
##                print("R", self.dictionary[i]['mile'])
                self.roads_resupplies.append((rr_index, i, self.dictionary[i]))
                rr_index +=1

            elif self.dictionary[i]['category'] == "Campsite" or self.dictionary[i]['category'] == "Shelter":
##                print("S", self.dictionary[i]['mile'])
                self.shelter_camp.append((s_index, i, self.dictionary[i]))
                s_index +=1

            elif self.dictionary[i]['type'] == "shoes":
##                print("Shoes", self.dictionary[i]['mile'])
                self.shoes.append((shoe_index, i, self.dictionary[i]))
                shoe_index +=1
            else:
##                print("others", self.dictionary[i]['mile'])
                if self.dictionary[i]['category'] != "Terminus":
                    self.others.append((rest_index, i, self.dictionary[i]))
                    rest_index +=1

        self.road_resupply()
        self.shoes_list()
        self.others_list()

        list1 = []

        for item in self.final_list:
            list1.append(int(item.id_num))

        self.event_list = list(set(list1))
        
        self.event_list.sort()

    def shoes_list(self):        

        for item in self.shoes:
            waypoint = Waypoint(item[1])
            self.final_list.append(waypoint)

    def others_list(self):        
        length = 5
        
        list1=[]

        while len(list1)  < length:
            rand = random.randint(1,len(self.others))

            if rand not in list1:
                
                list1.append(rand)

        for item in self.others:
            if item[0] in list1:
                waypoint = Waypoint(item[1])
                self.final_list.append(waypoint)

    
    def road_resupply(self):
        length = len(self.roads_resupplies)//4
        
        list1=[]

        while len(list1)  < length:
            rand = random.randint(1,len(self.roads_resupplies))

            if rand not in list1:
                list1.append(rand)

        for item in self.roads_resupplies:
            if item[0] in list1:
                waypoint = Waypoint(item[1])
                self.final_list.append(waypoint)



class Resupply:
    def __init__(self, screen, player, waypoint_object, currentWaypoint, sign_display):
        self.done = False       
        self.clock = pg.time.Clock()
        self.screen = screen
        self.player = player
        self.waypoint_object = waypoint_object
        self.currentWaypoint = currentWaypoint
        self.guide_book = GuideBook(self.screen, self.waypoint_object, self.currentWaypoint)
        self.game_state = GameState.PLAYGAME
        self.sign_display = sign_display
        self.camp = pg.transform.scale(CAMP_IMAGE, (130, 81))
        self.hotel = pg.transform.scale(HOTEL_IMAGE, (130, 81))
        self.hostel = pg.transform.scale(HOSTEL_IMAGE, (130, 81))
        self.shop = pg.transform.scale(SHOP_IMAGE, (150, 84))
        self.mail = pg.transform.scale(MAIL_IMAGE, (150, 84))
        self.no_mail = pg.transform.scale(NO_MAIL_IMAGE, (150, 84))
        self.action_list = []
        self.lodging_list = []
        self.food_action_complete = False
        self.have_box = False
        self.mail_checked = False
        self.added = False
        self.title = "No Mail !"
        
        self.background= pg.transform.scale(pg.image.load(resource_path('images/background.png')),(430, 110))
        self.night_background= pg.transform.scale(pg.image.load(resource_path('images/night_background.png')),(430, 110))
        
        self.random_maildrop = Random_MailDrop()
        
        self.box = None
        self.breakfast = 0
        self.lunch = 0
        self.dinner = 0
        self.snacks = 0

        self.date_display= DateDisplay(self.screen, self.player)
        self.status_bar = StatusBar(self.screen, self.player)
        self.mile_display = MileDisplay(self.screen, self.player)
        self.mail_option = Mail_Option(1)
        self.mail_list = Mail_Options_List(self.screen, self.mail_option, self.player)
        
        self.dictionary = get_resupply_options()
        self.list = []

        for item in self.dictionary:
            option = Resupply_Options(item)
            self.list.append(option)
            
        for item in self.list:
            if item.mile == self.player.mile:
                self.current_resupply = item

        self.actions = self.current_resupply.actions.split(", ")
        self.options_list()
        self.status = "In Town"

        self.sleep_display = SleepDisplayTown(self.screen, self.waypoint_object)
        self.sleep_display_showing = False

        self.sleep_delay = 1000
        self.sleep_update = pg.time.get_ticks()
        self.sleep_count = 0
        
        self.ready_to_go_back = False
        self.to_trail_delay = 1000
        self.to_trail_update = pg.time.get_ticks()
        self.to_trail_count = 0
        self.to_trail_display = Transport_Display(self.screen, self.waypoint_object, self.player)
        self.to_trail_display_showing = False
        self.walking = False
        self.shuttle = False
        self.hitch = False
        self.hitch_comment = ""
        self.shuttle_comment = ""
        
        self.food_store = Food_Store(self.screen, self.player, self.player.hiker_funds, self.current_resupply)
        self.gear_store = Gear_Store(self.screen, self.player, self.player.hiker_funds, self.current_resupply)

        
        self.shuttle_cost = 0

        self.days_needed_full_health = self.player.player_stats.zeros_to_full_health

        self.lodging_status = "Night"
        self.lodging = "Lodging Options"


        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.resupply_sprites = pg.sprite.Group()
        self.action_sprites = pg.sprite.Group()
        self.lodging_sprites = pg.sprite.Group()
        self.mail_sprites = pg.sprite.Group()

        

        # Create the button instances. You can pass your own images here.
   
        self.guidebook_btn = Button(
            667, 30, 120, 50, self.show_guide,
            pg.font.SysFont("franklingothicheavy",20),
            'Guidebook', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.laundry_btn = Button(
            667, 195, 120, 50, self.laundry,
            pg.font.SysFont("franklingothicheavy",20),
            'Laundry $5', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)


        self.refill_btn = Button(
            667, 355, 120, 50, self.refill,
            pg.font.SysFont("franklingothicheavy",20),
            'Refill', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.gear_shop_btn = Button(
            667, 515, 120, 50, self.shop_gear,
            pg.font.SysFont("franklingothicheavy",20),
            'Buy Gear', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.walk_back_to_trail_btn = Button(
            342, 190, 200, 50, self.walk_back,
            pg.font.SysFont("franklingothicheavy",20),
            'Walk Back', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.hitch_to_trail_btn = Button(
            342, 300, 200, 50, self.hitch_back,
            pg.font.SysFont("franklingothicheavy",20),
            'Hitch Back', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.shuttle_to_trail_btn = Button(
            342, 410, 200, 50, self.shuttle_back,
            pg.font.SysFont("franklingothicheavy",20),
            'Call Shuttle', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.back_to_trail_btn = Button(
            342, 520, 200, 50, self.back_to_trail,
            pg.font.SysFont("franklingothicheavy",22),
            'Back To Trail', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.stay_in_town_btn = Button(
            342, 520, 200, 50, self.stay_in_town,
            pg.font.SysFont("franklingothicheavy",22),
            'Stay in Town', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)



        self.hostel_btn = Button(
            377, 438, 130, 40, self.hostel_stay,
            pg.font.SysFont("franklingothicheavy",20),
            'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.hotel_btn = Button(
            517, 438, 130, 40, self.hotel_stay,
            pg.font.SysFont("franklingothicheavy",20),
            'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.camp_btn = Button(
            237, 438, 130, 40, self.camp_stay,
            pg.font.SysFont("franklingothicheavy",20),
            'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.mail_btn = Button(
            460, 233, 150, 40, self.check_mail,
            pg.font.SysFont("franklingothicheavy",20),
            'Check Mail', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.shop_btn = Button(
            275, 233, 150, 40, self.shop_resupply,
            pg.font.SysFont("franklingothicheavy",20),
            'Resupply', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.quit_button = Button(
            15, 549, 200, 37, self.quit_game,
            pg.font.SysFont("franklingothicheavy",24),
            'Save and Exit', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.mail_ahead_btn = Button(
            252, 420, 175, 50, self.mail_items,
            pg.font.SysFont("franklingothicheavy",24),
            'Mail Ahead', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.add_to_pack_btn = Button(
            452, 420, 175, 50, self.add_to_pack,
            pg.font.SysFont("franklingothicheavy",24),
            'Add to Pack', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)



        # Add the button sprites to the sprite group.
        self.resupply_sprites.add(self.quit_button, self.laundry_btn,
                                  self.guidebook_btn, self.refill_btn, self.gear_shop_btn,
                                  self.back_to_trail_btn)
                                  
        
        self.action_sprites = self.action_sprite_logic()
        self.lodging_sprites = self.lodging_sprite_logic()

    def current_state(self):
        return self.game_state

    def back_to_trail(self):
        
        self.ready_to_go_back = True
        self.resupply_sprites.remove(self.back_to_trail_btn)
        self.resupply_sprites.add(self.walk_back_to_trail_btn, self.hitch_to_trail_btn,
                                  self.shuttle_to_trail_btn, self.stay_in_town_btn)
        self.action_sprites.empty()
        self.lodging_sprites.empty()

    def stay_in_town(self):
        self.ready_to_go_back = False
        self.status == "In Town"
       
        
        self.resupply_sprites.remove(self.walk_back_to_trail_btn, self.hitch_to_trail_btn, self.hitch_to_trail_btn,
                                  self.shuttle_to_trail_btn, self.stay_in_town_btn)

        self.resupply_sprites.add(self.back_to_trail_btn)
        self.action_sprites = self.action_sprite_logic()
        self.lodging_sprites = self.lodging_sprite_logic()
        
        
        
        


    def shop_gear(self):
        self.gear_store = Gear_Store(self.screen, self.player, self.player.hiker_funds, self.current_resupply) 
        self.gear_store.done = False
        self.gear_store.run()

    def laundry(self):
        self.player.player_stats.last_laundry_mile = self.player.mile
        self.player.player_stats.laundry_health_deduction = 0
        self.player.hiker_funds.other_costs += 5
        

    def refill(self):
        self.player.player_stats.out_of_water = False
        self.player.player_stats.water_warning_acknowledged = False
        self.player.player_stats.player_health()
        if self.player.liters < 4.0:
            self.player.liters += 0.5

    def add_to_pack(self):
        self.food_action_complete = True
        self.player.breakfast += self.breakfast
        self.player.lunch += self.lunch
        self.player.dinner += self.dinner
        self.player.snacks += self.snacks

        self.breakfast = 0
        self.lunch = 0
        self.dinner = 0
        self.snacks = 0

        self.box = []

        self.mail_sprites.empty()    
        self.have_box = False
        self.resupply_sprites.add(self.back_to_trail_btn)
        self.action_sprites = self.action_sprite_logic()
        self.lodging_sprites = self.lodging_sprite_logic()
        self.title = "No More Mail !"

    def mail_items(self):
        self.food_action_complete = True

        self.mail_list.box = self.box

        self.mail_list.activeChoice = None
        self.mail_list.done = False
        self.mail_list.run()


        if self.mail_list.box_sent:
            self.player.hiker_funds.other_costs += 10
            self.mail_sprites.empty()    
            self.have_box = False
            self.resupply_sprites.add(self.back_to_trail_btn)
            self.action_sprites = self.action_sprite_logic()
            self.lodging_sprites = self.lodging_sprite_logic()
            self.title = "No More Mail !"
        
    def walk_back(self):
        
        self.walking = True
        self.to_trail_display.update(self.waypoint_object, "Walk From")
        self.resupply_sprites.remove(self.walk_back_to_trail_btn, self.hitch_to_trail_btn,
                                  self.shuttle_to_trail_btn, self.stay_in_town_btn)
        self.to_trail_display_showing = True
        self.status = "To Trail"
        

    def hitch_back(self):
        if not self.hitch:
            status =random.randint(1,2)
            if status == 1:
                self.hitch_comment = "Ride Found."

                self.resupply_sprites.remove(self.hitch_to_trail_btn)
                self.hitch_to_trail_btn = Button(
                    342, 300, 200, 50, self.accept_hitch,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Accept Hitch', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                self.resupply_sprites.add(self.hitch_to_trail_btn)
                
            elif status == 2:
                self.hitch_comment = "Could not get a ride."
                self.hitch = True

            
                

    def accept_hitch(self):
        self.resupply_sprites.remove(self.walk_back_to_trail_btn, self.hitch_to_trail_btn,
                                  self.shuttle_to_trail_btn, self.stay_in_town_btn)

        self.to_trail_display.update(self.waypoint_object, "Hitch From")
        self.to_trail_display_showing = True
        self.status = "To Trail"
        
        

    def shuttle_back(self):
        if not self.shuttle:
            if self.shuttle_cost == 0:            
                    shuttle_costs = [5, 10, 15, 20]
                    cost = random.randint(1,4)
                    self.shuttle_cost =  shuttle_costs[cost-1]         
            cost_format = format(self.shuttle_cost,'.2f')
            self.shuttle_comment = "Shuttle Available - Cost = $ " + cost_format
            self.shuttle = True

            if self.shuttle:
                self.resupply_sprites.remove(self.shuttle_to_trail_btn)
                self.shuttle_to_trail_btn = Button(
                    342, 410, 200, 50, self.take_shuttle,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Take Shuttle', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                self.resupply_sprites.add(self.shuttle_to_trail_btn)

    def take_shuttle(self):
        self.resupply_sprites.remove(self.walk_back_to_trail_btn, self.hitch_to_trail_btn,
                                  self.shuttle_to_trail_btn, self.stay_in_town_btn)

        self.to_trail_display.update(self.waypoint_object, "Shuttle From")
        
        self.player.hiker_funds.shuttle_costs += self.shuttle_cost
        
        self.to_trail_display_showing = True
        self.status = "To Trail"

        
        
    def stats_adjust_zero(self):
        if self.player.player_stats.health_status == "Healthy":
                self.player.player_stats.energy = 100
                self.player.player_stats.health = 100
        
    
    def hostel_stay(self):
        self.shuttle = False
        self.hitch = False
        self.hitch_comment = ""
        self.shuttle_comment = ""
        
        if self.lodging == "Lodging Options" and self.status  == "In Town":            
            self.player.hiker_funds.lodging_costs += self.current_resupply.hostel_price
            sleep_energy = 30            

            if self.player.player_stats.energy < 100 - sleep_energy:
                self.player.player_stats.energy += sleep_energy
            else:
                self.player.player_stats.energy = 100
            
            self.status  = "Sleeping"
            self.sleep_display.update("Hostel")
            self.sleep_display_showing = True
            self.action_sprites.empty()
            self.lodging_sprites.empty()
            self.lodging_status = "Zero"
            if self.player.player_stats.health_status == "Healthy":
                self.lodging = str(1)+ " Zero Day to Full Health"
            elif self.player.player_stats.health_status == "Injured":
                self.lodging = str(self.days_needed_full_health) + " Zero Day(s) to Full Health"
                 


        if  self.lodging_status == "Zero" and self.status  == "In Town":
            self.player.player_stats.last_zero_mile = self.player.mile
            self.player.player_stats.total_zeros += 1
            self.player.player_stats.zeros_in_row  += 1
            self.player.player_stats.update_health_status()
            #print("Health Status", self.player.player_stats.health_status)
            self.player.hiker_funds.lodging_costs += self.current_resupply.hostel_price + self.current_resupply.zero
            self.stats_adjust_zero()
            self.status  = "Sleeping"
            self.sleep_display.update("Hostel Zero")
            self.sleep_display_showing = True
            self.action_sprites.empty()
            self.lodging_sprites.empty()
            self.player.player_stats.out_of_water_times = 0
            self.days_needed_full_health -= 1
            self.lodging = str(self.days_needed_full_health) + " Zero Day(s) to Full Health"
            
            
    def hotel_stay(self):
        self.shuttle = False
        self.hitch = False
        self.hitch_comment = ""
        self.shuttle_comment = ""
        
        if self.lodging == "Lodging Options" and self.status  == "In Town":            
            self.player.hiker_funds.lodging_costs += self.current_resupply.hotel_price
            sleep_energy = 30            

            if self.player.player_stats.energy < 100 - sleep_energy:
                self.player.player_stats.energy += sleep_energy
            else:
                self.player.player_stats.energy = 100
            
            self.status  = "Sleeping"
            self.sleep_display.update("Hotel")
            self.sleep_display_showing = True
            self.action_sprites.empty()
            self.lodging_sprites.empty()
            self.lodging_status = "Zero"
            if self.player.player_stats.health_status == "Healthy":
                self.lodging = str(1)+ " Zero Day to Full Health"
            elif self.player.player_stats.health_status == "Injured":
                self.lodging = str(self.days_needed_full_health) + " Zero Day(s) to Full Health"


        if self.lodging_status == "Zero" and self.status  == "In Town":
            self.player.player_stats.last_zero_mile = self.player.mile
            self.player.player_stats.total_zeros += 1
            self.player.player_stats.zeros_in_row  += 1
            self.player.player_stats.update_health_status()
            #print("Health Status", self.player.player_stats.health_status)  
            self.player.hiker_funds.lodging_costs += self.current_resupply.hotel_price + self.current_resupply.zero
            self.stats_adjust_zero()
            self.status  = "Sleeping"
            self.sleep_display.update("Hotel Zero")
            self.sleep_display_showing = True
            self.action_sprites.empty()
            self.lodging_sprites.empty()
            self.player.player_stats.out_of_water_times = 0
            self.days_needed_full_health -= 1
            self.lodging = str(self.days_needed_full_health) + " Zero Day(s) to Full Health"


    def camp_stay(self):
        self.shuttle = False
        self.hitch = False
        self.hitch_comment = ""
        self.shuttle_comment = ""
        
        if self.lodging == "Lodging Options" and self.status  == "In Town":            
            self.player.hiker_funds.lodging_costs += self.current_resupply.camp_price
            sleep_energy = 30            

            if self.player.player_stats.energy < 100 - sleep_energy:
                self.player.player_stats.energy += sleep_energy
            else:
                self.player.player_stats.energy = 100
            
            self.status  = "Sleeping"
            self.sleep_display.update("Camp")
            self.sleep_display_showing = True
            self.action_sprites.empty()
            self.lodging_sprites.empty()
            self.lodging_status = "Zero"
            if self.player.player_stats.health_status == "Healthy":
                self.lodging = str(1)+ " Zero Day to Full Health"
            elif self.player.player_stats.health_status == "Injured":
                self.lodging = str(self.days_needed_full_health) + " Zero Day(s) to Full Health"


        if self.lodging_status == "Zero" and self.status  == "In Town":
            self.player.player_stats.last_zero_mile = self.player.mile
            self.player.player_stats.total_zeros += 1
            self.player.player_stats.zeros_in_row  += 1
            self.player.player_stats.update_health_status()
            #print("Health Status", self.player.player_stats.health_status)
            self.player.hiker_funds.lodging_costs += self.current_resupply.camp_price + self.current_resupply.zero
            self.stats_adjust_zero()
            self.status  = "Sleeping"
            self.sleep_display.update("Camp Zero")
            self.sleep_display_showing = True
            self.action_sprites.empty()
            self.lodging_sprites.empty()
            self.player.player_stats.out_of_water_times = 0
            self.days_needed_full_health -= 1
            self.lodging = str(self.days_needed_full_health) + " Zero Day(s) to Full Health"

        
    def check_mail(self):

        
        new_list =[]
        if len(self.player.mail_drops) > 0:
            for item in self.player.mail_drops:
                
                if item[0].mile == self.player.mile:
                    self.resupply_sprites.remove(self.back_to_trail_btn)
                    self.have_box = True
                    if self.box == None:
                        self.box = item[2]
                        
                        self.breakfast = self.box[0][1]
                        self.lunch = self.box[1][1]
                        self.dinner = self.box[2][1]
                        self.snacks = self.box[3][1]
                        

                    else:
                        box = item[2]
                        
                        self.breakfast += box[0][1]
                        self.lunch += box[1][1]
                        self.dinner += box[2][1]
                        self.snacks += box[3][1]

##                        self.player.mail_drops.remove(item)
                        
                    self.action_sprites.empty()
                    self.lodging_sprites.empty()
                    self.mail_sprites.add(self.add_to_pack_btn, self.mail_ahead_btn)
                else:
                    new_list.append(item)

                
            self.box = [("Breakfast", self.breakfast),("Lunch",self.lunch),
                        ("Dinner",self.dinner),("Snacks",self.snacks)]

            
        
            
        self.player.mail_drops = new_list
        
        
        if self.random_maildrop.drop[1] != 0:
            if not self.added:
                self.player.hiker_funds.gifts += self.random_maildrop.drop[1]
            
            self.title = ""
                         
        self.mail_checked = True
        self.added = True
               
                
            
            
        

    def shop_resupply(self):
        self.food_store = Food_Store(self.screen, self.player, self.player.hiker_funds, self.current_resupply)
        self.food_store.done = False
        self.food_store.run()
        
        

    def options_list(self):
        for item in self.actions:
            if item == "mail":                
                self.action_list.append("mail")
            if item == "shop":
                self.action_list.append("shop")
            if item == "hostel":                
                self.lodging_list.append("hostel")
            if item == "hotel":                
                self.lodging_list.append("hotel")
            if item == "camp":
                self.lodging_list.append("camp")

    def action_sprite_logic(self):
        
        self.action_sprites.empty()
        
        action_sprites = pg.sprite.Group()
        action_sprites.empty()

##        for item in self.actions:
##            if item == "mail":                
##                self.action_list.append("mail")
##            if item == "shop":
##                self.action_list.append("shop")
##
##        print("after mail", len(self.action_list))


        if len(self.action_list) == 2:
            action_sprites.add(self.mail_btn, self.shop_btn)


        if len(self.action_list) == 1:
            if "mail" in self.action_list:
                self.mail_btn = Button(
                    367, 233, 150, 40, self.check_mail,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Check Mail', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                action_sprites.add(self.mail_btn)

            if "shop" in self.action_list:
                self.shop_btn = Button(
                    367, 233, 150, 40, self.shop_resupply,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Resupply', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                action_sprites.add(self.shop_btn)
                
        return action_sprites

    def lodging_sprite_logic(self):
        
        self.lodging_sprites.empty()
        
        lodging_sprites = pg.sprite.Group()
        lodging_sprites.empty()

##        for item in self.actions:
##            if item == "hostel":                
##                self.lodging_list.append("hostel")
##            if item == "hotel":                
##                self.lodging_list.append("hotel")
##            if item == "camp":
##                self.lodging_list.append("camp")


        if len(self.lodging_list) == 3:
            lodging_sprites.add(self.hostel_btn, self.hotel_btn, self.camp_btn)

   
        if len(self.lodging_list) == 2:
            if "hostel" in self.lodging_list and "hotel" in self.lodging_list:
                self.hostel_btn = Button(
                    305, 438, 130, 40, self.hostel_stay,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                

                self.hotel_btn = Button(
                    452, 438, 130, 40, self.hotel_stay,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                lodging_sprites.add(self.hotel_btn, self.hostel_btn)


                

            if "hotel" in self.lodging_list and "camp" in self.lodging_list:
                self.hotel_btn = Button(
                    305, 438, 130, 40, self.hotel_stay,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                

                self.camp_btn = Button(
                    452, 438, 130, 40, self.camp_stay,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                lodging_sprites.add(self.camp_btn, self.hostel_btn)


            if "camp" in self.lodging_list and "hostel" in self.lodging_list:
                self.hostel_btn = Button(
                    305, 438, 130, 40, self.hostel_stay,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                

                self.camp_btn = Button(
                    452, 438, 130, 40, self.camp_stay,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                lodging_sprites.add(self.camp_btn, self.hostel_btn)


        if len(self.lodging_list) == 1:
            if "hostel" in self.lodging_list:
                self.hostel_btn = Button(
                    377, 438, 130, 40, self.hostel_stay,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                lodging_sprites.add(self.hostel_btn)

            if "hotel" in self.lodging_list:
                self.hotel_btn = Button(
                    377, 438, 130, 40, self.hotel_stay,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                lodging_sprites.add(self.hotel_btn)


            if "camp" in self.lodging_list:
                self.camp_btn = Button(
                    377, 438, 130, 40, self.camp_stay,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Stay Here' , pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
                lodging_sprites.add(self.camp_btn)
                

        return lodging_sprites

       

    def show_guide(self):

        self.guide_book = GuideBook(self.screen, self.waypoint_object, self.currentWaypoint)
        self.guide_book.done = False
        self.guide_book.run()

    def save_game(self):
        player_object = self.player
        #create a pickle file
        picklefile = open('player_object', 'wb')
        #pickle the dictionary and write it to file
        pickle.dump(player_object, picklefile)
        #close the file
        picklefile.close()     

    def quit_game(self):
        if self.status == "To Trail":
            self.player.status == "Hiking"
            self.status = "Hiking"
            
        self.save_game()        
        self.done = True
        pg.quit()
        quit()
        

    def run(self):        
        while not self.done:
            
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()
            

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                pg.quit()
                quit()            
                
            for button in self.resupply_sprites:
                button.handle_event(event)

            for button in self.action_sprites:
                button.handle_event(event)

            for button in self.lodging_sprites:
                button.handle_event(event)

            for button in self.mail_sprites:
                button.handle_event(event)


    def run_logic(self):

        if not self.player.player_stats.energy_exempt:
            if self.player.player_stats.energy <= 0:
                self.done = True
                self.game_state = GameState.GAMEOVER
        
        if self.player.hiker_funds.calculate_available() <= 0\
           or self.player.player_stats.health <= 0:
            self.done = True
            self.game_state = GameState.GAMEOVER

        
        elif self.status == "Sleeping":
            self.resupply_sprites.remove(self.back_to_trail_btn)
            now = pg.time.get_ticks()
            if now - self.sleep_update > self.sleep_delay:
                self.sleep_update = now
                              
                self.sleep_count += 1
                if self.sleep_count == 5:
                    self.sleep_count = 0
                    self.status = "In Town"
                    self.date_display.update()
                    self.sleep_display_showing = False
                    self.action_sprites = self.action_sprite_logic()
                    self.lodging_sprites = self.lodging_sprite_logic()
                    self.resupply_sprites.add(self.back_to_trail_btn)
                    
##                    self.mile_counter.pause("False") #set back to running
##                    self.action_sprites.add(self.next_btn)
##                    self.display_random_trail = True
##                    self.waypoint_display.comment = "Good Morning! Let's get hiking!"
                    self.player.today_miles = 0.0

        elif self.status == "To Trail":
            if self.waypoint_object.distance > 0 and self.walking:
                adjust = self.waypoint_object.distance/5
                energy_adjust = ((self.waypoint_object.distance/.1)\
                                *self.player.player_stats.energy_deduction)/5
                
                
            else:
                adjust = 0
                energy_adjust  = 0
  
            now = pg.time.get_ticks()
            if now - self.to_trail_update > self.to_trail_delay:
                self.to_trail_update = now
                              
                self.to_trail_count += 1
                self.player.today_miles += adjust
                self.player.player_stats.energy -= energy_adjust
                
                if self.to_trail_count == 5:
                    
                    self.to_trail_count = 0
                    self.status = "Hiking"
                    
                    self.to_trail_display_showing = False
                    self.game_state = GameState.PLAYGAME
                    self.player.game_state = GameState.PLAYGAME
                    self.done = True
           
        
        self.resupply_sprites.update(self.dt)
        self.action_sprites.update(self.dt)
        self.lodging_sprites.update(self.dt)
        self.player.status = self.status

    def draw(self):
        self.screen.fill((100,100,100))
        if self.status == "Sleeping":
            self.screen.blit(self.night_background,(227,485))
        else:
            self.screen.blit(self.background,(227,485))

        header = pg.transform.scale(HEADER, (430, 60))
        self.screen.blit(header, (227,0))
        pg.draw.rect(self.screen, pg.Color("white"),(227, 135, 430, 355))
        pg.draw.rect(self.screen, pg.Color("black"),(227, 135, 430, 355), 2)
       

        title = drop_shadow_text(self.waypoint_object.resupply_options,
             "impact", 35, pg.Color("black"), pg.Color("white"),400, 50, 2)


        self.screen.blit(title, center_of_surface(title, 442, 30))
        lodging_labels = pg.font.SysFont("impact", 18)

        label = pg.font.SysFont("impact", 25)
        TextSurf, TextRect = text_objects(self.lodging, label, pg.Color("black"))
        TextRect.center = (442, 308)
        self.screen.blit(TextSurf, TextRect)



        self.date_display.draw()
        self.status_bar.update(self.player)
        self.mile_display.draw()
        self.sign_display.draw()

        if not self.have_box:

            if len(self.action_list) == 2:
                self.screen.blit(self.shop,(275, 150))
                if self.mail_checked:
                    self.screen.blit(self.no_mail,(460, 150))
                    if self.title !="":
                        TextSurf, TextRect = text_objects(self.title, lodging_labels, pg.Color("black"))
                        TextRect.center = (535, 192)
                        self.screen.blit(TextSurf, TextRect)
                    else:
                        TextSurf, TextRect = text_objects("Money From", lodging_labels, pg.Color("black"))
                        TextRect.center = (535, 167)
                        self.screen.blit(TextSurf, TextRect)

                        TextSurf, TextRect = text_objects(self.random_maildrop.drop[0], lodging_labels, pg.Color("black"))
                        TextRect.center = (535, 192)
                        self.screen.blit(TextSurf, TextRect)

                        TextSurf, TextRect = text_objects("$ " + str(self.random_maildrop.drop[1]), lodging_labels, pg.Color("black"))
                        TextRect.center = (535, 217)
                        self.screen.blit(TextSurf, TextRect)
                        
                else:
                    self.screen.blit(self.mail,(460, 150))

            if len(self.action_list) == 1:
                if "mail" in self.action_list:
                    if self.mail_checked:
                        self.screen.blit(self.no_mail,(367, 150))
                        if self.title !="":
                            TextSurf, TextRect = text_objects(self.title, lodging_labels, pg.Color("black"))
                            TextRect.center = (442, 192)
                            self.screen.blit(TextSurf, TextRect)
                        else:
                            TextSurf, TextRect = text_objects("Money From", lodging_labels, pg.Color("black"))
                            TextRect.center = (442, 172)
                            self.screen.blit(TextSurf, TextRect)

                            TextSurf, TextRect = text_objects(self.random_maildrop.drop[0], lodging_labels, pg.Color("black"))
                            TextRect.center = (442, 192)
                            self.screen.blit(TextSurf, TextRect)

                            TextSurf, TextRect = text_objects("$ " + str(self.random_maildrop.drop[1]), lodging_labels, pg.Color("black"))
                            TextRect.center = (442, 212)
                            self.screen.blit(TextSurf, TextRect)
                            
                    else:                    
                        self.screen.blit(self.mail,(367, 150))
                    

                if "shop" in self.action_list:
                    self.screen.blit(self.shop,(367, 150))

            
            if self.lodging == "Take A Zero":
                    camp_price = self.current_resupply.camp_price + self.current_resupply.zero
                    hostel_price = self.current_resupply.hostel_price + self.current_resupply.zero
                    hotel_price = self.current_resupply.hotel_price + self.current_resupply.zero
            else:
                    camp_price = self.current_resupply.camp_price
                    hostel_price = self.current_resupply.hostel_price
                    hotel_price = self.current_resupply.hotel_price

            if len(self.lodging_list) == 3:
                self.screen.blit(self.camp,(237, 358))                   
                TextSurf, TextRect = text_objects("Camp - $ " + str(format(camp_price,'.2f')), lodging_labels, pg.Color("black"))
                TextRect.center = (302, 343)
                self.screen.blit(TextSurf, TextRect)

                self.screen.blit(self.hostel,(377, 358))
                hostel_price = self.current_resupply.hostel_price
                TextSurf, TextRect = text_objects("Hostel - $ " + str(format(hostel_price,'.2f')),
                                                  lodging_labels, pg.Color("black"))
                TextRect.center = (442, 343)
                self.screen.blit(TextSurf, TextRect)

                self.screen.blit(self.hotel,(517, 358))
                
                TextSurf, TextRect = text_objects("Hotel - $ " + str(format(hotel_price,'.2f')), lodging_labels, pg.Color("black"))
                TextRect.center = (582, 343)
                self.screen.blit(TextSurf, TextRect)


            if len(self.lodging_list) == 2:
                if "hostel" in self.lodging_list and "hotel" in self.lodging_list:
                    self.screen.blit(self.hostel,(305, 358))
                    hotel_price = self.current_resupply.hotel_price
                    TextSurf, TextRect = text_objects("Hostel - $ " + str(format(hostel_price,'.2f')),
                                                      lodging_labels, pg.Color("black"))
                    TextRect.center = (370, 343)
                    self.screen.blit(TextSurf, TextRect)

                    self.screen.blit(self.hotel,(452, 358))
                    TextSurf, TextRect = text_objects("Hotel - $ " + str(format(hotel_price,'.2f')), lodging_labels, pg.Color("black"))
                    TextRect.center = (517, 343)
                    self.screen.blit(TextSurf, TextRect)
                    


                    

                if "hotel" in self.lodging_list and "camp" in self.lodging_list:
                    self.screen.blit(self.hotel,(305, 358))
                    TextSurf, TextRect = text_objects("Hotel - $ " + str(format(hotel_price,'.2f')),
                                                      lodging_labels, pg.Color("black"))
                    TextRect.center = (370, 343)
                    self.screen.blit(TextSurf, TextRect)

                    self.screen.blit(self.camp,(452, 358))
                    TextSurf, TextRect = text_objects("Camp - $ " + str(format(camp_price,'.2f')), lodging_labels, pg.Color("black"))
                    TextRect.center = (517, 343)
                    self.screen.blit(TextSurf, TextRect)


                if "camp" in self.lodging_list and "hostel" in self.lodging_list:
                    self.screen.blit(self.hostel,(305, 358))
                    TextSurf, TextRect = text_objects("Hostel - $ " + str(format(hostel_price,'.2f')),
                                                      lodging_labels, pg.Color("black"))
                    TextRect.center = (370, 343)
                    self.screen.blit(TextSurf, TextRect)

                    self.screen.blit(self.camp,(452, 358))
                    TextSurf, TextRect = text_objects("Camp - $ " + str(format(camp_price,'.2f')), lodging_labels, pg.Color("black"))
                    TextRect.center = (517, 343)
                    self.screen.blit(TextSurf, TextRect)
                    
            if len(self.lodging_list) == 1:
                if "hostel" in self.lodging_list:
                    self.screen.blit(self.hostel,(377, 358))
                    TextSurf, TextRect = text_objects("Hostel - $ " + str(format(hostel_price,'.2f')),
                                                  lodging_labels, pg.Color("black"))
                    TextRect.center = (442, 343)
                    self.screen.blit(TextSurf, TextRect)

                    
                if "hotel" in self.lodging_list:
                    self.screen.blit(self.hotel,(377, 358))
                    TextSurf, TextRect = text_objects("Hotel - $ " + str(format(hotel_price,'.2f')),
                                                  lodging_labels, pg.Color("black"))
                    TextRect.center = (442, 343)
                    self.screen.blit(TextSurf, TextRect)
                    
                if "camp" in self.lodging_list:
                    self.screen.blit(self.camp,(377, 358))
                    TextSurf, TextRect = text_objects("Camp - $ " + str(format(camp_price,'.2f')),
                                                  lodging_labels, pg.Color("black"))
                    TextRect.center = (442, 343)
                    self.screen.blit(TextSurf, TextRect)
                
        
        pg.draw.rect(self.screen, (30, 30, 30),(657, 0, 140, 600))
        pg.draw.line(self.screen, pg.Color("black"), (227, 286), (657,286), 2)

        if self.have_box:
            y = 250
            pg.draw.rect(self.screen, pg.Color("white"),(227, 135, 430, 355))
            pg.draw.rect(self.screen, pg.Color("black"),(227, 135, 430, 355), 2)


            current_label = pg.font.SysFont("impact", 28)
            ind_label = pg.font.SysFont("consolas", 22)
            list_label = pg.font.SysFont("impact", 22)
            num_label = pg.font.SysFont("impact", 24)


            TextSurf, TextRect = text_objects("Items In Box", current_label, pg.Color("black"))
            TextRect.center = (442, 180)
            self.screen.blit(TextSurf, TextRect)

            for item in self.box:
                if item[1] > 0:
                    TextSurf, TextRect = text_objects(item[0], list_label,
                                                      pg.Color("black"))
                    TextRect.bottomleft = (350, y) 

                    self.screen.blit(TextSurf, TextRect)

                    TextSurf, TextRect = text_objects(str(item[1]), num_label,
                                                      pg.Color("black"))
                    TextRect.bottomright = (530, y) 

                    self.screen.blit(TextSurf, TextRect)

                    y+= 50
                    
            self.mail_sprites.draw(self.screen)



##        if self.status == "Sleeping":
##                self.sleep_display.draw()

        if self.sleep_display_showing:
            if self.status == "Sleeping":
                self.sleep_display.draw()
        elif self.ready_to_go_back and self.status == "In Town":
            pg.draw.rect(self.screen, pg.Color("white"),(227, 135, 430, 355))
            pg.draw.rect(self.screen, pg.Color("black"),(227, 135, 430, 355), 2)

            TextSurf, TextRect = text_objects(str(self.waypoint_object.distance) + " miles back to trail", label, pg.Color("black"))
            TextRect.center = (442, 165)
            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(self.hitch_comment, label, pg.Color("black"))
            TextRect.center = (442, 285)
            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(self.shuttle_comment, label, pg.Color("black"))
            TextRect.center = (442, 385)
            self.screen.blit(TextSurf, TextRect)

            
            

        elif self.to_trail_display_showing:
            if self.status == "To Trail":
                self.to_trail_display.draw()

        if self.player.player_stats.laundry_health_deduction >0:
            title = drop_shadow_text("Dirty Laundry","impact", 20, pg.Color("black"),
                                     pg.Color("white"),400, 50, 2)
            self.screen.blit(title, center_of_surface(title, 725, 120))


        self.screen.blit(LAUNDRY_BTN,(690, 125))  
        self.screen.blit(DRINK_BTN,(685, 270))
        self.screen.blit(GEAR_BTN,(685, 435))
       
        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)
    
        self.action_sprites.draw(self.screen)    
        self.resupply_sprites.draw(self.screen)
        self.lodging_sprites.draw(self.screen)
        cursor_AT(self.screen, True)
        pg.display.flip()






class GameOver:

    def __init__(self, screen, player):
        
        self.done = False
        self.clock = pg.time.Clock()
        self.screen = screen
        self.blaze = pg.transform.scale(BLAZE, (25, 75))
        self.player = player

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.menu_sprites = pg.sprite.Group()
        self.background  = pg.transform.scale(pg.image.load(resource_path('images/game_over.jpg')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))


        # Buttons
        self.new_game = Button(
            550, 525, 200, 50, self.play_game,
            pg.font.SysFont("franklingothicheavy",24),
            'Play Again', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        

        
        self.quit_button = Button(
            50, 525, 200, 50, self.quit_game,
            pg.font.SysFont("franklingothicheavy",24),
            'Exit', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        # Add the button sprites to the sprite group.
        self.menu_sprites.add(self.new_game, self.quit_button)
        self.game_state = GameState.MENU

    def play_game(self):
                
        self.done = True
        self.game_state = GameState.PLAYERMENU

        

    def quit_game(self):
        self.done = True
        self.game_state = GameState.QUIT

    def run(self):
        while not self.done:
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                self.game_state = GameState.QUIT
                
            for button in self.menu_sprites:
                button.handle_event(event)

    def run_logic(self):
        self.menu_sprites.update(self.dt)

    def draw(self):
        self.screen.blit(self.background, (0,0))        
        title1 = drop_shadow_text("Game Over",
             "impact", 70, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title1, center_of_surface(title1, 400, 65))
        self.screen.blit(self.blaze, (50,28))
        self.screen.blit(self.blaze, (725,28))





        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)

        self.menu_sprites.draw(self.screen)
        cursor_AT(self.screen, True)
        pg.display.flip()

    def current_state(self):
        return self.game_state


class SleepDisplay:

    def __init__(self, screen, waypoint_object):
        self.screen = screen
        self.waypoint_object = waypoint_object
        self.shelterImage = pg.transform.scale(pg.image.load(resource_path("images/shelter_sleep.png")),
                                               (400, 275))
        self.campsiteImage = pg.transform.scale(pg.image.load(resource_path("images/campsite_sleep.png")),
                                               (400, 275))
        self.displayImage = pg.transform.scale(pg.image.load(resource_path("images/shelter_sleep.png")),
                                               (400, 275))
        self.frameImage = pg.transform.scale(pg.image.load(resource_path("images/picframe.png")),
                                               (430, 350))
        
        self.update_delay = 1000
        self.last_update = pg.time.get_ticks()
        self.count = 0
        self.status = "Sleeping"


    def update(self, waypoint_object):
        self.count = 0
        self.waypoint_object = waypoint_object
##        print(self.waypoint_object.category)

        if self.waypoint_object.category == "Shelter":
            self.displayImage = self.shelterImage
            

        elif self.waypoint_object.category == "Campsite":
            self.displayImage = self.campsiteImage

        #self.draw()

    def draw(self):
        self.screen.blit(self.displayImage,(246,153))
        self.screen.blit(self.frameImage,(227,135))
          


class MileDisplay:
    def __init__(self,screen, player):
        self.screen = screen
        self.player = player
        self.bootprint= pg.transform.scale(pg.image.load(resource_path('images/bootprint.png')),(100, 42))
        self.green=(0,180,0)
        self.font = pg.font.SysFont("franklingothicheavy",22)

    def update(self):
        pass

    def draw(self):
        pg.draw.rect(self.screen, (2, 20, 7),(227, 60, 430, 45))
        self.screen.blit(self.bootprint,(245,61))

        
        round_rect(self.screen, (365,68,275,30), pg.Color("black"), 3,
                        1, (220, 220, 220))

        round_rect(self.screen, (366,69,round(self.player.mile *0.125, 1),28), self.green, 3,
                        1, (self.green))

        text = self.font.render(str(round(self.player.mile, 1)) + " / 2193.0", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.center = (500, 83) 

        self.screen.blit(text, text_rect)

        pg.draw.rect(self.screen, (44, 18, 23),(227, 105, 430, 30))

        text = self.font.render("Today's Miles: " + str(round(self.player.today_miles, 1)),
                                True, pg.Color("white"))
        
        text_rect = text.get_rect()
        text_rect.center = (442, 119)
        
        self.screen.blit(text, text_rect)

        

        
        


class DateDisplay:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.current_date = date.datetime(self.player.year,
                                    self.player.current_month,
                                    self.player.current_day)

    def update(self):
        self.current_date = date.datetime(self.player.year,
                                    self.player.current_month,
                                    self.player.current_day)
               
        new_date = self.current_date + date.timedelta(days=1)

        self.current_date = new_date
        
        self.player.current_month = self.current_date.month
        self.player.current_day = self.current_date.day

        #print(self.player.current_month)
        #print(self.player.current_day)

    def draw(self):
        pg.draw.rect(self.screen, (0, 0, 25),(0, 0, 227, 80))
        
        day_of_week = self.current_date.strftime("%A")
        month = self.current_date.strftime("%B")
        day = self.current_date.strftime("%d")

        week_day = drop_shadow_text(day_of_week + ",",
             "franklingothicheavy", 28, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(week_day, center_of_surface(week_day, 113, 25)) 

        title = drop_shadow_text(month + " " + day,
             "franklingothicheavy", 28, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title, center_of_surface(title, 113, 55))     


class DisplayMap:
    def __init__(self, screen):
        self.done = True
        self.screen = screen
        self.map =  pg.transform.scale(pg.image.load(resource_path('images/at_map.png')),
                                               (228, 592))
        self.map_arrow = pg.transform.scale(pg.image.load(resource_path("images/arrow.png")),
                                               (68, 40))


    def draw(self):
        if not self.done:
            self.screen.blit(self.map,(570,4))


class DisplayEat:
    def __init__(self, screen, player):
        self.done = True
        self.screen = screen
        self.player = player
        self.font = pg.font.SysFont("impact", 18)
       

    def draw(self):
       
        if not self.done:
            pg.draw.rect(self.screen, (255, 255, 255),(657, 405, 140, 195))
            pg.draw.rect(self.screen, (0,0,0),(657, 405, 140, 195),2)

            text = self.font.render("Options", True, pg.Color("black"))
            text_rect = text.get_rect()
            text_rect.center = (727, 420) 

            self.screen.blit(text, text_rect)



class Sign:
    def __init__(self, screen,player, next_resupply, next_water, next_camping):
        self.screen = screen
        self.player = player
        self.sign_rect = pg.Rect(556, 404, 234, 190)
        self.font = pg.font.SysFont("franklingothicheavy",17)
        self.sign= pg.transform.scale(pg.image.load(resource_path('images/sign2.png')),(220, 135))
        self.brown = (92, 65, 48)
        self.dark_brown = (61, 45, 34)
        self.next_resupply = next_resupply
        self.next_water = next_water
        self.next_camping = next_camping
        self.outline = (23, 17, 13)

    def draw(self):
        water = self.next_water.miles_to_next
        camping = self.next_camping.miles_to_next
        resupply = self.next_resupply.miles_to_next

        pg.draw.rect(self.screen, (30, 30, 30),(0, 405, 227, 155))
        pg.draw.rect(self.screen, (4, 48, 16),(0, 540, 227, 60))
        self.screen.blit(self.sign, (5,405))


        text = self.font.render("APPALACHIAN TRAIL", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.center = (116, 436) 

        self.screen.blit(text, text_rect)

        text = self.font.render("APPALACHIAN TRAIL", True, pg.Color("white"))
        text_rect = text.get_rect()
        text_rect.center = (115, 435) 

        self.screen.blit(text, text_rect)

        text = self.font.render("Next Water", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.topleft = (31, 456) 

        self.screen.blit(text, text_rect)


        text = self.font.render("Next Water", True, pg.Color("white"))
        text_rect = text.get_rect()
        text_rect.topleft = (30, 455) 

        self.screen.blit(text, text_rect)



        text = self.font.render(str(water), True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.topright = (201, 456) 

        self.screen.blit(text, text_rect)

        text = self.font.render(str(water), True, pg.Color("white"))
        text_rect = text.get_rect()
        text_rect.topright = (200, 455) 

        self.screen.blit(text, text_rect)


        text = self.font.render("Next Camping", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.topleft = (31, 481) 

        self.screen.blit(text, text_rect)


        text = self.font.render(str(camping), True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.topright = (201, 481) 

        self.screen.blit(text, text_rect)
        

        text = self.font.render("Next Camping", True, pg.Color("white"))
        text_rect = text.get_rect()
        text_rect.topleft = (30, 480) 

        self.screen.blit(text, text_rect)


        text = self.font.render(str(camping), True, pg.Color("white"))
        text_rect = text.get_rect()
        text_rect.topright = (200, 480) 

        self.screen.blit(text, text_rect)

        text = self.font.render("Next Resupply", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.topleft = (31, 506) 

        self.screen.blit(text, text_rect)


        text = self.font.render(str(resupply), True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.topright = (201, 506) 

        self.screen.blit(text, text_rect)


        

        text = self.font.render("Next Resupply", True, pg.Color("white"))
        text_rect = text.get_rect()
        text_rect.topleft = (30, 505) 

        self.screen.blit(text, text_rect)


        text = self.font.render(str(resupply), True, pg.Color("white"))
        text_rect = text.get_rect()
        text_rect.topright = (200, 505) 

        self.screen.blit(text, text_rect)


class Hiker(pg.sprite.Sprite):
    def __init__(self):
        super(Hiker, self).__init__()
        
        self.walk_1 = pg.transform.scale(pg.image.load(resource_path('images/walk/walk_1.png')),(80, 80))
        self.walk_2 = pg.transform.scale(pg.image.load(resource_path('images/walk/walk_2.png')),(80, 80))
        self.walk_3 = pg.transform.scale(pg.image.load(resource_path('images/walk/walk_3.png')),(80, 80))
        self.walk_4 = pg.transform.scale(pg.image.load(resource_path('images/walk/walk_4.png')),(80, 80))
        self.walk_5 = pg.transform.scale(pg.image.load(resource_path('images/walk/walk_5.png')),(80, 80))
        self.walk_6 = pg.transform.scale(pg.image.load(resource_path('images/walk/walk_6.png')),(80, 80))
        self.walk_7 = pg.transform.scale(pg.image.load(resource_path('images/walk/walk_7.png')),(80, 80))
        self.walk_8 = pg.transform.scale(pg.image.load(resource_path('images/walk/walk_8.png')),(80, 80))
        self.images = [self.walk_1,self.walk_1,self.walk_2,self.walk_2,self.walk_3,self.walk_3,self.walk_4,
                       self.walk_4,self.walk_5,self.walk_5,self.walk_6,self.walk_6,self.walk_7,self.walk_7,
                       self.walk_8,self.walk_8]
        
        self.index = 0

        self.image = self.images[self.index]
        self.rect = pg.Rect(250, 510, 80, 80)


    def update(self):
         
        self.index += 1

        if self.index >= len(self.images):
            self.index = 0
        
        self.image = self.images[self.index]


class StatusBar :

    def __init__(self, screen, player):
        
        self.done = False
        self.clock = pg.time.Clock()
        self.screen = screen
        self.player = player
        
        self.green=(0,180,0)
        self.red = (212, 0, 0)
        self.yellow = (236, 222, 0)
        self.fund_color = self.green
        self.water_color = self.green
        self.energy_color = self.green
        self.health_color = self.green
        self.weight_color = self.green
        self.food_color = self.green
        
        self.cash = self.player.hiker_funds.calculate_available()
        self.water =self.player.liters
        self.energy =self.player.player_stats.energy *1.6
        self.health = self.player.player_stats.health *1.6
        self.font = pg.font.SysFont("franklingothicheavy",18)
        

    def update(self, player):

        
        self.cash = self.player.hiker_funds.calculate_available()
        self.water =self.player.liters
        self.energy =self.player.player_stats.energy *1.6
        self.health = self.player.player_stats.health  *1.6



        if self.player.hiker_funds.calculate_available() <= 500:
            self.fund_color = self.red
        elif self.player.hiker_funds.calculate_available() >500\
             and self.player.hiker_funds.calculate_available() <=1500:
            self.fund_color = self.yellow
        else:
            self.fund_color = self.green


        if self.player.calculate_Packweight() >= 35:
            self.weight_color = self.red
        elif self.player.calculate_Packweight() < 35 and self.player.calculate_Packweight()> 30 :
            self.weight_color = self.yellow
        else:
            self.weight_color = self.green


        if self.player.liters < .75:
            self.water_color = self.red
        elif self.player.liters >= .75 and self.player.liters <=1.5:
            self.water_color = self.yellow
        elif self.player.liters > 1.5:
            self.water_color = self.green

        
        
        if self.player.player_stats.energy >= 50:
            self.energy_color = self.green
        elif self.player.player_stats.energy < 50 and self.player.player_stats.energy >=25:
            self.energy_color = self.yellow
        elif self.player.player_stats.energy < 25:
            self.energy_color = self.red

        if self.player.player_stats.health  >= 50:
            self.health_color = self.green
        elif self.player.player_stats.health  < 50 and self.player.player_stats.health  >=25:
            self.health_color = self.yellow
        elif self.player.player_stats.health  < 25:
            self.health_color = self.red


        
        self.energy =self.player.player_stats.energy *1.6
        self.health = self.player.player_stats.health  *1.6

        self.draw()
        

    def draw(self):
        pg.draw.rect(self.screen, (50, 38, 38),(0, 80, 227, 166))
        pg.draw.rect(self.screen,(80, 80, 80), (0, 243, 227, 162))
        

##        title = drop_shadow_text("Status",
##             "franklingothicheavy", 22, pg.Color("black"), pg.Color("white"),0, 0, 1)
##
##        self.screen.blit(title, center_of_surface(title, 113, 75))

        title = drop_shadow_text("Supplies",
             "franklingothicheavy", 22, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title, center_of_surface(title, 113, 258))

        

        self.screen.blit(CASH_IMAGE, (10, 85))
        self.screen.blit(ENERGY_IMAGE, (10, 125))
        self.screen.blit(HEALTH_IMAGE, (10, 162))
        self.screen.blit(WEIGHT_IMAGE, (10,202))

        
        self.screen.blit(WATER_IMAGE, (10, 270))
        self.screen.blit(FOOD_IMAGE, (10, 332))
        


        round_rect(self.screen, (50,90,160,25), pg.Color("black"), 3,
                        1, (self.fund_color))

        round_rect(self.screen, (50,210,160,25), pg.Color("black"), 3,
                        1, (self.weight_color))

        round_rect(self.screen, (50,275,160,25), pg.Color("black"), 3,
                        1, (self.water_color))

        round_rect(self.screen, (50,308,160,90), pg.Color("black"), 2,
                        1, (pg.Color("white")))


        



        round_rect(self.screen, (50,130,160,25), pg.Color("black"), 3,
                        1, (220, 220, 220))

        round_rect(self.screen, (50,170,160,25), pg.Color("black"), 3,
                        1, (220, 220, 220))


        round_rect(self.screen, (50,130,self.energy,25), pg.Color("black"), 3,
                        1, self.energy_color)

        round_rect(self.screen, (50,170,self.health,25), pg.Color("black"), 3,
                        1, self.health_color)


        text = self.font.render("$ " + format(self.player.hiker_funds.calculate_available(),'.2f'), True, pg.Color("black"))
##        text = self.font.render("$ " + str(int(self.player.hiker_funds.calculate_available())), True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.center = (130, 102) 

        self.screen.blit(text, text_rect)

        

        text = self.font.render(str(int(self.player.player_stats.energy))+ " %", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.center = (130, 141) 

        self.screen.blit(text, text_rect)

        text = self.font.render(str(self.player.player_stats.health)+ " %", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.center = (130, 181) 

        self.screen.blit(text, text_rect)

        text = self.font.render(str(round(self.player.calculate_Packweight(), 1))+ " LBS", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.center = (130, 221) 

        self.screen.blit(text, text_rect)

        text = self.font.render(str(round(self.player.liters, 1))+ " L", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.center = (130, 286) 

        self.screen.blit(text, text_rect)

        

        text = self.font.render("Breakfasts", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.bottomleft = (70, 333) 

        self.screen.blit(text, text_rect)

        text = self.font.render(str(self.player.breakfast), True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.bottomright = (190, 333) 

        self.screen.blit(text, text_rect)


        text = self.font.render("Lunches", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.bottomleft = (70, 353) 

        self.screen.blit(text, text_rect)

        text = self.font.render(str(self.player.lunch), True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.bottomright = (190, 353) 

        self.screen.blit(text, text_rect)

        text = self.font.render("Dinners", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.bottomleft = (70, 373) 

        self.screen.blit(text, text_rect)

        text = self.font.render(str(self.player.dinner), True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.bottomright = (190, 373) 

        self.screen.blit(text, text_rect)

        text = self.font.render("Snacks", True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.bottomleft = (70, 393) 

        self.screen.blit(text, text_rect)

        text = self.font.render(str(self.player.snacks), True, pg.Color("black"))
        text_rect = text.get_rect()
        text_rect.bottomright = (190, 393) 

        self.screen.blit(text, text_rect)



class Alert:

    def __init__(self, screen, message, status):
        self.done = False
        self.screen = screen
        self.showing = status
        self.message = message
        self.box = pg.Rect(150, 150, 500, 300)

        self.ok = Button(
            350, 375, 100, 50, self.ok,
            pg.font.SysFont("franklingothicmedium",20),
            'OK', pg.Color("white"))

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.alert_sprites = pg.sprite.Group()

    def ok(self):
        self.alert_sprites.empty()
        self.showing = False
        self.done = True

    def run(self):
        while not self.done:
            
            self.dt = self.clock.tick(60)
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():            
            for button in self.alert_sprites:
                button.handle_event(event)

    def run_logic(self):
        self.alert_sprites.update(self.dt)
        

    def draw(self, display):
        if self.showing:
               
        
            pg.draw.rect(display, pg.Color("lightgray"), self.box)
            pg.draw.rect(display, pg.Color("black"), (150, 150, 500, 300),3)
            pg.draw.rect(display, pg.Color("darkgray"), (153, 153, 494, 294),3)

            label = pg.font.SysFont("impact", 22)
            x = 400
            y = 225
            

            for e in self.message:

                TextSurf, TextRect = text_objects(e, label, pg.Color("black"))
                TextRect.center = (x, y)
                display.blit(TextSurf, TextRect)
                y+=35
                
           

        
            self.alert_sprites.add(self.ok)
            self.alert_sprites.draw(self.screen)




class MealsWaterSpinner:

    def __init__(self, visible, screen, hiker_funds, player, available,weight, x, y, width,
                 title = "", button_visible = True, font_size_title = 0,
                 top_color = "green", box_color = "white",
                 font_color = "black", font = "impact"):
        self.done = False
        self.screen = screen
        self.hiker_funds = hiker_funds
        self.player = player
        self.visible = visible
        self.available = available
        self.weight = weight
        self.x = x
        self.y = y
        self.w = width
        self.h = 225
        self.font_size = 30
        self.title = title

        
        self.buttons = button_visible
        
        self.button_w = 25
        self.button_h = 45

        self.top_color = top_color
        self.box_color = box_color
        self.font_color = font_color
        self.font = font
        
        self.waypoint_object = Waypoint(self.player.current_waypoint)
        
        self.guide_book = GuideBook(self.screen, self.waypoint_object, self.player.current_waypoint)
        self.current_resupply = Resupply_Options('0')

        
        # Scale the images to the desired size (doesn't modify the originals).
        self.right_normal = pg.transform.scale(RIGHT_NORMAL,(self.button_w, self.button_h))
        self.right_hover = pg.transform.scale(RIGHT_HOVER,(self.button_w, self.button_h))
        self.right_down = pg.transform.scale(RIGHT_DOWN,(self.button_w, self.button_h))

      
        # Scale the images to the desired size (doesn't modify the originals).
        self.left_normal = pg.transform.scale(LEFT_NORMAL,(self.button_w, self.button_h))
        self.left_hover = pg.transform.scale(LEFT_HOVER,(self.button_w, self.button_h))
        self.left_down = pg.transform.scale(LEFT_DOWN,(self.button_w, self.button_h))

        self.guidebook_btn = Button(
            497, 185, 180, 45, self.show_guide,
            pg.font.SysFont("franklingothicheavy",22),
            'Guidebook', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.buy_food_btn = Button(
            497, 240, 180, 45, self.buy_food,
            pg.font.SysFont("franklingothicheavy",22),
            'Buy Food', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.waterUP = Button(
            677, 297, self.button_w, self.button_h, self.increment_water,
            pg.font.SysFont("franklingothicmedium",35), '',
            pg.Color("black"), self.right_normal, self.right_hover, self.right_down)

        self.waterDOWN = Button(
            475, 297, self.button_w, self.button_h, self.decrement_water,
            pg.font.SysFont("franklingothicmedium",35), '', pg.Color("black"),
            self.left_normal, self.left_hover, self.left_down)

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.consumables_sprites = pg.sprite.Group()

    def show_guide(self):
        self.guide_book =  GuideBook(self.screen, self.waypoint_object,
                                     self.player.current_waypoint)
        self.guide_book.done = False
        self.guide_book.run()

    def buy_food(self):
##        self.player.balance = self.hiker_funds.calculate_available()
        self.food_store = Food_Store(self.screen, self.player, self.hiker_funds, self.current_resupply)
        self.food_store.done = False
        self.food_store.run()

        

    def increment_water(self):
        
        
        if self.player.liters < 4.0:
            self.player.liters += .5
            
            self.weight.add_to_display(self.screen)
        

    def decrement_water(self):
        
        
        if self.player.liters > 0.5:
            self.player.liters -= 0.5


    def run(self):
        while not self.done:
            
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            for button in self.consumables_sprites:
                button.handle_event(event)

    def run_logic(self):
        self.consumables_sprites.update(self.dt)
        

    def draw(self, display):
        if self.visible:
            self.consumables_sprites.add(self.guidebook_btn, self.buy_food_btn,
                                         self.waterUP, self.waterDOWN)
            pg.draw.rect(display, pg.Color("white"), (self.x, self.y, self.w, self.h))
            green = pg.transform.scale(BROWNISH,(self.w, 45))
            display.blit(green,(self.x,self.y))
            pg.draw.rect(display, pg.Color("black"), (self.x, self.y, self.w, self.h), 2)
            pg.draw.rect(display, pg.Color("black"),(self.x, self.y, self.w, 45), 2)
            label = pg.font.SysFont("impact", 30)
            TextSurf, TextRect = text_objects("Supplies", label, pg.Color("black"))
            TextRect.center = (589, 152)
            display.blit(TextSurf, TextRect)
            
            largelabel = pg.font.SysFont("impact", 32)
            TextSurf, TextRect = text_objects(format(self.player.liters, ',.1f') + " L of H\u20820", largelabel,
                                              pg.Color("black"))
            TextRect.center = (590, 320)
            display.blit(TextSurf, TextRect)

            if self.buttons:
                self.consumables_sprites.draw(self.screen)



class PackWeight:
    def __init__(self, visible, screen, player):
        self.screen = screen
        self.player = player
        self.visible = visible

    def add_to_display(self, display):
        if self.visible:


            pg.draw.rect(self.screen, pg.Color("white"), (50, 375,
                                                          350, 100))

            pg.draw.rect(self.screen, pg.Color("black"), (50, 375,
                                                          350, 100), 2)

            texture  = pg.transform.scale(CLOUD,(350,45))
            self.screen.blit(texture,(50,375))

            

            pg.draw.rect(self.screen, pg.Color("black"), (50, 375,
                                                          350, 45), 2)

            label = pg.font.SysFont("impact", 30)
            TextSurf, TextRect = text_objects("Pack Weight", label, pg.Color("black"))
            TextRect.center = (225, 397)
            display.blit(TextSurf, TextRect)

    ##        print("Here In PackWeight")
            amount_label = pg.font.SysFont("impact", 40)
            TextSurf, TextRect = text_objects(format(self.player.calculate_Packweight(), '.1f') + " LBS",
                                              amount_label, pg.Color("black"))
            TextRect.center = (225, 445)
            display.blit(TextSurf, TextRect)




class AvailableFunds:
    def __init__(self, visible, screen, hiker_funds):
        self.screen = screen
        self.hiker_funds = hiker_funds
        self.visible = visible

        


    def add_to_display(self, display):
        if self.visible:
            pg.draw.rect(self.screen, pg.Color("white"), (425, 375,
                                                          325, 100))

            pg.draw.rect(self.screen, pg.Color("black"), (425, 375,
                                                          325, 100), 2)

            texture  = pg.transform.scale(GREEN,(325,45))
            self.screen.blit(texture,(425,375))

            

            pg.draw.rect(self.screen, pg.Color("black"), (425, 375,
                                                          325, 45), 2)

            label = pg.font.SysFont("impact", 30)
            TextSurf, TextRect = text_objects("Available Balance", label, pg.Color("black"))
            TextRect.center = (595, 396)
            display.blit(TextSurf, TextRect)
  
            amount_label = pg.font.SysFont("impact", 40)
            TextSurf, TextRect = text_objects("$ " + str(format(self.hiker_funds.calculate_available(), '.2f')),
                                              amount_label, pg.Color("black"))
            TextRect.center = (595, 445)
            display.blit(TextSurf, TextRect)

##            print("Balance In Available Funds", self.player.balance)
##
##            print("HIking Funds In Available Funds", self.player.hiking_funds)

        
        
        
        
        














# Button is a sprite subclass, that means it can be added to a sprite group.
# You can draw and update all sprites in a group by
# calling `group.update()` and `group.draw(screen)`.

class Button(pg.sprite.Sprite):

    def __init__(self, x, y, width, height, callback,
                 font=FONT, text='', text_color=(0, 0, 0),
                 image_normal=IMAGE_NORMAL, image_hover=IMAGE_HOVER,
                 image_down=IMAGE_DOWN, fontName="georgia", fontSize=20,
                 shadowColor = pg.Color("black"), topColor = pg.Color("white"),
                 offset = 1):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.text = text
        self.text_color = text_color
        self.fontName = fontName
        self.fontSize = fontSize
        self.shadowColor = shadowColor
        self.topColor = topColor
        self.offset = offset
        
        # Scale the images to the desired size (doesn't modify the originals).
        self.image_normal = pg.transform.scale(image_normal, (self.width, self.height))
        self.image_hover = pg.transform.scale(image_hover, (self.width, self.height))
        self.image_down = pg.transform.scale(image_down, (self.width, self.height))

        self.image = self.image_normal  # The currently active image.
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        # To center the text rect.
        self.image_center = self.image.get_rect().center
        self.shadow_center = self.image.get_rect().center
        self.center_offX, self.center_offY = center_of_surface(self.image, self.width+1, self.height)
        self.shadow_center = self.center_offX, self.center_offY
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.image_center)
        self.rectSC = self.image.get_rect(topleft = (self.x,self.y))
        text_surfS = self.font.render(self.text, True, self.shadowColor)
        text_rectS = text_surfS.get_rect(center=self.shadow_center)

        
        # Blit the text onto the images.
        for image in (self.image_normal, self.image_hover, self.image_down):
            image.blit(text_surfS, text_rectS)
            image.blit(text_surf, text_rect)

        # This function will be called when the button gets pressed.
        self.callback = callback
        self.button_down = False
        

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.image = self.image_down
                self.button_down = True
        elif event.type == pg.MOUSEBUTTONUP:
            # If the rect collides with the mouse pos.
            if self.rect.collidepoint(event.pos) and self.button_down:
                self.callback()  # Call the function.
                self.image = self.image_hover
            self.button_down = False
        elif event.type == pg.MOUSEMOTION:
            collided = self.rect.collidepoint(event.pos)
            if collided and not self.button_down:
                self.image = self.image_hover
            elif not collided:
                self.image = self.image_normal




class Menu:

    def __init__(self, screen, player):
        
        self.done = False
        self.clock = pg.time.Clock()
        self.screen = screen
        self.player = player        

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.menu_sprites = pg.sprite.Group()
        self.background  = pg.transform.scale(pg.image.load(resource_path('images/intro.jpg')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))


        # Buttons
        self.new_game = Button(
            606, 500, 170, 50, self.play_game,
            pg.font.SysFont("franklingothicheavy",22),
            'New Game', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.saved_game = Button(
            412, 500, 170, 50, self.get_saved_player,
            pg.font.SysFont("franklingothicheavy",22),
            'Saved Game', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.tutorial = Button(
            218, 500, 170, 50, self.display_intro,
            pg.font.SysFont("franklingothicheavy",22),
            'Game Tutorial', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.quit_button = Button(
            24, 500, 170, 50, self.quit_game,
            pg.font.SysFont("franklingothicheavy",22),
            'Exit', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        # Add the button sprites to the sprite group.
        self.menu_sprites.add(self.new_game, self.tutorial, self.saved_game, self.quit_button)
        self.game_state = GameState.MENU

    def play_game(self):
        self.done = True
        self.game_state = GameState.PLAYERMENU
        

    def display_intro(self):
        self.done = True
        self.game_state = GameState.WELCOME

    def get_saved_player(self):
        picklefile = open('player_object', 'rb')
        #unpickle the dataframe
        self.player = pickle.load(picklefile)
        #close file
        picklefile.close()

        #print the dataframe
        print(type(self.player))
        print(self.player.name)
        self.done = True
        self.game_state = GameState.PLAYGAME    

    def quit_game(self):
        self.done = True
        self.game_state = GameState.QUIT

    def run(self):
        while not self.done:
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                self.done = True
                self.game_state = GameState.QUIT
                
            for button in self.menu_sprites:
                button.handle_event(event)

    def run_logic(self):
        self.menu_sprites.update(self.dt)

    def draw(self):
        
        self.screen.blit(self.background,(0,0))

        title1 = drop_shadow_text("Appalachian Trail",
             "impact", 70, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title1, center_of_surface(title1, 495, 200))

        title2 = drop_shadow_text("Thru Hike",
             "impact", 50, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title2, center_of_surface(title2, 495, 350))

        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)

        self.menu_sprites.draw(self.screen)
        cursor_AT(self.screen, True)
        pg.display.flip()

    def current_state(self):
        return self.game_state


class InputText():
    def __init__(self, visible, display, player, x, y, w, h, pgIC, pgAC, fontName, fontSize):
        self.screen = display
        self.player = player
        self.visible = visible

        self.error = ""
        self.font = pg.font.SysFont(fontName, fontSize)
##        self.text = ''
        self.text_length = 0
##        self.max_length = 12
        self.inactiveColor = pg.Color(pgIC)
        self.activeColor =pg.Color(pgAC) 
        self.color = self.inactiveColor
        self.textColor = pg.Color("black")
        self.textSurface = self.font.render(str(self.player.name) , True, self.activeColor)
        self.width_text = self.textSurface.get_width()
        self.inputBox = pg.Rect(x, y, w, h)
        self.active = False
 
    def event_handler(self, event):
        if self.visible:            
            if event.type == pg.MOUSEBUTTONDOWN:
                self.active = self.inputBox.collidepoint(event.pos)     
                self.color = self.activeColor if self.active else self.inactiveColor
            if event.type == pg.KEYDOWN:
                if self.active:
                    if event.key == pg.K_RETURN or event.key == pg.K_TAB:
                        self.active = False
                    elif event.key == pg.K_BACKSPACE:
                        self.player.name = self.player.name[:-1]
                        if self.text_length > 0:
                            self.text_length -= 1
                    else:
                        if self.width_text < 168:
                            self.player.name += event.unicode
                            self.text_length += 1
                        else:
                            self.error = "Too Long"

    def add_to_display(self, display):

        
        if self.visible:     
        
            pg.draw.rect(display, pg.Color("white"), (self.inputBox.x+2,
                                                      self.inputBox.y+2,
                                                      self.inputBox.w-4,
                                                      self.inputBox.h-4))
            self.textSurface = self.font.render(self.player.name , True, self.textColor)
            self.width_text = self.textSurface.get_width()
            display.blit(self.textSurface, (self.inputBox.x+10, self.inputBox.y+5))
            pg.draw.rect(display, self.color, self.inputBox, 2)


     


class Welcome:
    def __init__(self, screen):
        self.done = False       
        self.clock = pg.time.Clock()
        self.screen = screen
        self.count = 0
        self.page1 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/page1.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page2 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/page2.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page3 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/buyfood1.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page6 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/guide.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page5 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/mailFood.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page4 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/buyfood2.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page7 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/display1.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page8 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/display2.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))        
        self.page9 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/waypoint.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        
        self.page10 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/random.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page11 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/town.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page12 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/intown.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page13 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/gear.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.page14 = pg.transform.scale(pg.image.load(resource_path('images/tutorial/gameover.png')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
         
        

        self.list = [self.page1, self.page2, self.page3, self.page4, self.page5,
                     self.page6, self.page7, self.page8, self.page9, self.page10,
                     self.page11, self.page12, self.page13, self.page14]

        self.display_screen = "Welcome"

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.info_sprites = pg.sprite.Group()

        

        # Create the button instances. You can pass your own images here.
        self.ok = Button(
            550, 520, 200, 50, self.input_new_player,
            pg.font.SysFont("franklingothicheavy",24),
            'OK', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.next = Button(
            550, 520, 200, 50, self.next,
            pg.font.SysFont("franklingothicheavy",24),
            'Next', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.pages = Button(
            550, 520, 200, 50, self.pages,
            pg.font.SysFont("franklingothicheavy",24),
            'Next', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.cancel = Button(
            300, 520, 200, 50, self.cancel,
            pg.font.SysFont("franklingothicheavy",24),
            'Cancel', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.quit_button = Button(
            50, 520, 200, 50, self.quit_game,
            pg.font.SysFont("franklingothicheavy",24),
            'Exit', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        # Add the button sprites to the sprite group.
        self.info_sprites.add(self.next, self.cancel, self.quit_button)
        self.game_state = GameState.WELCOME

    def next(self):
        self.display_screen = "Pages"
        self.info_sprites.remove(self.next)
        self.info_sprites.add(self.pages)
        

    def pages(self):
        if self.count < len(self.list)-1:
            self.count += 1
        if self.count == 13:
            self.info_sprites.remove(self.next)
            self.info_sprites.add(self.ok)
        
        
        
        
        

    def input_new_player(self):
        self.done = True
        self.game_state = GameState.MENU

    def cancel(self):
        self.done = True
        self.game_state = GameState.MENU        

    def quit_game(self):
        self.done = True
        self.game_state = GameState.QUIT

    def run(self):        
        while not self.done:
            
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                self.game_state = GameState.QUIT
                
            for button in self.info_sprites:
                button.handle_event(event)

    def run_logic(self):
        self.info_sprites.update(self.dt)

    def draw(self):
        print(self.count)
        self.screen.fill(pg.Color("gray10"))
        

        blaze = pg.transform.scale(BLAZE, (25, 75))

        if self.display_screen == "Welcome":      
            text1 = "You’re about to begin a great adventure."
            line1 = drop_shadow_text(text1, "georgia", 19, pg.Color("black"), pg.Color("white"),0, 0, 1)
            text2 = "The Appalachian Trail is a 2,193 mile long footpath in the eastern United States"
            line2 = drop_shadow_text(text2, "georgia", 19, pg.Color("black"), pg.Color("white"),0, 0, 1)            
            text3 = "extending between Springer Mountain in Georgia and Mount Katahdin in Maine."
            text4 = "A thru-hiker is a person who attempts to hike the entire trail in a single season"
            text5 = "carrying only a backpack and supplies.  A thru-hiker must make stops along the"
            text6 = "way in towns to replenish supplies and allow the body to recover."
            text7 = "During the journey, you will face obstacles such as weather, wildlife, injury,"
            text8 = "sickness, and many others. You must reach Mount Katahdin before October 15 "
            text9 = "when Mount Katahdin closes for the year."
            text10 = "Before you set off, you must choose a trail name, starting gear, starting date,"
            text11 = "walking speed, and funds available to complete the trail. "            
            text12 = "Happy Hiking !!"  

            line2 = drop_shadow_text(text2, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)
            
            line3 = drop_shadow_text(text3, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            line4 = drop_shadow_text(text4, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            line5 = drop_shadow_text(text5, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            line6 = drop_shadow_text(text6, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            line7 = drop_shadow_text(text7, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            line8 = drop_shadow_text(text8, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            line9 = drop_shadow_text(text9, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            line10 = drop_shadow_text(text10, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            line11 = drop_shadow_text(text11, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            line12 = drop_shadow_text(text12, "georgia",
                19, pg.Color("black"), pg.Color("white"),0, 0, 1)

            self.screen.blit(line2,(55,125))
            self.screen.blit(line3,(55,150))            
            self.screen.blit(line4,(55,200))
            self.screen.blit(line5,(55,225))
            self.screen.blit(line6,(55,250))            
            self.screen.blit(line7,(55,300))
            self.screen.blit(line8,(55,325))
            self.screen.blit(line9,(55,350))            
            self.screen.blit(line10,(55,400))
            self.screen.blit(line11,(55,425))            
            self.screen.blit(line12,(55,475))

            title = drop_shadow_text("Welcome to the Appalachian Trail !",
             "georgia", 38, pg.Color("black"), pg.Color("white"),400, 50, 2)
            self.screen.blit(title, center_of_surface(title, 400, 65))
            

        if self.display_screen == "Pages":
            self.screen.blit(self.list[self.count],(0,0))
            TextSurf, TextRect = text_objects("Game Play Tutorial", pg.font.SysFont("impact", 50), pg.Color("black"))
            TextRect.center = (400, 70)
            self.screen.blit(TextSurf, TextRect)
            
            

        
        self.screen.blit(blaze, (50,28))
        self.screen.blit(blaze, (725,28))    
        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)
        self.info_sprites.draw(self.screen)
        cursor_AT(self.screen, True)
        pg.display.flip()

    def current_state(self):
        return self.game_state



   
        

        
class DateSpinner:

    def __init__(self, visible, screen, player,x, y, width, weatherDisplay, button_visible = True,
                 month=3, day=15, top_color = "red",
                 day_color = "white", font_color = "black", font = "impact"):
        self.done = False
        self.visible = visible
        self.screen = screen
        self.player = player
        self.x = x
        self.y = y
        self.w = width
        self.h = width * .75
        self.font_size = int(self.h *.19)

        self.month_name = month_names(self.player.start_month)
        
        self.buttons = button_visible
        
        self.button_w = int(self.w/6)
        self.button_h = int(self.w * 0.25)

        self.top_color = top_color
        self.day_color = day_color
        self.font_color = font_color
        self.font = font
        self.weatherDisplay = weatherDisplay

        # Scale the images to the desired size (doesn't modify the originals).
        self.right_normal = pg.transform.scale(RIGHT_NORMAL,(self.button_w, self.button_h))
        self.right_hover = pg.transform.scale(RIGHT_HOVER,(self.button_w, self.button_h))
        self.right_down = pg.transform.scale(RIGHT_DOWN,(self.button_w, self.button_h))

      
        # Scale the images to the desired size (doesn't modify the originals).
        self.left_normal = pg.transform.scale(LEFT_NORMAL,(self.button_w, self.button_h))
        self.left_hover = pg.transform.scale(LEFT_HOVER,(self.button_w, self.button_h))
        self.left_down = pg.transform.scale(LEFT_DOWN,(self.button_w, self.button_h))

        
        
        self.monthUP = Button(
            self.x + self.w - self.button_w, self.y, self.button_w, self.button_h, self.increment_month,
            pg.font.SysFont("franklingothicmedium",35), '',
            pg.Color("black"), self.right_normal, self.right_hover, self.right_down)

        self.monthDOWN = Button(
            self.x, self.y, self.button_w, self.button_h, self.decrement_month,
            pg.font.SysFont("franklingothicmedium",35), '', pg.Color("black"),
            self.left_normal, self.left_hover, self.left_down)

        self.dayUP = Button(
            self.x + self.w - self.button_w, self.y+self.w/3, self.button_w,
            self.button_h+10, self.increment_day,
            pg.font.SysFont("franklingothicmedium",35), '',
            pg.Color("black"), self.right_normal, self.right_hover, self.right_down)

        self.dayDOWN = Button(
            self.x, self.y+self.w/3, self.button_w, self.button_h+10,
            self.decrement_day,
            pg.font.SysFont("franklingothicmedium",35), '', pg.Color("black"),
            self.left_normal, self.left_hover, self.left_down)

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.

        
        self.date_sprites = pg.sprite.Group()

        

    def increment_month(self):
        
        """Callback method to increment the number."""        
        if self.player.start_month >= 2 and self.player.start_month <= 5:
            self.player.start_month += 1
            self.month_name = month_names(self.player.start_month)
            
        if self.player.start_month > 5:
            self.player.start_month = 2
            self.month_name = month_names(self.player.start_month)

        self.player.current_month = self.player.start_month
        self.weatherDisplay.add_to_display(self.screen, self.player)


        

    def decrement_month(self):
        
        if self.player.start_month <= 5 and self.player.start_month >=2:
            self.player.start_month -= 1
            self.month_name = month_names(self.player.start_month)        
        if self.player.start_month ==1:
            self.player.start_month = 5
            self.month_name = month_names(self.player.start_month)
            
        self.player.current_month = self.player.start_month    
        
        self.weatherDisplay.add_to_display(self.screen, self.player)


    def increment_day(self):
        

       
        """Callback method to increment the number."""
        if self.player.start_month == 5:
            if self.player.start_day == 1:
                self.player.start_day += 14
            elif self.player.start_day == 15:
                self.player.start_day = 1
                self.player.start_month = 2
                self.month_name = month_names(self.player.start_month)
        
                
        elif self.player.start_month >= 2 and self.player.start_month<= 5:
            if self.player.start_day == 1:
                self.player.start_day += 14
            elif self.player.start_day == 15:
                self.player.start_day = 1
                self.player.start_month += 1
                self.month_name = month_names(self.player.start_month)

        self.player.current_month = self.player.start_month
        self.player.current_day = self.player.start_day
        self.weatherDisplay.add_to_display(self.screen, self.player)

  

    def decrement_day(self):
        
        
        """Callback method to increment the number."""
        if self.player.start_month == 2:
            if self.player.start_day == 1:
                self.player.start_day = 15
                self.player.start_month = 5
                self.month_name = month_names(self.player.start_month)
            elif self.player.start_day ==15:
                self.player.start_day = 1

        elif self.player.start_month >= 2 and self.player.start_month <=5:
            if self.player.start_day == 1:
                self.player.start_day = 15
                self.player.start_month -= 1
                self.month_name = month_names(self.player.start_month)
                
            elif self.player.start_day == 15:
                self.player.start_day = 1

                
        self.player.current_month = self.player.start_month
        self.player.current_day = self.player.start_day

        
        self.weatherDisplay.add_to_display(self.screen, self.player)


    def run(self):
        while not self.done:
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            for button in self.date_sprites:
                button.handle_event(event)
            

    def run_logic(self):
        self.date_sprites.update(self.dt)
        

    def draw(self, display):

        
        if self.visible:
            self.date_sprites.add(self.monthUP, self.monthDOWN,self.dayUP, self.dayDOWN)
            pg.draw.rect(display, pg.Color(self.day_color),
                         (self.x, self.y, self.w, self.h))
            
            #pg.draw.rect(display, pg.Color(self.top_color),(self.x, self.y,
            ##self.w, self.h*.33))
            red = pg.transform.scale(RED,(self.w, int(self.h*.33)))
            display.blit(red,(self.x,self.y))

            month_label = pg.font.SysFont(self.font, self.font_size)
            TextSurf, TextRect = text_objects(self.month_name,
                                              month_label, pg.Color(self.font_color))
            TextRect.center = (self.x+self.w/2, self.button_h/2 + self.y)
            display.blit(TextSurf, TextRect)

            day_label = pg.font.SysFont(self.font, int(self.font_size*2.7))
            TextSurf, TextRect = text_objects(str(self.player.start_day),
                                              day_label, pg.Color(self.font_color))
            TextRect.center = (self.x+self.w/2, self.y+self.h/1.5)
            display.blit(TextSurf, TextRect)
            
            if self.buttons:
                self.date_sprites.draw(self.screen)
                
            pg.draw.rect(display, pg.Color(self.font_color),(self.x, self.y,
                                                             self.w, self.h), 2)
            pg.draw.rect(display, pg.Color(self.font_color),(self.x, self.y,
                                                             self.w, self.h*.33), 2)

        else:
            self.date_sprites.empty()

class FundsSpinner:

    def __init__(self, visible, screen, hiking_funds, player, x, y, width, title = "Starting Funds",
                 button_visible = True, font_size_title = 0,
                 top_color = "green", box_color = "white",
                 font_color = "black", font = "impact"):
        self.done = False
        self.screen = screen
        self.hiking_funds = hiking_funds
        self.player = player
        self.visible = visible
        self.x = x
        self.y = y
        self.w = width
        self.h = int(self.w*.43)
        self.font_size = int(self.h *.2)
        self.title = title
       
        
        self.buttons = button_visible
        
        self.button_w = int(self.w/10.5)
        self.button_h = int(self.w/7)

        self.top_color = top_color
        self.box_color = box_color
        self.font_color = font_color
        self.font = font

       # Scale the images to the desired size (doesn't modify the originals).
        self.right_normal = pg.transform.scale(RIGHT_NORMAL,(self.button_w, self.button_h))
        self.right_hover = pg.transform.scale(RIGHT_HOVER,(self.button_w, self.button_h))
        self.right_down = pg.transform.scale(RIGHT_DOWN,(self.button_w, self.button_h))

      
        # Scale the images to the desired size (doesn't modify the originals).
        self.left_normal = pg.transform.scale(LEFT_NORMAL,(self.button_w, self.button_h))
        self.left_hover = pg.transform.scale(LEFT_HOVER,(self.button_w, self.button_h))
        self.left_down = pg.transform.scale(LEFT_DOWN,(self.button_w, self.button_h))

        

        self.amountUP = Button(
            self.x + self.w - self.button_w, self.y+self.w/5.25, self.button_w, self.button_h+10, self.increment_amt,
            pg.font.SysFont("franklingothicmedium",35), '',
            pg.Color("black"), self.right_normal, self.right_hover, self.right_down)

        self.amountDOWN = Button(
            self.x,self.y+self.w/5.25 , self.button_w, self.button_h+10, self.decrement_amt,
            pg.font.SysFont("franklingothicmedium",35), '', pg.Color("black"),
            self.left_normal, self.left_hover, self.left_down)

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.fund_sprites = pg.sprite.Group()

        

    def increment_amt(self):
        if self.hiking_funds.funds < 10000:
            self.hiking_funds.funds +=1000
        
##        if self.player.funds <10000:
##            self.player.funds += 1000
####            self.str_amount = "$ " + format(self.player.funds, ',d')
##        

    def decrement_amt(self):
        if self.hiking_funds.funds > 3000:
            self.hiking_funds.funds -=1000
        
##        if self.player.funds > 3000:
##            self.player.funds -= 1000
####            self.str_amount = "$ " + format(self.player.funds, ',d')
        

    

    def run(self):
        while not self.done:
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():            
            for button in self.fund_sprites:
                button.handle_event(event)

    def run_logic(self):
        self.fund_sprites.update(self.dt)
        

    def draw(self, display):
        if self.visible:
            self.fund_sprites.add(self.amountUP, self.amountDOWN)
            pg.draw.rect(display, pg.Color(self.box_color), (self.x, self.y, self.w, self.h))
            pg.draw.rect(display, pg.Color(self.top_color),(self.x, self.y, self.w, self.h*.33))
            red = pg.transform.scale(GREEN,(self.w, int(self.h*.33)))
            display.blit(red,(self.x,self.y))
            
            

            title_label = pg.font.SysFont(self.font, self.font_size)
            TextSurf, TextRect = text_objects(self.title, title_label, pg.Color(self.font_color))
            TextRect.center = (self.x+self.w/2, self.y +(self.h*.33)/2)
            display.blit(TextSurf, TextRect)

    ##        str_amount = "$ " + format(self.player.funds, ',d')
            
            
            amount_label = pg.font.SysFont(self.font, int(self.font_size*2.5))
            TextSurf, TextRect = text_objects("$ " + format(self.hiking_funds.funds, ',.0f'),
                                              amount_label, pg.Color(self.font_color))

##            TextSurf, TextRect = text_objects("$ " + format(self.player.funds, ',.0f'),
##                                  amount_label, pg.Color(self.font_color))
            TextRect.center = (self.x+self.w/2, self.y+self.h/1.5)
            display.blit(TextSurf, TextRect)
            
            if self.buttons:
                self.fund_sprites.draw(self.screen)
                
            pg.draw.rect(display, pg.Color(self.font_color),(self.x, self.y, self.w, self.h), 2)
            pg.draw.rect(display, pg.Color(self.font_color),(self.x, self.y, self.w, self.h*.33), 2)
            



        


        


class WeatherDisplay():
    def __init__(self, visible, screen, player, x, y, w, h,pgIC, pgAC, fontName, fontSize):
        self.screen = screen
        self.visible = visible
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.player = player
        
        #self.month = player.month

        self.sunny  = pg.transform.scale(SUNNY,(90,90))
        self.rain  = pg.transform.scale(RAIN,(90,90))
        self.cloudy  = pg.transform.scale(CLOUDY,(90,90))
        self.t_storms  = pg.transform.scale(T_STORMS,(90,90))
        self.partly_cloudy  = pg.transform.scale(PARTLY_CLOUDY,(90,90))
        self.windy  = pg.transform.scale(WINDY,(90,90))
        self.sleet  = pg.transform.scale(SLEET,(90,90))
        self.snow = pg.transform.scale(SNOW,(90,90))
        self.cold  = pg.transform.scale(COLD,(90,90))
        self.warm  = pg.transform.scale(WARM,(90,90))
        self.hot = pg.transform.scale(HOT,(90,90))


    def add_to_display(self, display, player):
        if self.visible:

            pg.draw.rect(self.screen, pg.Color("white"), (self.x,self.y, self.w, self.h))
            pg.draw.rect(self.screen, pg.Color("black"), (self.x,self.y, self.w, self.h), 2)

            label = pg.font.SysFont("impact", 34)
            TextSurf, TextRect = text_objects(str(month_names(self.player.start_month)), label, pg.Color("black"))
            TextRect.center = (400,400)
            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects("Weather", label, pg.Color("black"))
            TextRect.center = (400,445)
            self.screen.blit(TextSurf, TextRect)


            if player.start_month == 1:
                self.screen.blit(self.partly_cloudy,(self.x+5, self.y+5))
                self.screen.blit(self.sleet,(self.x+98, self.y+5))
                self.screen.blit(self.cold,(self.x+389, self.y+5))
                self.screen.blit(self.snow,(self.x+482, self.y+5))

            elif player.start_month == 2 or player.start_month == 11:
                self.screen.blit(self.rain,(self.x+5, self.y+5))
                self.screen.blit(self.partly_cloudy,(self.x+98, self.y+5))
                self.screen.blit(self.cold,(self.x+389, self.y+5))
                self.screen.blit(self.sunny,(self.x+482, self.y+5))

            elif player.start_month == 3:
                
                display.blit(self.sunny,(self.x+5, self.y+5))
                display.blit(self.windy,(self.x+98, self.y+5))
                display.blit(self.warm,(self.x+389, self.y+5))
                display.blit(self.sleet,(self.x+482, self.y+5))

            elif player.start_month == 4 or player.start_month == 9:
                self.screen.blit(self.partly_cloudy,(self.x+5, self.y+5))
                self.screen.blit(self.sunny,(self.x+98, self.y+5))
                self.screen.blit(self.warm,(self.x+389, self.y+5))
                self.screen.blit(self.t_storms,(self.x+482, self.y+5))

            elif player.start_month == 5 or player.start_month == 10:
                self.screen.blit(self.partly_cloudy,(self.x+5, self.y+5))
                self.screen.blit(self.t_storms,(self.x+98, self.y+5))
                self.screen.blit(self.warm,(self.x+389, self.y+5))
                self.screen.blit(self.sunny,(self.x+482, self.y+5))

            elif player.start_month == 6:
                self.screen.blit(self.t_storms,(self.x+5, self.y+5))
                self.screen.blit(self.sunny,(self.x+98, self.y+5))
                self.screen.blit(self.hot,(self.x+389, self.y+5))
                self.screen.blit(self.partly_cloudy,(self.x+482, self.y+5))

            elif player.start_month == 7:
                self.screen.blit(self.sunny,(self.x+5, self.y+5))
                self.screen.blit(self.partly_cloudy,(self.x+98,self. y+5))
                self.screen.blit(self.hot,(self.x+389, self.y+5))
                self.screen.blit(self.t_storms,(self.x+482, self.y+5))

            elif player.start_month == 8:
                self.screen.blit(self.t_storms,(self.x+5, self.y+5))
                self.screen.blit(self.cloudy,(self.x+98, self.y+5))
                self.screen.blit(self.hot,(self.x+389, self.y+5))
                self.screen.blit(self.sunny,(self.x+482, self.y+5))

            elif player.start_month == 12:
                self.screen.blit(self.snow,(self.x+5, self.y+5))
                self.screen.blit(self.sleet,(self.x+98, self.y+5))
                self.screen.blit(self.cold,(self.x+389, self.y+5))
                self.screen.blit(self.partly_cloudy,(self.x+482, self.y+5))


class PackInfo:

    def __init__(self, visible, screen, hiker_funds, player, fontName="impact", fontSize =22, fontColor= "black"):
        self.done = False
        self.screen = screen
        self.hiker_funds = hiker_funds
        self.player = player
        self.visible = visible

        
        self.conv_box = pg.Rect(0, 0, 0, 0)
        self.lightweight_box = pg.Rect(0, 0, 0, 0)
        self.ultralight_box = pg.Rect(0, 0, 0, 0)

        
        self.color = pg.Color("black")
        self.player = player

        self.font = pg.font.SysFont(fontName, fontSize)
        self.font_size = fontSize
        self.font_color = pg.Color(fontColor)

        self.selected = pg.transform.scale(CHECK,(25, 25))

        
        
        
        self.activeChoice = None
        self.activeConv = False
        self.activeLight = False
        self.activeUltra = False
        


    def run(self):
        while not self.done:
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.draw()

    def handle_events(self, event):


        if event.type == pg.MOUSEBUTTONDOWN:
            self.activeConv = self.conv_box.collidepoint(event.pos)
            self.activeLight = self.lightweight_box.collidepoint(event.pos)
            self.activeUltra = self.ultralight_box.collidepoint(event.pos)

            if self.activeConv:
                self.activeChoice = self.conv_box
                self.player.gear = "Conventional"

            elif self.activeLight:
                self.activeChoice = self.lightweight_box
                self.player.gear = "Lightweight"
            elif self.activeUltra:
                self.activeChoice = self.ultralight_box
                self.player.gear = "Ultralight"
            else:
                self.activeChoice = None



    def draw(self, display):
        if self.visible:

            self.conv_box = pg.Rect(70, 185, 25, 25)
            self.lightweight_box = pg.Rect(70, 230, 25, 25)
            self.ultralight_box = pg.Rect(70, 275, 25, 25)

            
            pg.draw.rect(self.screen, pg.Color("white"), (50, 130,
                                                          350, 225))

            pg.draw.rect(self.screen, pg.Color("black"), (50, 130,
                                                          350, 225), 2)

            texture  = pg.transform.scale(GRAY,(350,45))
            self.screen.blit(texture,(50,130))

            

            pg.draw.rect(self.screen, pg.Color("black"), (50, 130,
                                                          350, 45), 2)

            label = pg.font.SysFont("impact", 30)
            TextSurf, TextRect = text_objects("Gear", label, pg.Color("black"))
            TextRect.center = (225, 152)
            display.blit(TextSurf, TextRect)

            

            textConv1 = "Weight doesn't matter! I'll take what I can get."
            textConv2 = "I'll take what I can get."

            textLight1 = "Lightweight sounds good! I'll shop deals."
            textlight2 = "I'll shop deals."

            textUltra1 = "I am a gram counter! I want the absolute best."
            textUltra2 = "I want the absolute best."

            defaulttext1 = "Pick your type of gear!"

            label = pg.font.SysFont("impact", 18)

            if self.player.gear == "Conventional":
                self.hiker_funds.gear_cost = 500
##                self.player.gear_cost = 500
                self.player.base_weight = 21
##                self.player.hiking_funds = self.player.funds - self.player.gear_cost
                
                
                TextSurf, TextRect = text_objects(textConv1, label, pg.Color("black"))
                TextRect.center = (225, 325)
                display.blit(TextSurf, TextRect)

    ##            TextSurf, TextRect = text_objects(textConv2, label, pg.Color("black"))
    ##            TextRect.center = (225, 420)
    ##            display.blit(TextSurf, TextRect)

            elif self.player.gear == "Lightweight":
                self.hiker_funds.gear_cost = 1500
##                self.player.gear_cost = 1500
                self.player.base_weight = 15
##                self.player.hiking_funds = self.player.funds - self.player.gear_cost
                
                
                
                
                TextSurf, TextRect = text_objects(textLight1, label, pg.Color("black"))
                TextRect.center = (225, 325)
                display.blit(TextSurf, TextRect)
    ##
    ##            TextSurf, TextRect = text_objects(textlight2, label, pg.Color("black"))
    ##            TextRect.center = (225, 420)
    ##            display.blit(TextSurf, TextRect)

            elif self.player.gear == "Ultralight":
                self.hiker_funds.gear_cost = 2500
##                self.player.gear_cost = 2500
                self.player.base_weight = 9
##                self.player.hiking_funds = self.player.funds - self.player.gear_cost
                
                
                
                TextSurf, TextRect = text_objects(textUltra1, label, pg.Color("black"))
                TextRect.center = (225, 325)
                display.blit(TextSurf, TextRect)
    ##
    ##            TextSurf, TextRect = text_objects(textUltra2, label, pg.Color("black"))
    ##            TextRect.center = (225, 420)
    ##            display.blit(TextSurf, TextRect)

            else:

                TextSurf, TextRect = text_objects(defaulttext1, label, pg.Color("black"))
                TextRect.center = (225, 325)
                display.blit(TextSurf, TextRect)


            pg.draw.rect(self.screen,(188, 244, 210), self.conv_box)
            pg.draw.rect(self.screen, self.color, self.conv_box, 2)
            pg.draw.rect(self.screen,(188, 244, 210), self.lightweight_box)
            pg.draw.rect(self.screen, self.color, self.lightweight_box, 2)
            pg.draw.rect(self.screen,(188, 244, 210), self.ultralight_box)
            pg.draw.rect(self.screen, self.color, self.ultralight_box, 2)


            TextSurf, TextRect = text_objects("Conventional",
                                              self.font, self.font_color)
            TextRect = (120, 182)
            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects("$ 500.00",
                                              self.font, self.font_color)
            TextRect = (300, 182)
            self.screen.blit(TextSurf, TextRect)

            

            TextSurf, TextRect = text_objects("Lightweight",
                                              self.font, self.font_color)
            TextRect = (120, 227)
            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects("$ 1,500.00",
                                              self.font, self.font_color)
            TextRect = (287, 227)
            self.screen.blit(TextSurf, TextRect)


            

            TextSurf, TextRect = text_objects("Ultralight",
                                              self.font, self.font_color)
            TextRect = (120, 272)
            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects("$ 2,500.00",
                                              self.font, self.font_color)
            TextRect = (285, 272)
            self.screen.blit(TextSurf, TextRect)

            if self.activeChoice !=None:
                self.screen.blit(self.selected,(self.activeChoice))

class GuideBook:

    def __init__(self, screen, waypoint_object, currentWaypoint):
        
        self.done = False
        self.clock = pg.time.Clock()
        self.screen = screen
        self.currentWaypoint = currentWaypoint
        self.blaze = pg.transform.scale(BLAZE, (25, 75))
        self.color = pg.Color("black")
        self.resupply_color = pg.Color("darkred")
        
        self.page_number = 1
        self.waypoint_dictionary = waypoint_object.dictionary
        
        self.total_pages = math.ceil((len(self.waypoint_dictionary) - (self.currentWaypoint-1))/12 )
        self.page_start = self.currentWaypoint
        self.page_end = self.page_start + 11
        self.page_list = []
        self.page_list = self.get_page()

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.guidebook_sprites = pg.sprite.Group()

        # Buttons
        self.close_guide = Button(
            550, 525, 200, 50, self.close_guide,
            pg.font.SysFont("franklingothicheavy",24),
            'Close Guide', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.next_page = Button(
            300, 525, 200, 50, self.next_page,
            pg.font.SysFont("franklingothicheavy",24),
            'Next Page', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.previous_page = Button(
            50, 525, 200, 50, self.previous_page,
            pg.font.SysFont("franklingothicheavy",24),
            'Previous Page', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        # Add the button sprites to the sprite group.
        self.guidebook_sprites.add(self.close_guide, self.next_page, self.previous_page)
        

    def close_guide(self):
        
        self.done = True
        

    def next_page(self):
        

        if self.page_number < self.total_pages:
            self.page_number += 1
            self.page_list = self.get_page()

        

    def previous_page(self):
        
        
        if self.page_number > 1:
            self.page_number -= 1
            self.page_start -= len(self.page_list)+ 12
            self.page_list = self.get_page()

    def run(self):
        while not self.done:
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                pg.quit()
                quit()
                
            for button in self.guidebook_sprites:
                button.handle_event(event)

    def get_page(self):
        self.page_list = []
        page_complete = False
        

        while not page_complete:
            waypoint_object = Waypoint(str(self.page_start))
            self.page_list.append(waypoint_object)
            self.page_start += 1

            if self.page_start == len(self.waypoint_dictionary)+1:
                page_complete = True

            if len(self.page_list) == 12:
                page_complete = True

        return self.page_list

    def run_logic(self):      
        self.guidebook_sprites.update(self.dt)

    def draw(self):
        mile_x = 140
        category_x = 180
        description_x = 310
        elevation_x = 635
        y = 205
        
        
        self.screen.fill((100, 100, 100))

        title1 = drop_shadow_text("AT Guidebook",
             "impact", 70, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title1, center_of_surface(title1, 400, 65))
        self.screen.blit(self.blaze, (50,28))
        self.screen.blit(self.blaze, (725,28))

        pg.draw.rect(self.screen, pg.Color("white"),(50, 130, 700, 375))
        pg.draw.rect(self.screen, pg.Color("black"),(50, 130, 700, 375),2)


        text, text_rect = text_objects("Mile", pg.font.SysFont("impact",22), self.color)
        text_rect.center = (120, 160) 

        self.screen.blit(text, text_rect)

        text, text_rect = text_objects("Category", pg.font.SysFont("impact",22), self.color)
        text_rect.center = (220, 160) 

        self.screen.blit(text, text_rect)

        text, text_rect = text_objects("Description", pg.font.SysFont("impact",22), self.color)
        text_rect.center = (360, 160) 

        self.screen.blit(text, text_rect)

        text, text_rect = text_objects("Elevation", pg.font.SysFont("impact",22), self.color)
        text_rect.center = (670, 160) 

        self.screen.blit(text, text_rect)

        pg.draw.line(self.screen, pg.Color("black"), (75, 175), (725,175), 2) 

        for o in self.page_list:
            if o.category == "Resupply":
                color = self.resupply_color
                font = pg.font.SysFont("consolas",20)
            else:
                color = self.color
                font = pg.font.SysFont("courier",18)
                
            text, text_rect = text_objects(str(o.mile), font, color)
            text_rect.bottomright = (mile_x, y) 

            self.screen.blit(text, text_rect)

            text, text_rect = text_objects(str(o.category), font, color)
            text_rect.bottomleft = (category_x, y) 

            self.screen.blit(text, text_rect)

            text, text_rect = text_objects(str(o.description), font, color)
            text_rect.bottomleft = (description_x, y) 

            self.screen.blit(text, text_rect)

            text, text_rect = text_objects(str(o.elevation) + " ft", font, color)
            text_rect.bottomleft = (elevation_x, y) 

            self.screen.blit(text, text_rect)

            y += 26
        
        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)

        self.guidebook_sprites.draw(self.screen)
        cursor_AT(self.screen, True)
        pg.display.flip()




        






class Next_Resupply_Waypoint:
    def __init__(self, player, waypoint_object):
        self.player = player
        self.current_location = waypoint_object
        self.next_resupply_mile = 0
        self.next_resupply_waypoint = None
        self.next_resupply_set = False
        self.miles_to_next = 0.0

    def update(self, waypoint_object):
        self.current_location = waypoint_object
        
        id_num = int(self.current_location.id_num)

        if self.miles_to_next == 0.0:
            self.next_resupply_set = False

        while not self.next_resupply_set and int(self.current_location.id_num)\
              < len(self.current_location.dictionary):

            next_waypoint_object = Waypoint(str(id_num + 1))


            if 'resupply' in next_waypoint_object.actions:
                self.next_resupply_waypoint = next_waypoint_object
                self.next_resupply_mile = self.next_resupply_waypoint.mile
                self.next_resupply_set = True

            if id_num < len(self.current_location.dictionary) - 1:
                    id_num += 1

            elif 'Terminus' in next_waypoint_object.category:
                self.next_resupply_set = True
                self.next_resupply_mile = "  --  "
                
            else:
                self.next_resupply_set = True
                self.next_resupply_mile = "  --  "
                
        if self.next_resupply_mile != "  --  ":
            self.miles_to_next = round(self.next_resupply_mile - self.player.mile,1)
        else:
            self.miles_to_next = "  --  "



class Next_Water_Waypoint:
    def __init__(self, player, waypoint_object):
        self.player = player
        self.current_location = waypoint_object
        self.next_water_mile = 0
        self.next_water_waypoint = None
        self.next_water_set = False
        self.miles_to_next = 0.0

    def update(self, waypoint_object):
        self.current_location = waypoint_object
               
        id_num = int(self.current_location.id_num)

        if self.miles_to_next == 0.0:
            self.next_water_set = False

        while not self.next_water_set and int(self.current_location.id_num)\
              < len(self.current_location.dictionary):

            next_waypoint_object = Waypoint(str(id_num + 1))

            if 'water' in next_waypoint_object.actions:
                self.next_water_waypoint = next_waypoint_object
                self.next_water_mile = self.next_water_waypoint.mile
                self.next_water_set = True

            if id_num < len(self.current_location.dictionary) - 1:
                    id_num += 1

            elif 'Terminus' in next_waypoint_object.category:
                self.next_water_set = True
                self.next_water_mile = "  --  "
                
            else:
                self.next_water_set = True
                self.next_water_mile = "  --  "
                
        if self.next_water_mile != "  --  ":
            self.miles_to_next = round(self.next_water_mile - self.player.mile,1)
        else:
            self.miles_to_next = "  --  "

class Next_Camping_Waypoint:
    def __init__(self, player, waypoint_object):
        self.player = player
        self.current_location = waypoint_object
        self.next_camping_mile = 0
        self.next_camping_waypoint = None
        self.next_camping_set = False
        self.miles_to_next = 0.0

    def update(self, waypoint_object):
        self.current_location = waypoint_object
               
        id_num = int(self.current_location.id_num)

        if self.miles_to_next == 0.0:
            self.next_camping_set = False

        while not self.next_camping_set and int(self.current_location.id_num)\
              < len(self.current_location.dictionary):

            next_waypoint_object = Waypoint(str(id_num + 1))

            if 'sleep' in next_waypoint_object.actions:
                self.next_camping_waypoint = next_waypoint_object
                self.next_camping_mile = self.next_camping_waypoint.mile
                self.next_camping_set = True

            if id_num < len(self.current_location.dictionary) - 1:
                    id_num += 1

            elif 'Terminus' in next_waypoint_object.category:
                self.next_camping_set = True
                self.next_camping_mile = "  --  "
                
            else:
                self.next_camping_set = True
                self.next_camping_mile = "  --  "
                
        if self.next_camping_mile != "  --  ":
            self.miles_to_next = round(self.next_camping_mile - self.player.mile,1)
        else:
            self.miles_to_next = "  --  "
        
class RandomTrailImage:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.random_trail_dict = get_trail_images()
        self.trailImage = pg.transform.scale(pg.image.load(resource_path("images/trail/foggy.jpg")),
                                               (400, 275))
        self.frameImage = pg.transform.scale(pg.image.load(resource_path("images/picframe.png")),
                                               (430, 350))
        
        self.comment = "The fog has taken over."


    def pickRandom(self):
        
        image_number = str(random.randint(1,13))

        image_str = self.random_trail_dict[image_number]['image']
        self.comment = self.random_trail_dict[image_number]['description']

        self.trailImage = pg.transform.scale(pg.image.load(resource_path(image_str)),
                                               (400, 275))

        #print(image_str)
        #print (comment)

        return self.trailImage, self.comment


    def draw(self):

        self.screen.blit(self.trailImage,(246,153))
        self.screen.blit(self.frameImage,(227,135))

        small_label = pg.font.SysFont("franklingothicheavy", 22)

        TextSurf, TextRect = text_objects(self.comment, small_label, pg.Color("black"))
        TextRect.center = (442, 457)
        self.screen.blit(TextSurf, TextRect)




class RandomWaterImage:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.random_water_dict = get_water_images()
        self.randomImage = pg.transform.scale(pg.image.load(resource_path("images/water/water.jpg")),
                                               (400, 275))
        
        

    def pickRandom(self):
        
        image_number = str(random.randint(1,5))
        #print(self.month)
        #print(image_number)

        image_str = self.random_water_dict[image_number]['image']
        comment = self.random_water_dict[image_number]['description']

        #print(image_str)
        #print (comment)

        return image_str, comment

class RandomImage:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.random_images_dict = get_random_images()
        self.randomImage = pg.transform.scale(pg.image.load(resource_path("images/random/dandelion.jpg")),
                                               (400, 275))

        #print("in random")
        
        
        

    def pickRandom(self):
        
        image_number = str(random.randint(1,10))
        #print(self.month)
        #print("image number", image_number)

        image_str = self.random_images_dict[image_number]['image']
        comment = self.random_images_dict[image_number]['description']


        return image_str, comment
        

class WaypointDisplay:
    def __init__(self, screen, waypoint_object, player, mileage_counter):
        
        self.screen = screen
        self.player = player
        self.waypoint_object = waypoint_object
        
        self.mile_counter = mileage_counter
        
        self.month = self.player.current_month

        
        self.displayImage = pg.transform.scale(pg.image.load(resource_path("images/intro2.png")),
                                               (400, 275))

        self.frameImage = pg.transform.scale(pg.image.load(resource_path("images/picframe.png")),
                                               (430, 350))

        self.mile = "Welcome to the Appalachian Trail!"
        self.description = ""
        self.comment = "An amazing journey awaits."
        self.add_comm = "Click Start Hike to Begin."
        self.actions = ""
        self.coordinates = ""
        self.x = 0
        self.y = 0
        
        

        
        


    def update(self, waypoint_object):
            self.waypoint_object = waypoint_object
##            print(self.waypoint_object.mile)

            self.mile = "Mile " + str(self.waypoint_object.mile)\
                        + " - " + self.waypoint_object.description
            self.description = ""
            self.comment = ""
            self.add_comm = ""
            self.actions = self.waypoint_object.actions
            self.coordinates = self.waypoint_object.coordinates
            self.x, self.y = self.coordinates.split(",")

            image_str = self.waypoint_object.image

            if image_str =="n":
                random_image = RandomImage(self.screen, self.player)

                image_str, description = random_image.pickRandom()
                
                self.displayImage = pg.transform.scale(pg.image.load(resource_path(image_str)),
                                               (400, 275))
                self.comment = description

                
                
                #display random image
                

            elif image_str == "w":
                random_water = RandomWaterImage(self.screen, self.player)

                image_str, description = random_water.pickRandom()
                
                self.displayImage = pg.transform.scale(pg.image.load(resource_path(image_str)),
                                               (400, 275))

                self.comment = description

            else: 
                self.displayImage = pg.transform.scale(pg.image.load(resource_path(image_str)),
                                                   (400, 275))
                self.comment = self.waypoint_object.comment




    def draw(self):
            
        self.screen.blit(self.displayImage,(246,153))
        self.screen.blit(self.frameImage,(227,135))

        large_label = pg.font.SysFont("franklingothicheavy", 20)
        
        TextSurf, TextRect = text_objects(self.mile, large_label, pg.Color("black"))
        TextRect.center = (442, 443)
        self.screen.blit(TextSurf, TextRect)

        small_label = pg.font.SysFont("franklingothicheavy", 18)

        TextSurf, TextRect = text_objects(self.comment, small_label, pg.Color("black"))
        TextRect.center = (442, 468)
        self.screen.blit(TextSurf, TextRect)




class Waypoint:
    """Waypoint on the trai"""
    def __init__(self, id_num):
        self.dictionary = get_waypoint_data()
        self.id_num = str(id_num)
        self.actions = self.dictionary[self.id_num]['actions']
        self.mile = self.dictionary[self.id_num]['mile']
        self.description = self.dictionary[self.id_num]['description']
        self.elevation = self.dictionary[self.id_num]['elevation']
        self.category = self.dictionary[self.id_num]['category']
        self.type = self.dictionary[self.id_num]['type']
        self.distance = self.dictionary[self.id_num]['distance']
        self.food_storage = self.dictionary[self.id_num]['food_storage']
        self.image = self.dictionary[self.id_num]['image']
        self.resupply_options = self.dictionary[self.id_num]['resupply_options']
        self.comment = self.dictionary[self.id_num]['comment']
        self.state = self.dictionary[self.id_num]['state']
        self.coordinates = self.dictionary[self.id_num]['coordinates']
        
 
  


        
            
class Mail_Option:
    """Mail Option on the trai"""
    def __init__(self, key):
        self.dictionary = get_resupply_options()
        self.key = str(key)
        self.id_num = self.dictionary[self.key]['id_num']
        self.mile = self.dictionary[self.key]['mile']
        self.description = self.dictionary[self.key]['description']
        self.distance = self.dictionary[self.key]['distance']
        self.post_office = self.dictionary[self.key]['post_office']


class Mail_Options_List:

    def __init__(self, screen, mail_option_object, player):
        
        self.done = False
        self.clock = pg.time.Clock()
        self.screen = screen
        self.player = player
        self.currentWaypoint = self.player.current_waypoint
        self.blaze = pg.transform.scale(BLAZE, (25, 75))
        
        self.color = pg.Color("black")

        self.page_number = 1
        self.mail_dictionary = mail_option_object.dictionary
        self.all_options = [(k,v) for k,v in self.mail_dictionary.items()]
        self.available_options = []
        self.available_options_list()

        
        self.total_pages = math.ceil(len(self.available_options)/5)
                            
        self.page_start = 1
        self.page_end = self.page_start + 4
        self.page_list = []
        self.page_list = self.get_page()
        self.option1 = pg.Rect(0, 0, 0, 0)
        self.option2 = pg.Rect(0, 0, 0, 0)
        self.option3 = pg.Rect(0, 0, 0, 0)
        self.option4 = pg.Rect(0, 0, 0, 0)
        self.option5 = pg.Rect(0, 0, 0, 0)
        self.selected = -1
        self.selected_image = pg.transform.scale(CHECK,(25, 25))
        self.activeChoice = None
        self.active1 = False
        self.active2 = False
        self.active3 = False
        self.active4 = False
        self.active5 = False

        self.box = None
        self.send_to = None
        self.box_category = None
        self.box_sent = False
        
  
        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.list_sprites = pg.sprite.Group()

        # Buttons

        self.mail_btn = Button(
            585, 525, 165, 50, self.mail_box,
            pg.font.SysFont("franklingothicheavy",20),
            'Mail Box - $10', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.close_list_btn = Button(
            50, 525, 165, 50, self.close_list,
            pg.font.SysFont("franklingothicheavy",20),
            'Cancel', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.next_page = Button(
            405, 525, 170, 50, self.next_page,
            pg.font.SysFont("franklingothicheavy",20),
            'Next Page', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.previous_page = Button(
            225, 525, 170, 50, self.previous_page,
            pg.font.SysFont("franklingothicheavy",20),
            'Previous Page', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        # Add the button sprites to the sprite group.
        self.list_sprites.add(self.mail_btn, self.close_list_btn, self.next_page, self.previous_page)

    def available_options_list(self):
        for i in self.all_options:
            if i[1]['mile'] > self.player.mile:
                self.available_options.append(i)
        
    def close_list(self):
        self.done = True

    def mail_box(self):
        if self.activeChoice != None:
            self.player.mail_drops.append((self.send_to, self.box_category, self.box))
            
            self.box_sent = True 
            self.done = True
            
        

    def next_page(self):
        self.activeChoice = None
        
        if self.page_number < self.total_pages:

            self.page_number += 1
            self.page_list = self.get_page()

        

    def previous_page(self):

        self.activeChoice = None
        
        if self.page_number > 1:
            self.page_number -= 1
            self.page_start -= len(self.page_list)+ 5
            self.page_list = self.get_page()

    def run(self):
        while not self.done:
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):

                
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                pg.quit()
                quit()
                
            for button in self.list_sprites:
                button.handle_event(event)

            if event.type == pg.MOUSEBUTTONDOWN:
                self.active1 = self.option1.collidepoint(event.pos)
                self.active2 = self.option2.collidepoint(event.pos)
                self.active3 = self.option3.collidepoint(event.pos)
                self.active4 = self.option4.collidepoint(event.pos)
                self.active5 = self.option5.collidepoint(event.pos)

                if self.active1:
                    self.activeChoice = self.option1
                    self.selected = 0
                    self.send_to = self.page_list[self.selected]
                    
                elif self.active2:
                    self.activeChoice = self.option2
                    self.selected = 1
                    self.send_to = self.page_list[self.selected]
                    
                elif self.active3:
                    self.activeChoice = self.option3
                    self.selected = 2
                    self.send_to = self.page_list[self.selected]
                    
                elif self.active4:
                    self.activeChoice = self.option4
                    self.selected = 3
                    self.send_to = self.page_list[self.selected]
                    
                elif self.active5:
                    self.activeChoice = self.option5
                    self.selected = 4
                    self.send_to = self.page_list[self.selected]
                    
##                else:
##                    self.activeChoice = None


            

    def get_page(self):
        self.page_list = []
        page_complete = False
        

        while not page_complete:
            list_object = Mail_Option(str(self.page_start))

            if list_object.mile > self.player.mile:

                self.page_list.append(list_object)

            self.page_start += 1

            if self.page_start == len(self.mail_dictionary)+1:
                page_complete = True

            if len(self.page_list) == 5:
                page_complete = True

        return self.page_list

    def run_logic(self):
        
        self.list_sprites.update(self.dt)

    def draw(self):
        mile_x = 140
        description_x = 170
        distance_x = 500
        send_here_x = 635
        y = 235
        
        
        self.screen.fill((100, 100, 100))

        title1 = drop_shadow_text("Mailing Options",
             "impact", 70, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title1, center_of_surface(title1, 400, 65))
        self.screen.blit(self.blaze, (50,28))
        self.screen.blit(self.blaze, (725,28))

        pg.draw.rect(self.screen, pg.Color("white"),(50, 130, 700, 375))
        pg.draw.rect(self.screen, pg.Color("black"),(50, 130, 700, 375),2)


        text, text_rect = text_objects("Mile", pg.font.SysFont("impact",22), self.color)
        text_rect.center = (120, 180) 

        self.screen.blit(text, text_rect)

        text, text_rect = text_objects("Description", pg.font.SysFont("impact",22), self.color)
        text_rect.center = (220, 180) 

        self.screen.blit(text, text_rect)

        text, text_rect = text_objects("Distance", pg.font.SysFont("impact",22), self.color)
        text_rect.center = (545, 157)
        self.screen.blit(text, text_rect)

        text, text_rect = text_objects("From Trail", pg.font.SysFont("impact",22), self.color)
        text_rect.center = (545, 180) 

        self.screen.blit(text, text_rect)

        text, text_rect = text_objects("Send Here", pg.font.SysFont("impact",22), self.color)
        text_rect.center = (670, 180) 

        self.screen.blit(text, text_rect)

        pg.draw.line(self.screen, pg.Color("black"), (75, 195), (725,195), 2) 

        for o in self.page_list:
            if o.post_office == 'yes':
                description = "Post Office - " + o.description
            else:
                description = o.description
                
            text, text_rect = text_objects(str(o.mile), pg.font.SysFont("consolas",18), self.color)
            text_rect.bottomright = (mile_x, y) 

            self.screen.blit(text, text_rect)

            text, text_rect = text_objects(description, pg.font.SysFont("consolas",18), self.color)
            text_rect.bottomleft = (description_x, y) 

            self.screen.blit(text, text_rect)

            text, text_rect = text_objects(str(o.distance) + " miles", pg.font.SysFont("consolas",20), self.color)
            text_rect.bottomleft = (distance_x, y) 

            self.screen.blit(text, text_rect)


            y += 60


        self.option1 = pg.Rect(660, 210, 25, 25)
        self.option2 = pg.Rect(660, 270, 25, 25)
        self.option3 = pg.Rect(660, 330, 25, 25)
        self.option4 = pg.Rect(660, 390, 25, 25)
        self.option5 = pg.Rect(660, 450, 25, 25)
        
        if len(self.page_list) >= 1:
            pg.draw.rect(self.screen,(188, 244, 210), self.option1)
            pg.draw.rect(self.screen, self.color, self.option1, 2)

        if len(self.page_list) >= 2:
            pg.draw.rect(self.screen,(188, 244, 210), self.option2)
            pg.draw.rect(self.screen, self.color, self.option2, 2)

        if len(self.page_list) >= 3:
            pg.draw.rect(self.screen,(188, 244, 210), self.option3)
            pg.draw.rect(self.screen, self.color, self.option3, 2)

        if len(self.page_list) >= 4:
            pg.draw.rect(self.screen,(188, 244, 210), self.option4)
            pg.draw.rect(self.screen, self.color, self.option4, 2)
            
        if len(self.page_list) >= 5:
            pg.draw.rect(self.screen,(188, 244, 210), self.option5)
            pg.draw.rect(self.screen, self.color, self.option5, 2)

        if self.activeChoice !=None:
           
            self.screen.blit(self.selected_image,(self.activeChoice))
                    
        
        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)

        self.list_sprites.draw(self.screen)
        cursor_AT(self.screen, True)
        pg.display.flip()

class Food_Store:  
    def __init__(self, screen, player, hiker_funds, current_resupply):
        
        self.done = False
        self.clock = pg.time.Clock()
        self.screen = screen
        self.player = player
        self.hiker_funds = hiker_funds
        self.current_resupply = current_resupply
        self.blaze = pg.transform.scale(BLAZE, (25, 75))
        self.items_bought = False
        self.food_action_complete = False
        self.label = "Choose an action:"
        
        self.markup = 1 * self.current_resupply.food_markup

        self.meal_cost = 2.50 + (2.50 * self.current_resupply.food_markup)

        self.snack_cost = 1.25 + (1.25 * self.current_resupply.food_markup)

        self.num_breakfasts = 0
        self.num_lunches = 0
        self.num_dinners = 0
        self.num_snacks = 0
        self.food_cost = ((self.num_breakfasts + self.num_lunches + self.num_dinners) * self.meal_cost)\
                         + (self.num_snacks * (1.25 * self.snack_cost))
        self.food_weight = (self.num_breakfasts * .5) + (self.num_lunches * .5)\
                     + (self.num_dinners * .5) + (self.num_snacks * .25)

        self.box = []


        
        self.show_cart = True
        self.bought_items = False
        
        self.waypoint_object = Waypoint(self.player.current_waypoint)
        
        self.guide_book = GuideBook(self.screen, self.waypoint_object, self.player.current_waypoint)

        self.mail_option = Mail_Option(1)
        self.mail_list = Mail_Options_List(self.screen, self.mail_option, self.player)
        
        
        self.grocery_list = [("Breakfast",self.meal_cost), ("Lunch",self.meal_cost),
                             ("Dinner", self.meal_cost), ("Snack",self.snack_cost)]

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.grocery_sprites = pg.sprite.Group()

        self.breakfast_up = Button(
             560, 286, 20, 20, self.increase_breakfast,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),UP_NORMAL, UP_HOVER,UP_DOWN)

        self.breakfast_down = Button(
            560, 307, 20, 20, self.decrease_breakfast,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),DOWN_NORMAL,DOWN_HOVER,DOWN_DOWN)

        self.lunch_up = Button(
             560, 336, 20, 20, self.increase_lunch,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),UP_NORMAL, UP_HOVER,UP_DOWN)

        self.lunch_down = Button(
            560, 357, 20, 20, self.decrease_lunch,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),DOWN_NORMAL,DOWN_HOVER,DOWN_DOWN)

        self.dinner_up = Button(
             560, 386, 20, 20, self.increase_dinner,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),UP_NORMAL, UP_HOVER,UP_DOWN)

        self.dinner_down = Button(
            560, 407, 20, 20, self.decrease_dinner,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),DOWN_NORMAL,DOWN_HOVER,DOWN_DOWN)

        self.snack_up = Button(
             560, 436, 20, 20, self.increase_snacks,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),UP_NORMAL, UP_HOVER,UP_DOWN)

        self.snack_down = Button(
            560, 457, 20, 20, self.decrease_snacks,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),DOWN_NORMAL,DOWN_HOVER,DOWN_DOWN)

        self.guidebook_btn = Button(
            100, 420, 150, 50, self.show_guide,
            pg.font.SysFont("franklingothicheavy",20),
            'Guidebook', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.buy_btn = Button(
            600, 350, 130, 50, self.buy,
            pg.font.SysFont("franklingothicheavy",20),
            'Buy Items', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.done_shopping = Button(
            300, 525, 200, 50, self.done_shopping,
            pg.font.SysFont("franklingothicheavy",24),
            'Done Shopping', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.mail_btn = Button(
            545, 315, 175, 50, self.mail_items,
            pg.font.SysFont("franklingothicheavy",24),
            'Mail Ahead', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.add_to_pack_btn = Button(
            545, 390, 175, 50, self.add_to_pack,
            pg.font.SysFont("franklingothicheavy",24),
            'Add to Pack', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

       
        # Add the button sprites to the sprite group.
        self.grocery_sprites.add(self.guidebook_btn, self.buy_btn, self.done_shopping,
                                 self.breakfast_up, self.breakfast_down,
                                 self.lunch_up, self.lunch_down,
                                 self.dinner_up, self.dinner_down,
                                 self.snack_up, self.snack_down)

    def show_guide(self):
        self.guide_book = GuideBook(self.screen, self.waypoint_object, self.player.current_waypoint)
        self.guide_book.done = False
        self.guide_book.run()
                                                                                                                                                                                                                                                                           

    def add_to_pack(self):
        self.food_action_complete = True
        self.player.breakfast += self.num_breakfasts
        self.player.lunch += self.num_lunches
        self.player.dinner += self.num_dinners
        self.player.snacks += self.num_snacks

        self.food_weight = 0

        self.num_breakfasts = 0
        self.num_lunches = 0
        self.num_dinners = 0        
        self.num_snacks = 0

        

        self.show_cart = True
        self.bought_items = False
        self.grocery_sprites.remove(self.mail_btn, self.add_to_pack_btn)
        self.grocery_sprites.add(self.buy_btn,self.breakfast_up, self.breakfast_down,
                     self.lunch_up, self.lunch_down,
                     self.dinner_up, self.dinner_down,
                     self.snack_up, self.snack_down)
        
        
    def mail_items(self):
        self.food_action_complete = True
        self.box = [("Breakfast", self.num_breakfasts),("Lunch",self.num_lunches),
                    ("Dinner",self.num_dinners),("Snacks",self.num_snacks)]
        self.mail_list.box = self.box
        

        
        self.mail_list.activeChoice = None
        self.mail_list.done = False
        self.mail_list.run()


        if self.mail_list.box_sent:
            self.food_weight = 0

            self.num_breakfasts = 0
            self.num_lunches = 0
            self.num_dinners = 0        
            self.num_snacks = 0
            self.hiker_funds.other_costs += 10
            
            self.show_cart = True
            self.bought_items = False

            self.grocery_sprites.remove(self.mail_btn, self.add_to_pack_btn)
            self.grocery_sprites.add(self.buy_btn,self.breakfast_up, self.breakfast_down,
                     self.lunch_up, self.lunch_down,
                     self.dinner_up, self.dinner_down,
                     self.snack_up, self.snack_down)
            
        


    def buy(self):
        if self.food_cost > 0:
            self.items_bought = True
            self.show_cart = False
            self.bought_items = True
            self.hiker_funds.food_cost += self.food_cost
##            #self.player.balance -= self.food_cost
####            print("Player Balance", self.player.balance)
##            print("Hiker Funds Available", self.hiker_funds.calculate_available())
            self.grocery_sprites.remove(self.buy_btn,self.breakfast_up, self.breakfast_down,
                                 self.lunch_up, self.lunch_down,
                                 self.dinner_up, self.dinner_down,
                                 self.snack_up, self.snack_down)
            
            self.grocery_sprites.add(self.mail_btn, self.add_to_pack_btn)
            self.food_cost = 0.00

        

    def done_shopping(self):

        if self.food_action_complete == False:
            self.label = "Action Required:"
            
        if self.food_action_complete == True:   
            self.player.hiking_funds = self.hiker_funds
            self.done = True

        if self.items_bought == False:
            self.done = True
        

    def increase_breakfast(self):
        if self.num_breakfasts < 10:
            self.num_breakfasts += 1
            self.food_cost = ((self.num_breakfasts + self.num_lunches + self.num_dinners) * self.meal_cost)\
                         + (self.num_snacks * self.snack_cost)
            self.food_weight = (self.num_breakfasts * .5) + (self.num_lunches * .5)\
                     + (self.num_dinners * .5) + (self.num_snacks * .25)


    def decrease_breakfast(self):
        if self.num_breakfasts > 0:
            self.num_breakfasts -= 1
            self.food_cost = ((self.num_breakfasts + self.num_lunches + self.num_dinners) * self.meal_cost)\
                         + (self.num_snacks * self.snack_cost)
            self.food_weight = (self.num_breakfasts * .5) + (self.num_lunches * .5)\
                     + (self.num_dinners * .5) + (self.num_snacks * .25)
        
        

    def increase_lunch(self):
        if self.num_lunches < 10:
            self.num_lunches += 1
            self.food_cost = ((self.num_breakfasts + self.num_lunches + self.num_dinners) * self.meal_cost)\
                         + (self.num_snacks * self.snack_cost)
            self.food_weight = (self.num_breakfasts * .5) + (self.num_lunches * .5)\
                     + (self.num_dinners * .5) + (self.num_snacks * .25)


    def decrease_lunch(self):
        if self.num_lunches > 0:
            self.num_lunches -= 1
            self.food_cost = ((self.num_breakfasts + self.num_lunches + self.num_dinners) * self.meal_cost)\
                         + (self.num_snacks * self.snack_cost)
            self.food_weight = (self.num_breakfasts * .5) + (self.num_lunches * .5)\
                     + (self.num_dinners * .5) + (self.num_snacks * .25)
        

    def increase_dinner(self):
        if self.num_dinners < 10:
            self.num_dinners += 1
            self.food_cost = ((self.num_breakfasts + self.num_lunches + self.num_dinners) * self.meal_cost)\
                         + (self.num_snacks * self.snack_cost)
            self.food_weight = (self.num_breakfasts * .5) + (self.num_lunches * .5)\
                     + (self.num_dinners * .5) + (self.num_snacks * .25)

    def decrease_dinner(self):
        if self.num_dinners > 0:
            self.num_dinners -= 1
            self.food_cost = ((self.num_breakfasts + self.num_lunches + self.num_dinners) * self.meal_cost)\
                         + (self.num_snacks * self.snack_cost)
            self.food_weight = (self.num_breakfasts * .5) + (self.num_lunches * .5)\
                     + (self.num_dinners * .5) + (self.num_snacks * .25)

    def increase_snacks(self):
        if self.num_snacks < 20:
            self.num_snacks += 1
            self.food_cost = ((self.num_breakfasts + self.num_lunches + self.num_dinners) * self.meal_cost)\
                         + (self.num_snacks * self.snack_cost)
            self.food_weight = (self.num_breakfasts * .5) + (self.num_lunches * .5)\
                     + (self.num_dinners * .5) + (self.num_snacks * .25)
        

    def decrease_snacks(self):
        if self.num_snacks > 0:
            self.num_snacks -= 1
            self.food_cost = ((self.num_breakfasts + self.num_lunches + self.num_dinners) * self.meal_cost)\
                         + (self.num_snacks * self.snack_cost)
            self.food_weight = (self.num_breakfasts * .5) + (self.num_lunches * .5)\
                     + (self.num_dinners * .5) + (self.num_snacks * .25)
        

    def run(self):
        while not self.done:
            self.screen.fill((100,100,100))
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                pg.quit()
                quit()
                
            for button in self.grocery_sprites:
                button.handle_event(event)

    def run_logic(self):

        self.grocery_sprites.update(self.dt)

    def draw(self):

        title1 = drop_shadow_text("Food Supplies",
             "impact", 70, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title1, center_of_surface(title1, 400, 65))
        self.screen.blit(self.blaze, (50,28))
        self.screen.blit(self.blaze, (725,28))
        green  = pg.transform.scale(GREEN,(175,36))
        blue  = pg.transform.scale(CLOUD,(175,36))
        

        pg.draw.rect(self.screen, pg.Color("white"),(50, 120, 700, 385))
        self.screen.blit(green,(50,120))
        self.screen.blit(blue,(225,120))
        self.screen.blit(green,(400,120))
        self.screen.blit(blue,(575,120))
        
        pg.draw.rect(self.screen, pg.Color("black"),(50, 120, 700, 385),2)
        
        pg.draw.line(self.screen, pg.Color("black"),(224,120), (224,215), 2)
        pg.draw.line(self.screen, pg.Color("black"),(399,120), (399,215), 2)
        pg.draw.line(self.screen, pg.Color("black"),(574,120), (574,215), 2)
        pg.draw.line(self.screen, pg.Color("black"),(300,216), (300,505), 2)

        
        pg.draw.line(self.screen, pg.Color("black"),(50,156), (750,156), 2)
        pg.draw.line(self.screen, pg.Color("black"),(50,216), (750,216), 2)
 

##        pg.draw.line(self.screen, pg.Color("black"),(50,348), (225,348), 2)


        label = pg.font.SysFont("impact", 22)
        TextSurf, TextRect = text_objects("Available Funds", label, pg.Color("black"))
        TextRect.center = (137, 138)
        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Pack Weight", label, pg.Color("black"))
        TextRect.center = (312, 138)
        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Food Cost", label, pg.Color("black"))
        TextRect.center = (487, 138)
        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Food Weight", label, pg.Color("black"))
        TextRect.center = (662, 138)
        self.screen.blit(TextSurf, TextRect)

        amount_label = pg.font.SysFont("impact", 28)
        TextSurf, TextRect = text_objects("$ " + str(format(self.hiker_funds.calculate_available(), '.2f')),
                                          amount_label, pg.Color("black"))
        TextRect.center = (137, 185)
        self.screen.blit(TextSurf, TextRect)


        TextSurf, TextRect = text_objects(str(format(self.player.calculate_Packweight() ,'.1f') + " LBS"),
                                          amount_label, pg.Color("black"))
        TextRect.center = (312, 185)
        self.screen.blit(TextSurf, TextRect)

   
        TextSurf, TextRect = text_objects("$ " + format(self.food_cost, '.2f'),
                                          amount_label, pg.Color("black"))
        TextRect.center = (487, 185)
        self.screen.blit(TextSurf, TextRect)


        TextSurf, TextRect = text_objects(str(format(self.food_weight ,'.1f') + " LBS"),
                                          amount_label, pg.Color("black"))
        TextRect.center = (662, 185)
        self.screen.blit(TextSurf, TextRect)

        current_label = pg.font.SysFont("impact", 28)
        ind_label = pg.font.SysFont("consolas", 22)
        list_label = pg.font.SysFont("impact", 22)
        num_label = pg.font.SysFont("impact", 24)

        TextSurf, TextRect = text_objects("In Pack Supplies", current_label, pg.Color("black"))
        TextRect.center = (177, 250)
        self.screen.blit(TextSurf, TextRect)

        if self.show_cart:
        
            TextSurf, TextRect = text_objects("Shopping Cart", current_label, pg.Color("black"))
            TextRect.center = (450, 250)
            self.screen.blit(TextSurf, TextRect)
            y = 320

            for item in self.grocery_list:
                TextSurf, TextRect = text_objects(item[0], list_label,
                                              pg.Color("black"))
                TextRect.bottomleft = (330, y) 

                self.screen.blit(TextSurf, TextRect)

                TextSurf, TextRect = text_objects("$", list_label,
                                                  pg.Color("black"))
                TextRect.bottomleft = (450, y) 

                self.screen.blit(TextSurf, TextRect)

                TextSurf, TextRect = text_objects(str(format(item[1],'.2f')), list_label,
                                                  pg.Color("black"))
                TextRect.bottomright = (510, y) 

                self.screen.blit(TextSurf, TextRect)



                y+=50

            TextSurf, TextRect = text_objects(str(self.num_breakfasts), num_label,
                                              pg.Color("black"))
            TextRect.bottomright = (550, 322) 

            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(str(self.num_lunches), num_label,
                                              pg.Color("black"))
            TextRect.bottomright = (550, 372) 

            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(str(self.num_dinners), num_label,
                                              pg.Color("black"))
            TextRect.bottomright = (550, 422) 

            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(str(self.num_snacks), num_label,
                                              pg.Color("black"))
            TextRect.bottomright = (550, 472) 

            self.screen.blit(TextSurf, TextRect)

        if self.bought_items:
        
            TextSurf, TextRect = text_objects("Bought Items", current_label, pg.Color("black"))
            TextRect.center = (420, 250)
            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(self.label, list_label, pg.Color("black"))
            TextRect.center = (635, 290)
            self.screen.blit(TextSurf, TextRect)
            
            y = 320

            for item in self.grocery_list:
                TextSurf, TextRect = text_objects(item[0], list_label,
                                              pg.Color("black"))
                TextRect.bottomleft = (330, y) 

                self.screen.blit(TextSurf, TextRect)

                
                y+=50

            TextSurf, TextRect = text_objects(str(self.num_breakfasts), num_label,
                                              pg.Color("black"))
            TextRect.bottomright = (500, 322) 

            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(str(self.num_lunches), num_label,
                                              pg.Color("black"))
            TextRect.bottomright = (500, 372) 

            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(str(self.num_dinners), num_label,
                                              pg.Color("black"))
            TextRect.bottomright = (500, 422) 

            self.screen.blit(TextSurf, TextRect)

            TextSurf, TextRect = text_objects(str(self.num_snacks), num_label,
                                              pg.Color("black"))
            TextRect.bottomright = (500, 472) 

            self.screen.blit(TextSurf, TextRect)


        
        TextSurf, TextRect = text_objects("Breakfasts", ind_label,
                                          pg.Color("black"))
        TextRect.bottomleft = (95, 310) 

        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects(str(self.player.breakfast), ind_label,
                                          pg.Color("black"))
        TextRect.bottomright = (255, 310) 

        self.screen.blit(TextSurf, TextRect)
        

        TextSurf, TextRect = text_objects("Lunches", ind_label,
                                          pg.Color("black"))
        TextRect.bottomleft = (95, 340) 

        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects(str(self.player.lunch), ind_label,
                                          pg.Color("black"))
        TextRect.bottomright = (255, 340) 

        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Dinners", ind_label,
                                          pg.Color("black"))
        TextRect.bottomleft = (95, 370) 

        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects(str(self.player.dinner), ind_label,
                                          pg.Color("black"))
        TextRect.bottomright = (255, 370) 

        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Snacks", ind_label,
                                          pg.Color("black"))
        TextRect.bottomleft = (95, 400) 

        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects(str(self.player.snacks), ind_label,
                                          pg.Color("black"))
        TextRect.bottomright = (255, 400) 

        self.screen.blit(TextSurf, TextRect)

        
       


        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)

        self.grocery_sprites.draw(self.screen)
        cursor_AT(self.screen, True)
        pg.display.flip()

class Gear_Store:  
    def __init__(self, screen, player, hiker_funds, current_resupply):
        
        self.done = False
        self.clock = pg.time.Clock()
        self.screen = screen
        self.player = player
        self.current_resupply = current_resupply
        self.hiker_funds = hiker_funds
        self.blaze = pg.transform.scale(BLAZE, (25, 75))
        self.items_bought = False
        self.food_action_complete = False
        self.label = "Choose an action:"
        
        self.markup = 1
        self.num_breakfasts = 0
        self.num_lunches = 0
        self.num_dinners = 0
        self.num_snacks = 0
        self.gear_cost = 0
        self.gear_weight = 0

        self.box = []


        self.items_needed = self.player.player_stats.to_buy 



        self.show_cart = True
        self.bought_items = False
        
        self.waypoint_object = Waypoint(self.player.current_waypoint)
        
        self.guide_book = GuideBook(self.screen, self.waypoint_object, self.player.current_waypoint)

        self.mail_option = Mail_Option(1)
        self.mail_list = Mail_Options_List(self.screen, self.mail_option, self.player)
        self.qty_conv_tent = 0
        self.qty_lw_tent = 0
        self.qty_ul_tent = 0
        self.qty_tent_poles = 0
        self.qty_tape = 0
        self.qty_hiking_poles = 0
        self.qty_shoes = 0
        self.qty_socks = 0
        self.item_name = "Tent Poles"
        self.list_price = 25
        self.game_state = GameState.PLAYGAME
        

        if self.player.player_stats.entire_tent:
            self.item_name = "Tent Poles Included"
            self.list_price = 0
            self.item = (self.item_name,self.list_price)
        else:
            self.item_name = "Tent Poles"
            self.list_price = 25
            self.item = (self.item_name,self.list_price)
            
            

        self.shopping_list = [("4 lb Tent",100), ("2.5 lb Tent",250),("1.5 lb Tent",450),self.item,
                             ("Repair Tape", 5), ("Hiking Poles",50), ("Shoes", 120),
                              ("Socks", 10)]

       
        
        self.cart = [("4 lb Tent",self.qty_conv_tent, self.qty_conv_tent*100 ),
                     ("2.5 lb Tent",self.qty_lw_tent,self.qty_lw_tent * 250),
                     ("1.5 lb Tent",self.qty_ul_tent,self.qty_ul_tent * 450),
                     (self.item_name, self.qty_tent_poles,self.qty_tent_poles *self.list_price),
                     ("Repair Tape", self.qty_tape, self.qty_tape*5),
                     ("Hiking Poles", self.qty_hiking_poles, self.qty_hiking_poles*50),
                     ("Shoes", self.qty_shoes, self.qty_shoes * 120),
                     ("Socks", self.qty_socks, self.qty_socks * 10)]

        # Contains all sprites. Also put the button sprites into a
        # separate group in your own game.
        self.gear_sprites = pg.sprite.Group()

        self.tent_4lb = Button(
             450, 238, 110, 20, self.buy_conv_tent,
            pg.font.SysFont("franklingothicmedium",18),
            'Add to Cart', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        
        self.tent_2p5lb = Button(
             450, 268, 110, 20, self.buy_lightweight_tent,
            pg.font.SysFont("franklingothicmedium",18),
            'Add to Cart', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.tent_1p5lb = Button(
             450, 298, 110, 20, self.buy_ul_tent,
            pg.font.SysFont("franklingothicmedium",18),
            'Add to Cart', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.tent_poles = Button(
             450, 328, 110, 20, self.buy_tent_poles,
            pg.font.SysFont("franklingothicmedium",18),
            'Add to Cart', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.repair_tape = Button(
             450, 358, 110, 20, self.buy_repair_tape,
            pg.font.SysFont("franklingothicmedium",18),
            'Add to Cart', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.hiking_poles = Button(
             450, 388, 110, 20, self.buy_hiking_poles,
            pg.font.SysFont("franklingothicmedium",18),
            'Add to Cart', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.shoes = Button(
             450, 418, 110, 20, self.buy_shoes,
            pg.font.SysFont("franklingothicmedium",18),
            'Add to Cart', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        
        self.socks = Button(
             450, 448, 110, 20, self.buy_socks,
            pg.font.SysFont("franklingothicmedium",18),
            'Add to Cart', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

 
        self.guidebook_btn = Button(
            50, 525, 200, 50, self.show_guide,
            pg.font.SysFont("franklingothicheavy",24),
            'Guidebook', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.buy_btn = Button(
            665, 465, 75, 30, self.buy,
            pg.font.SysFont("franklingothicheavy",20),
            'Buy', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.clear_cart_btn = Button(
            585, 465, 75, 30, self.clear,
            pg.font.SysFont("franklingothicheavy",20),
            'Clear', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.done_shopping = Button(
            550, 525, 200, 50, self.done_shopping,
            pg.font.SysFont("franklingothicheavy",24),
            'Done Shopping', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)


       
        # Add the button sprites to the sprite group.
        
            
        self.gear_sprites.add(self.guidebook_btn, self.buy_btn, self.clear_cart_btn, self.done_shopping,
                                 self.tent_4lb, self.tent_2p5lb, self.tent_1p5lb,
                                 self.tent_poles, self.repair_tape, self.hiking_poles,
                                 self.shoes, self.socks)
        if self.player.player_stats.entire_tent:
            self.gear_sprites.remove(self.tent_poles)

    def cart_list(self):
        
        self.cart = [("4 lb Tent",self.qty_conv_tent, self.qty_conv_tent*100 ),
             ("2.5 lb Tent",self.qty_lw_tent,self.qty_lw_tent * 250),
             ("1.5 lb Tent",self.qty_ul_tent,self.qty_ul_tent * 450),
             (self.item_name,self.qty_tent_poles,self.qty_tent_poles *self.list_price),
             ("Repair Tape", self.qty_tape, self.qty_tape*5),
             ("Hiking Poles", self.qty_hiking_poles, self.qty_hiking_poles*50),
             ("Shoes", self.qty_shoes, self.qty_shoes * 120),
             ("Socks", self.qty_socks, self.qty_socks * 10)]

        
        
            

    def clear(self):
        self.qty_conv_tent = 0
        self.qty_lw_tent = 0
        self.qty_ul_tent = 0
        self.qty_tent_poles = 0
        self.qty_tape = 0
        self.qty_hiking_poles = 0
        self.qty_shoes = 0
        self.qty_socks = 0
        self.gear_weight = 0
        self.gear_cost = 0
        self.cart_list()
        

        
    def buy_conv_tent(self):
        if self.gear_cost + 100 <= self.player.hiker_funds.calculate_available():               
            self.gear_weight += 4
            self.gear_cost += 100
            self.qty_conv_tent += 1
            self.cart_list()

    def buy_lightweight_tent(self):
        if self.gear_cost + 250 <= self.player.hiker_funds.calculate_available(): 
            self.gear_weight += 2.5
            self.gear_cost += 250
            self.qty_lw_tent += 1
            self.cart_list()

    def buy_ul_tent(self):
        if self.gear_cost + 450 <= self.player.hiker_funds.calculate_available(): 
            self.gear_weight += 1.5
            self.gear_cost += 450
            self.qty_ul_tent += 1
            self.cart_list()

    def buy_tent_poles(self):
        if self.gear_cost + 25 <= self.player.hiker_funds.calculate_available(): 
            self.gear_weight += .5
            self.gear_cost += 25
            self.qty_tent_poles += 1
            self.cart_list()

    def buy_repair_tape(self):
        if self.gear_cost + 5 <= self.player.hiker_funds.calculate_available(): 
            self.gear_weight += .1
            self.gear_cost += 5
            self.qty_tape += 1
            self.cart_list()

    def buy_hiking_poles(self):
        if self.gear_cost + 50 <= self.player.hiker_funds.calculate_available(): 
            self.gear_weight += 1
            self.gear_cost += 50
            self.qty_hiking_poles += 1
            self.cart_list()

    def buy_shoes(self):
        if self.gear_cost + 120 <= self.player.hiker_funds.calculate_available(): 
            self.qty_shoes += 1
            self.gear_cost += 120
            self.cart_list()


    def buy_sleeping_pad(self):
        if self.gear_cost + 100 <= self.player.hiker_funds.calculate_available(): 
            self.gear_weight += 1
            self.gear_cost += 100
            self.qty_sleeping_pad += 1
            self.cart_list()


    def buy_socks(self):
        if self.gear_cost + 10 <= self.player.hiker_funds.calculate_available(): 
            self.qty_socks += 1
            self.gear_cost += 10
            self.cart_list()


    def show_guide(self):
        self.guide_book = GuideBook(self.screen, self.waypoint_object, self.player.current_waypoint)
        self.guide_book.done = False
        self.guide_book.run()
                                                                                                                                                                                                                                                                           
        

    def buy(self):

        if self.player.hiker_funds.calculate_available() >= self.gear_cost:
        
            
            if self.gear_cost > 0:
                cost = 0

                for item in self.cart:
                    cost += item[2]

                self.hiker_funds.gear_cost += cost
                self.gear_cost = 0

                if self.qty_conv_tent > 0 or self.qty_lw_tent > 0 or self.qty_ul_tent > 0:

                    if self.player.gear == "Conventional":
                        self.player.base_weight = 17
                        
                    elif self.player.gear == "Lightweight":
                        self.player.base_weight = 12.5

                    elif self.player.gear == "Ultralight":
                        self.player.base_weight = 7.5

                if self.qty_tent_poles > 0:
                    self.player.base_weight-= .5

                if self.qty_hiking_poles > 0:
                    self.player.base_weight-= 1

                self.player.base_weight += self.gear_weight

                needed = []

                if self.items_needed[0][1]:
                   if self.qty_conv_tent > 0 or self.qty_lw_tent > 0 or self.qty_ul_tent > 0:
                        self.items_needed[0] = ("Tent", False)

                        

                if self.items_needed[1][1]:
                    if self.qty_tent_poles > 0:
                        self.items_needed[1] = ("Tent Poles", False)

                        
                    

                if self.items_needed[2][1]:
                    if self.qty_tape > 0:
                        self.items_needed[2] = ("Repair Tape", False)

                        
                   
                if self.items_needed[3][1]:
                    if self.qty_hiking_poles > 0:
                        self.items_needed[3] = ("Hiking Poles", False)
                        self.player.player_stats.hiking_pole_adjust = 0
                        self.player.player_stats.hiking_pole_injury = 0
                        
                    
                if self.items_needed[4][1]:
                    if self.qty_shoes > 0:
                        self.items_needed[4] = ("Shoes", False)
                        self.player.player_stats.shoe_chance_injury = 0

                if self.items_needed[5][1]:
                    if self.qty_socks > 0:
                        self.items_needed[5] = ("Socks", False)
                        self.player.player_stats.sock_adjust = 0
                        self.player.player_stats.sock_injury = 0
                    

                self.gear_weight = 0

                self.qty_conv_tent = 0
                self.qty_lw_tent = 0
                self.qty_ul_tent = 0
                self.qty_tent_poles = 0
                self.qty_tape = 0
                self.qty_hiking_poles = 0
                self.qty_shoes = 0
                self.qty_socks = 0

                self.cart_list()

                self.player.player_stats.to_buy = self.items_needed
                self.player.player_stats.update_shelter_only_status()
                self.player.player_stats.update_energy_percentage()
                self.player.player_stats.update_chance_injury()


        else:

            print("Insuffient FUnds")

    def done_shopping(self):
            self.done = True

    def run(self):
        while not self.done:
            self.screen.fill((100,100,100))
            self.dt = self.clock.tick(30) / 1000
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                pg.quit()
                quit()
                
            for button in self.gear_sprites:
                button.handle_event(event)

    def run_logic(self):

        self.gear_sprites.update(self.dt)

    def draw(self):

        title1 = drop_shadow_text("Shop Gear",
             "impact", 70, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title1, center_of_surface(title1, 400, 65))
        self.screen.blit(self.blaze, (50,28))
        self.screen.blit(self.blaze, (725,28))
        green  = pg.transform.scale(GREEN,(175,36))
        blue  = pg.transform.scale(CLOUD,(175,36))
        

        pg.draw.rect(self.screen, pg.Color("white"),(50, 120, 700, 385))
        self.screen.blit(green,(50,120))
        self.screen.blit(blue,(225,120))
        self.screen.blit(green,(400,120))
        self.screen.blit(blue,(575,120))
        
        pg.draw.rect(self.screen, pg.Color("black"),(50, 120, 700, 385),2)
        
        pg.draw.line(self.screen, pg.Color("black"),(224,120), (224,505), 2)
        pg.draw.line(self.screen, pg.Color("black"),(399,120), (399,215), 2)
        pg.draw.line(self.screen, pg.Color("black"),(574,120), (574,505), 2)
##        pg.draw.line(self.screen, pg.Color("black"),(260,216), (260,505), 2)

        
        pg.draw.line(self.screen, pg.Color("black"),(50,156), (750,156), 2)
        pg.draw.line(self.screen, pg.Color("black"),(50,216), (750,216), 2)
 

##        pg.draw.line(self.screen, pg.Color("black"),(50,348), (225,348), 2)


        label = pg.font.SysFont("impact", 22)
        TextSurf, TextRect = text_objects("Available Funds", label, pg.Color("black"))
        TextRect.center = (137, 138)
        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Pack Weight", label, pg.Color("black"))
        TextRect.center = (312, 138)
        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Cart Total", label, pg.Color("black"))
        TextRect.center = (662, 138)
        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Gear Weight", label, pg.Color("black"))
        TextRect.center = (487, 138)
        self.screen.blit(TextSurf, TextRect)

        amount_label = pg.font.SysFont("impact", 28)
        TextSurf, TextRect = text_objects("$ " + str(format(self.hiker_funds.calculate_available(), '.2f')),
                                          amount_label, pg.Color("black"))
        TextRect.center = (137, 185)
        self.screen.blit(TextSurf, TextRect)


        TextSurf, TextRect = text_objects(str(format(self.player.calculate_Packweight() ,'.1f') + " LBS"),
                                          amount_label, pg.Color("black"))
        TextRect.center = (312, 185)
        self.screen.blit(TextSurf, TextRect)

   
        TextSurf, TextRect = text_objects("$ " + format(self.gear_cost, '.2f'),
                                          amount_label, pg.Color("black"))
        TextRect.center = (662, 185)
        self.screen.blit(TextSurf, TextRect)


        TextSurf, TextRect = text_objects(str(format(self.gear_weight ,'.1f') + " LBS"),
                                          amount_label, pg.Color("black"))
        TextRect.center = (487, 185)
        self.screen.blit(TextSurf, TextRect)

        current_label = pg.font.SysFont("impact", 26)
        ind_label = pg.font.SysFont("consolas", 22)
        list_label = pg.font.SysFont("consolas", 18)
        num_label = pg.font.SysFont("impact", 24)

        TextSurf, TextRect = text_objects("Shopping List", current_label, pg.Color("black"))
        TextRect.center = (137, 240)
        self.screen.blit(TextSurf, TextRect)

        TextSurf, TextRect = text_objects("Cart", current_label, pg.Color("black"))
        TextRect.center = (662, 240)
        self.screen.blit(TextSurf, TextRect)

        if self.show_cart:
        
##            TextSurf, TextRect = text_objects("Shopping Cart", current_label, pg.Color("black"))
##            TextRect.center = (450, 250)
##            self.screen.blit(TextSurf, TextRect)
            y = 260

            for item in self.shopping_list:
              
                TextSurf, TextRect = text_objects(item[0], list_label,
                                              pg.Color("black"))
                TextRect.bottomleft = (245, y) 

                self.screen.blit(TextSurf, TextRect)

                if item[1] != 0:

                    TextSurf, TextRect = text_objects("$", list_label,
                                                      pg.Color("black"))
                    TextRect.bottomleft = (385, y) 

                    self.screen.blit(TextSurf, TextRect)

                    TextSurf, TextRect = text_objects(str(format(item[1],'.0f')), list_label,
                                                      pg.Color("black"))
                    TextRect.bottomright = (440, y) 

                    self.screen.blit(TextSurf, TextRect)



                y+=30


        list_y = 280
        
        for item in self.items_needed:
            if item[1]:
                TextSurf, TextRect = text_objects(item[0], ind_label, pg.Color("black"))
                TextRect.center = (140, list_y) 

                self.screen.blit(TextSurf, TextRect)

                list_y += 30

        cart_y = 280
        cart_label = pg.font.SysFont("consolas", 18)



        for item in self.cart:

            if item[1] > 0:
                TextSurf, TextRect = text_objects(item[0], cart_label,
                                              pg.Color("black"))
                TextRect.bottomleft = (585, cart_y) 

                self.screen.blit(TextSurf, TextRect)



                TextSurf, TextRect = text_objects(str(format(item[1],'.0f')), cart_label,
                                                  pg.Color("black"))
                TextRect.bottomright = (735, cart_y) 

                self.screen.blit(TextSurf, TextRect)

                cart_y+=22

        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)

        self.gear_sprites.draw(self.screen)
        cursor_AT(self.screen, True)
        pg.display.flip()

class SleepDisplayTown:

    def __init__(self, screen, waypoint_object):
        self.screen = screen
        self.waypoint_object = waypoint_object
        self.type_of = ""
        self.frameImage = pg.transform.scale(pg.image.load(resource_path("images/picframe.png")),
                                               (430, 355))
        self.hostelImage = pg.transform.scale(pg.image.load(resource_path("images/hostelnight.png")),
                                               (400, 275))
        self.hostelZeroImage = pg.transform.scale(pg.image.load(resource_path("images/hostelzero.png")),
                                               (400, 275))

        self.hotelImage = pg.transform.scale(pg.image.load(resource_path("images/hotelnight.png")),
                                               (400, 275))
        self.hotelZeroImage = pg.transform.scale(pg.image.load(resource_path("images/hotelzero.png")),
                                               (400, 275))

        self.campImage = pg.transform.scale(pg.image.load(resource_path("images/campnight.png")),
                                               (400, 275))
        self.campZeroImage = pg.transform.scale(pg.image.load(resource_path("images/campzero.png")),
                                               (400, 275))

        self.displayImage = pg.transform.scale(pg.image.load(resource_path("images/hostelnight.png")),
                                               (400, 275))
        
        
##        self.update_delay = 1000
##        self.last_update = pg.time.get_ticks()
##        self.count = 0
##        self.status = "Sleeping"


    def update(self, type_of):
##        self.count = 0
        self.type_of = type_of
##        print(self.waypoint_object.category)

        if self.type_of == "Hostel":
            self.displayImage = self.hostelImage
        elif self.type_of == "Hostel Zero":
            self.displayImage = self.hostelZeroImage
        elif self.type_of == "Hotel":
            self.displayImage = self.hotelImage
        elif self.type_of == "Hotel Zero":
            self.displayImage = self.hotelZeroImage
        elif self.type_of == "Camp":
            self.displayImage = self.campImage
        elif self.type_of == "Camp Zero":
            self.displayImage = self.campZeroImage

    def draw(self):
        self.screen.blit(self.displayImage,(246,153))
        self.screen.blit(self.frameImage,(227,135))
        


class Random_MailDrop:
    def __init__(self):
        self.amounts = (0,0, 20, 0,0, 30, 0,0, 40, 0,0, 50, 0,0, 60, 0,0, 70, 0,0, 80, 0,0, 90,0, 0, 100,0, 0)
        self.person_list = ("Friend", "Aunt", "Uncle", "Mom", "Dad", "Grandmother", "Grandfather",
                       "Cousin", "Former Co-worker", "Neighbor", "Facebook Friend")
        self.index = random.randint(1,29)
        self.person = random.randint(1,11)
        self.drop = [self.person_list[self.person-1], self.amounts[self.index-1]]   

class Hiker_Funds:
    def __init__(self):
        self.funds = 0
        self.gifts = 0
        self.gear_cost = 0
        self.food_cost = 0
        self.lodging_costs = 0
        self.shuttle_costs = 0
        self.other_costs = 0
        self.available = 0

    def calculate_available(self):
        self.available = self.funds - self.gear_cost - self.food_cost - self.lodging_costs -\
                         self.shuttle_costs - self.other_costs + self.gifts
        return self.available

class Resupply_Options:
    """Resupply Options at Waypoint"""
    def __init__(self, key):
        self.dictionary = get_resupply_options()
        self.key = str(key)
        self.id_num = self.dictionary[self.key]['id_num']
        self.mile = self.dictionary[self.key]['mile']
        self.description = self.dictionary[self.key]['description']
        self.category = self.dictionary[self.key]['category']
        self.distance = self.dictionary[self.key]['distance']                     
        self.post_office = self.dictionary[self.key]['post_office']                                 
        self.actions = self.dictionary[self.key]['actions']
        self.food_markup = self.dictionary[self.key]['food_markup']
        self.camp_price = self.dictionary[self.key]['camp_price']
        self.hostel_price = self.dictionary[self.key]['hostel_price']                     
        self.hotel_price = self.dictionary[self.key]['hotel_price']                                 
        self.mail_Sunday = self.dictionary[self.key]['mail_Sunday']
        self.zero = self.dictionary[self.key]['zero']                                 
        self.gear_store = self.dictionary[self.key]['gear_store']                                  
    



class Transport_Display:

    def __init__(self, screen, waypoint_object, player):
        self.screen = screen
        self.waypoint_object = waypoint_object
        self.player = player
        self.frameImage = pg.transform.scale(pg.image.load(resource_path("images/picframe.png")),
                                               (430, 356))
        self.type_of = ""
        self.comment = ""

        self.walktoImage = pg.transform.scale(pg.image.load(resource_path("images/hitch_walk_to.png")),
                                               (400, 275))
        self.hitchtoImage = pg.transform.scale(pg.image.load(resource_path("images/hitch_truck_to.png")),
                                               (400, 275))
        self.shuttletoImage = pg.transform.scale(pg.image.load(resource_path("images/hitch_shuttle_to.png")),
                                               (400, 275))

        self.walkfromImage = pg.transform.scale(pg.image.load(resource_path("images/hitch_walk_from.png")),
                                               (400, 275))
        self.hitchfromImage = pg.transform.scale(pg.image.load(resource_path("images/hitch_truck_from.png")),
                                               (400, 275))
        self.shuttlefromImage = pg.transform.scale(pg.image.load(resource_path("images/hitch_shuttle_from.png")),
                                               (400, 275))


        self.displayImage = pg.transform.scale(pg.image.load(resource_path("images/hitch_walk_from.png")),
                                               (400, 275))
        

    def update(self, waypoint_object, type_of):
        self.waypoint_object = waypoint_object
##        self.count = 0
        self.type_of = type_of
##        print(self.waypoint_object.category)

        if self.type_of == "Walk To":
            self.displayImage = self.walktoImage
            self.comment = "Heading To Town!"
        elif self.type_of == "Hitch To":
            self.displayImage = self.hitchtoImage
            self.comment = "Heading To Town!"
        elif self.type_of == "Shuttle To":
            self.displayImage = self.shuttletoImage
            self.comment = "Heading To Town!"
        elif self.type_of == "Walk From":
            self.displayImage = self.walkfromImage
            self.comment = "Heading Back to the Trail!"
        elif self.type_of == "Hitch From":
            self.displayImage = self.hitchfromImage
            self.comment = "Heading Back to the Trail!"
        elif self.type_of == "Shuttle From":
            self.displayImage = self.shuttlefromImage
            self.comment = "Heading Back to the Trail!"


    def draw(self):
        self.screen.blit(self.displayImage,(246,153))
        self.screen.blit(self.frameImage,(227,135))
        small_label = pg.font.SysFont("franklingothicheavy", 18)

        TextSurf, TextRect = text_objects(self.comment, small_label, pg.Color("black"))
        TextRect.center = (442, 468)
        self.screen.blit(TextSurf, TextRect)


    
