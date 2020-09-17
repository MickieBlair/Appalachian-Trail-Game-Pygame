import pygame as pg
from functions import *  
from constants import *
from classes import *
from enum import Enum
import datetime as date
from datajson import *
import pickle



class Game:
    def __init__(self, screen, player):
        self.screen = screen

        
        self.player = player
        self.status = self.player.status
       
        self.done = False
        
        self.clock = pg.time.Clock()
        
        self.game_state = GameState.PLAYGAME        

        self.hiker = Hiker()
        self.hiker_group = pg.sprite.Group(self.hiker)
        self.still_hiker= pg.transform.scale(pg.image.load(resource_path('images/walk/still_1.png')),(80, 80))
        self.no_camping = pg.transform.scale(pg.image.load(resource_path('images/no_camping.png')),(400, 275))
        self.background = pg.transform.scale(pg.image.load(resource_path('images/background.png')),(430, 110))
        self.night_background= pg.transform.scale(pg.image.load(resource_path('images/night_background.png')),(430, 110))

        
        self.pause_sprite = False
        self.speed_image= AVERAGE_IMAGE
        
        self.all_sprites = pg.sprite.Group()
        self.waypoint_action_sprites = pg.sprite.Group()
        self.food_sprites = pg.sprite.Group()
        self.random_event_sprites = pg.sprite.Group()
        self.water_event_sprites = pg.sprite.Group()

        self.date_display= DateDisplay(self.screen, self.player)
        self.status_bar = StatusBar(self.screen, self.player)

        self.mile_counter = MileageCounter(self.screen, self.player)
        self.mile_counter_paused = True

        self.currentWaypoint = self.player.current_waypoint

        self.waypoint_object = Waypoint(self.currentWaypoint)
        self.guide_book = GuideBook(self.screen, self.waypoint_object, self.currentWaypoint)

        if self.player.mile == 0:            
            self.player.mile = self.waypoint_object.mile
            
        self.number_of_waypoints = len(self.waypoint_object.dictionary)
        
        self.waypoint_display = WaypointDisplay(self.screen,
                                                self.waypoint_object,
                                                 self.player,
                                                self.mile_counter)

        
        self.next_resupply = Next_Resupply_Waypoint(self.player, self.waypoint_object)
        self.next_water = Next_Water_Waypoint(self.player, self.waypoint_object)
        self.next_camping = Next_Camping_Waypoint(self.player, self.waypoint_object)
        self.sign_display = Sign(self.screen, self.player, self.next_resupply,
                                 self.next_water, self.next_camping)
        self.mile_counter.sign = self.sign_display

        self.mile_display = MileDisplay(self.screen, self.player)

        self.map_display = DisplayMap(self.screen)
        self.eat_display = DisplayEat(self.screen, self.player)

        self.random_trail_image = RandomTrailImage(self.screen, self.player.current_month)
        self.display_random_trail = False

        self.sleep_display = SleepDisplay(self.screen, self.waypoint_object)
        self.sleep_display_showing = False

        self.sleep_delay = 1000
        self.sleep_update = pg.time.get_ticks()
        self.sleep_count = 0
        self.cost = 0.00

        if self.player.random_events == None:
            self.random_events = Random_Events()
            self.player.random_events = self.random_events
        else:
            self.random_events = self.player.random_events
        
        self.random_event_showing = False
        self.random_event_display = None

        self.show_waypoint_actions = True

        self.to_town_showing = False
        self.to_town_display = Transport_Display(self.screen, self.waypoint_object, self.player)
        
        self.to_town_delay = 1000
        self.town_update = pg.time.get_ticks()
        self.town_count = 0
        self.walking = False

        self.hydration_event_showing = False
        self.hydration_event_display = Hydration_Event_Display(self.screen,
                                                                 self.waypoint_object,
                                                                 self.player,
                                                                 self.random_events)

        self.prior_status = ""

        self.quit_button = Button(
            15, 549, 200, 37, self.quit_game,
            pg.font.SysFont("franklingothicheavy",24),
            'Save and Exit', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.start_hike = Button(
            354, 515, 175, 45, self.start_game,
            pg.font.SysFont("franklingothicheavy",22),
            'Start Hiking', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.map_btn = Button(
            667, 195, 120, 50, self.show_map,
            pg.font.SysFont("franklingothicheavy",22),
            'Map', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.guidebook_btn = Button(
            667, 30, 120, 50, self.show_guide,
            pg.font.SysFont("franklingothicheavy",20),
            'Guidebook', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.speed_btn = Button(
            667, 355, 120, 50, self.game_speed,
            pg.font.SysFont("franklingothicheavy",22),
            'Speed  ', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.increase_speed = Button(
             763, 357, 23, 23, self.increase,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),UP_NORMAL, UP_HOVER,UP_DOWN)

        self.decrease_speed = Button(
            763, 381, 23, 23, self.decrease,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),DOWN_NORMAL,DOWN_HOVER,DOWN_DOWN)


        self.eat_btn = Button(
           667, 515, 120, 50, self.eat,
            pg.font.SysFont("franklingothicheavy",22),
            'Eat', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)



        self.next_btn = Button(
                354, 542, 175, 45, self.next_waypoint,
                pg.font.SysFont("franklingothicheavy",22),
                'Keep Hiking', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)



        self.resupply_btn = Button(
            867, 297, 120, 50, self.resupply,
            pg.font.SysFont("franklingothicheavy",22),
            'Resupply', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.camp_btn = Button(
            340, 534, 100, 50, self.camp,
            pg.font.SysFont("franklingothicheavy",18),
            'Stop Here', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.refill_btn = Button(
            235, 534, 100, 50, self.refill,
            pg.font.SysFont("franklingothicheavy",18),
            'Refill Water', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.breakfast_btn =Button(
            667, 435, 120, 35, self.eat_breakfast,
            pg.font.SysFont("franklingothicheavy",20),
            'Breakfast', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.lunch_btn = Button(
            667, 475, 120, 35, self.eat_lunch,
            pg.font.SysFont("franklingothicheavy",20),
            'Lunch', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.dinner_btn = Button(
            667, 515, 120, 35, self.eat_dinner,
            pg.font.SysFont("franklingothicheavy",20),
            'Dinner', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.snack_btn = Button(
            667, 555, 120, 35, self.eat_snack,
            pg.font.SysFont("franklingothicheavy",20),
            'Snack', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.hitch_btn = Button(
                265, 492, 350, 45, self.hitch,
                pg.font.SysFont("franklingothicheavy",20),
                'Try to Hitch ', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.walk_btn = Button(
                290, 492, 150, 45, self.walk,
                pg.font.SysFont("franklingothicheavy",20),
                'Walk To Town', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.shuttle_btn = Button(
                450, 492, 150, 45, self.shuttle,
                pg.font.SysFont("franklingothicheavy",20),
                'Call Shuttle', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.take_shuttle_btn = Button(
                450, 492, 150, 45, self.take_shuttle,
                pg.font.SysFont("franklingothicheavy",20),
                'Take Shuttle', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.take_hitch_btn = Button(
                450, 492, 150, 45, self.take_hitch,
                pg.font.SysFont("franklingothicheavy",20),
                'Accept Hitch', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.close_random_btn = Button(
                354, 500, 175, 45, self.close_random,
                pg.font.SysFont("franklingothicheavy",20),
                'OK', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.close_water_btn = Button(
                354, 435, 175, 45, self.close_water,
                pg.font.SysFont("franklingothicheavy",20),
                'OK', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.all_sprites.add(self.quit_button,
                             self.map_btn,
                             self.guidebook_btn,                             
                             self.eat_btn,
                             self.speed_btn,
                             self.increase_speed,
                             self.decrease_speed)

        

        self.saved_game_status()

        

    def saved_game_status(self):
        

        if self.status == "Start":
            self.all_sprites.add(self.start_hike)
        elif self.status == "Hiking":
            self.action_sprite_logic()
            

        elif self.status == "Sleeping":
            self.sleep_display.update(self.waypoint_object)
            self.sleep_display_showing = True
            self.waypoint_action_sprites.empty()
            self.waypoint_display.update(self.waypoint_object)

        elif self.status == "To Trail":
            self.status = "Hiking"
            self.player.status = "Trail"
            self.waypoint_display.update(self.waypoint_object)
            self.action_sprite_logic()

        elif self.status == "To Town":
            self.walking = False                        
            self.to_town_display.update(self.waypoint_object, "Hitch To")
            self.to_town_showing = True
            self.waypoint_action_sprites.empty()
            
        self.player.player_stats.player_health()   
        

        
            



    def quit_game(self):
        self.save_game()
        self.done = True
        self.game_state = GameState.QUIT

    def save_game(self):        
        player_object = self.player
        picklefile = open('player_object', 'wb')
        pickle.dump(player_object, picklefile)
        picklefile.close()
        


    def camp(self):
        
        if self.player.player_stats.shelters_only and self.waypoint_object.category =="Campsite":
            self.waypoint_object.comment = "No Camping"
            
            
        
        elif self.pause_sprite and not self.random_event_showing:
            self.show_waypoint_actions = False
            self.close_eat()
            self.close_map()

            #print("self.player.player_stats.camp_occurences", self.player.player_stats.camp_occurences)

            self.waypoint_action_sprites.empty()
            self.random_event_sprites.add(self.close_random_btn)

            
            self.status  = "Sleeping"
            
            self.sleep_display.update(self.waypoint_object)
            self.sleep_display_showing = True
            self.waypoint_action_sprites.empty()
            self.player.player_stats.camp_choice = ""

            #chance of event = 20%
            random_number = random.random()



            if random_number < .20 and self.player.player_stats.camp_occurences < 4:

                self.player.player_stats.camp_occurences +=1                             

                self.random_event_display = Random_Event_Display(self.screen,
                                                                 self.waypoint_object,
                                                                 self.player,
                                                                 self.random_events, "Camp")

                
            
        self.save_game()

    def next_waypoint(self):       
        if self.pause_sprite and not self.random_event_showing:
            self.show_waypoint_actions = True
            self.status = "Hiking"
            
            self.walking = False
            self.random_event_display = None
            self.close_eat()
            self.close_map()
            self.random_event_showing = False
            self.mile_counter.pause("True") #set back to running
            
            if self.currentWaypoint < self.number_of_waypoints:
                
                if self.player.mile == self.waypoint_object.mile:
                    
                    self.currentWaypoint += 1
                    self.player.current_waypoint = self.currentWaypoint

                    self.waypoint_object = Waypoint(self.currentWaypoint)

                    if self.currentWaypoint == self.player.player_stats.exemption_ends+1:
                        self.player.player_stats.energy_exempt = False

                    if self.player.player_stats.shelters_only and self.waypoint_object.category =="Campsite":
                        self.waypoint_object.comment = "No Camping"

                    self.waypoint_display.update(self.waypoint_object)
                    
                    self.random_trail_image.pickRandom()
                    

                    if self.currentWaypoint in self.random_events.event_list:
                        #print("YES IN LIST")
                        if self.waypoint_object.category =="Road" or self.waypoint_object.category =="Resupply":
                            #print("YES ROAD OR RESUPPLY")
                            self.random_event_display = Random_Event_Display(self.screen,
                                                                             self.waypoint_object,
                                                                             self.player,
                                                                             self.random_events, "Road Magic")
                            self.random_event_showing = True
                            self.waypoint_action_sprites.empty()
                            self.random_event_sprites.add(self.close_random_btn)

                        elif self.waypoint_object.type == "shoes":
                            self.random_event_display = Random_Event_Display(self.screen,
                                                                             self.waypoint_object,
                                                                             self.player,
                                                                             self.random_events, "Shoes")
                            self.random_event_showing = True
                            self.waypoint_action_sprites.empty()
                            self.random_event_sprites.add(self.close_random_btn)

                        elif self.waypoint_object.category !="Campsite" and self.waypoint_object.category !="Shelter":
                            self.random_event_display = Random_Event_Display(self.screen,
                                                                             self.waypoint_object,
                                                                             self.player,
                                                                             self.random_events,"Other")
                            self.random_event_showing = True
                            self.waypoint_action_sprites.empty()
                            self.random_event_sprites.add(self.close_random_btn)

                     #self.player.player_stats.chance_injury      
                    elif self.player.player_stats.health_status == "Healthy" and random.random() < self.player.player_stats.chance_injury\
                           and self.player.player_stats.injury_event_occurences < 5 and self.waypoint_object.type != "shoes" and\
                           self.waypoint_object.category !="Campsite" and self.waypoint_object.category !="Shelter"\
                           and self.waypoint_object.category !="Road" and self.waypoint_object.category !="Road"\
                           and self.waypoint_object.category !="Terminus":
                            self.player.player_stats.injury_event_occurences +=1 
                            self.random_event_display = Random_Event_Display(self.screen,
                                                                             self.waypoint_object,
                                                                             self.player,
                                                                             self.random_events, "Injury")
                            self.random_event_display.injury_event = True
                            self.random_event_showing = True
                            self.waypoint_action_sprites.empty()
                            self.random_event_sprites.add(self.close_random_btn) 

                    else:
                        self.action_sprite_logic()
        self.save_game()

    def current_state(self):
        return self.game_state

    def close_random(self):
        if self.pause_sprite and self.random_event_showing:
            self.random_event_showing = False
            self.random_event_sprites.empty()
            self.action_sprite_logic()

    def take_hitch(self):
        
        if self.pause_sprite and not self.random_event_showing:
            self.close_eat()
            self.close_map()
            self.walking = False
            self.status  = "To Town"
            
            self.to_town_display.update(self.waypoint_object, "Hitch To")
            self.to_town_showing = True
            self.waypoint_action_sprites.empty()
            self.save_game()

    def hitch(self):
        if self.pause_sprite and not self.random_event_showing:
            self.walking = False
            status =random.randint(1,2)
            if status == 1:
                self.waypoint_object.comment = "Ride Found."
                self.waypoint_display.update(self.waypoint_object)
                self.waypoint_action_sprites.empty()
                self.walk_btn = Button(
                    290, 492, 150, 45, self.walk,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Walk To Town', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
                
                self.waypoint_action_sprites.add(self.next_btn, self.walk_btn, self.take_hitch_btn)
            
            elif status == 2:
                self.waypoint_object.comment = "Could not get a ride."
                self.waypoint_display.update(self.waypoint_object)
                self.waypoint_action_sprites.empty()
                self.walk_btn = Button(
                    290, 492, 150, 45, self.walk,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Walk To Town', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

                self.shuttle_btn = Button(
                    450, 492, 150, 45, self.shuttle,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Call Shuttle', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
                self.waypoint_action_sprites.add(self.next_btn, self.walk_btn, self.shuttle_btn)
        

    def walk(self):
        if self.pause_sprite and not self.random_event_showing:
            self.close_eat()
            self.close_map()

            self.status  = "To Town"
            
            self.to_town_display.update(self.waypoint_object, "Walk To")
            self.to_town_showing = True
            self.waypoint_action_sprites.empty()
            self.walking = True
            self.save_game()

    def take_shuttle(self):
        if self.pause_sprite and not self.random_event_showing:
            self.walking = False
            self.player.hiker_funds.shuttle_costs += self.cost
            self.close_eat()
            self.close_map()

            self.status  = "To Town"
             
            self.to_town_display.update(self.waypoint_object, "Shuttle To")
            self.to_town_showing = True
            self.waypoint_action_sprites.empty()
            self.save_game()
                

    def shuttle(self):
        if self.pause_sprite and not self.random_event_showing:
            self.walking = False
            status =random.randint(1,2)
            if status == 1:
                
                shuttle_costs = [5, 10, 15, 20]
                cost = random.randint(1,4)
                self.cost =  shuttle_costs[cost-1]         
                cost_format = format(self.cost,'.2f')
                self.waypoint_object.comment = "Shuttle Available - Cost = $ " + cost_format
                self.waypoint_display.update(self.waypoint_object)
                self.waypoint_action_sprites.empty()

            self.walk_btn = Button(
                    290, 492, 150, 45, self.walk,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Walk To Town', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

            self.take_shuttle_btn = Button(
                    450, 492, 150, 45, self.take_shuttle,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Take Shuttle', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

                
            self.waypoint_action_sprites.add(self.next_btn, self.walk_btn, self.take_shuttle_btn)
                
            if status == 2:
                self.waypoint_object.comment = "No cell signal."
                self.waypoint_display.update(self.waypoint_object)
                self.waypoint_action_sprites.empty()
                self.walk_btn = Button(
                    354, 492, 175, 45, self.walk,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Walk To Town', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
                
                
                self.waypoint_action_sprites.add(self.next_btn, self.walk_btn)

                

    def action_sprite_logic(self):
        
        self.waypoint_action_sprites.empty()

        self.next_btn = Button(
                354, 542, 175, 45, self.next_waypoint,
                pg.font.SysFont("franklingothicheavy",22),
                'Keep Hiking', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.waypoint_action_sprites.add(self.next_btn)
        
        if self.show_waypoint_actions:
            if self.waypoint_object.actions == "water":
                self.refill_btn = Button(
                    375, 492, 135, 45, self.refill,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Refill Water', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)            
                self.waypoint_action_sprites.add(self.refill_btn)

            if self.waypoint_object.actions == "sleep":            
                self.camp_btn = Button(
                    375, 492, 135, 45, self.camp,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Sleep Here', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)            
                self.waypoint_action_sprites.add(self.camp_btn)

            if self.waypoint_object.actions == "sleep, water":
                self.refill_btn = Button(
                    300, 492, 135, 45, self.refill,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Refill Water', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)

                self.camp_btn = Button(
                    440, 492, 135, 45, self.camp,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Sleep Here', pg.Color("white"),WOOD_BTN, WOOD_BTN, WOOD_BTN)
            
                self.waypoint_action_sprites.add(self.refill_btn, self.camp_btn)

            if self.waypoint_object.type == "trail":
                self.resupply_btn = Button(
                    265, 492, 350, 45, self.resupply,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Enter ' + self.waypoint_object.resupply_options, pg.Color("white"),
                    WOOD_BTN, WOOD_BTN, WOOD_BTN)            
                self.waypoint_action_sprites.add(self.resupply_btn)

            if self.waypoint_object.type == "town":
                self.hitch_btn = Button(
                    265, 492, 350, 45, self.hitch,
                    pg.font.SysFont("franklingothicheavy",20),
                    'Hitch to ' + self.waypoint_object.resupply_options, pg.Color("white"),
                    WOOD_BTN, WOOD_BTN, WOOD_BTN)
                self.waypoint_action_sprites.add(self.hitch_btn)


    def show_guide(self):
        
        self.close_eat()
        self.close_map()
        self.guide_book = GuideBook(self.screen, self.waypoint_object, self.currentWaypoint)
        self.guide_book.done = False
        self.guide_book.run()


    def resupply(self):

        #print("game status", self.status)

        if not self.display_random_trail:

            
            resupply = Resupply(self.screen, self.player, self.waypoint_object,
                                self.currentWaypoint, self.sign_display)
            resupply.shuttle_cost = self.cost            
            resupply.run()

           

        self.status = "Hiking"
        self.game_state = resupply.game_state
        if self.game_state == GameState.QUIT:
            self.done = True
        
         
        self.walking = False
        self.waypoint_object.comment = "Let's get walking!"
        self.waypoint_display.update(self.waypoint_object)        
        self.action_sprite_logic()      

    def refill(self):
        if self.pause_sprite and not self.random_event_showing:
            self.close_eat()
            self.close_map()
            self.player.player_stats.out_of_water = False
            self.player.player_stats.water_warning_acknowledged = False
            self.player.player_stats.player_health()
            if self.player.liters < 4.0:
                self.player.liters += 0.5
            self.save_game()

    def start_game(self):
        self.close_eat()
        self.close_map()        
        self.waypoint_display.update(self.waypoint_object)
        self.all_sprites.remove(self.start_hike)
        self.status = "Hiking"
         
        self.action_sprite_logic()
        self.save_game()

        

    def show_map(self):
        self.close_eat() 
        self.all_sprites.empty()
        
        close_btn = Button(
            761, 4, 28, 28, self.close_map,
            pg.font.SysFont("franklingothicmedium",20),
            '', pg.Color("white"),pg.transform.scale(CLOSE_NORMAL, (30, 30)),
            pg.transform.scale(CLOSE_HOVER, (30, 30)),
            pg.transform.scale(CLOSE_DOWN, (30, 30)))

        self.all_sprites.add(self.quit_button,
                             close_btn)
        
        self.map_display.done = False

        

    def close_map(self):
        self.all_sprites.empty()
        self.map_display.done = True
        
        self.all_sprites.add(self.quit_button,
                             self.guidebook_btn,
                             self.map_btn,
                             self.speed_btn,
                             self.eat_btn,
                             self.increase_speed,
                             self.decrease_speed)

        if self.status == "Start":
            self.all_sprites.add(self.start_hike)

        if self.status == "Hiking":
            if not self.random_event_showing:
                self.action_sprite_logic()

        

    def eat(self):        
        if not self.random_event_showing:

            self.all_sprites.remove(self.eat_btn)

            self.food_sprites.add(self.breakfast_btn, self.lunch_btn, self.dinner_btn,
                                  self.snack_btn)
            
            close_btn = Button(
                770, 405, 28, 28, self.close_eat,
                pg.font.SysFont("franklingothicmedium",20),
                '', pg.Color("white"),pg.transform.scale(CLOSE_NORMAL, (30, 30)),
                pg.transform.scale(CLOSE_HOVER, (30, 30)),
                pg.transform.scale(CLOSE_DOWN, (30, 30)))

            self.all_sprites.add(self.quit_button,
                                 close_btn)
            
            self.eat_display.done = False

    def close_eat(self):
        self.all_sprites.empty()
        self.food_sprites.empty()
        self.eat_display.done = True

        
        self.all_sprites.add(self.quit_button,
                             self.guidebook_btn,
                             self.map_btn,
                             self.speed_btn,
                             self.eat_btn,
                             self.increase_speed,
                             self.decrease_speed)

        if self.status == "Start":
            self.all_sprites.add(self.start_hike)

        if self.status == "Hiking":
            if not self.random_event_showing:
                self.action_sprite_logic()

        

    def eat_breakfast(self):
        breakfast_energy = 20
        if self.player.breakfast > 0:
            self.player.breakfast -= 1
            if self.player.player_stats.energy < 100 - breakfast_energy:
                self.player.player_stats.energy += breakfast_energy
            else:
                self.player.player_stats.energy = 100
        self.close_eat()
        self.save_game()

    def eat_lunch(self):
        lunch_energy = 20
        if self.player.lunch > 0:
            self.player.lunch -= 1
            if self.player.player_stats.energy < 100 - lunch_energy:
                self.player.player_stats.energy += lunch_energy
            else:
                self.player.player_stats.energy = 100
        self.close_eat()
        self.save_game()

    def eat_dinner(self):
        dinner_energy = 20
        if self.player.dinner > 0:
            self.player.dinner -= 1
            if self.player.player_stats.energy < 100 - dinner_energy:
                self.player.player_stats.energy += dinner_energy
            else:
                self.player.player_stats.energy = 100
        self.close_eat()
        self.save_game()

    def eat_snack(self):
        snack_energy = 10
        if self.player.snacks > 0:
            self.player.snacks -= 1
            if self.player.player_stats.energy < 100 - snack_energy:
                self.player.player_stats.energy += snack_energy
            else:
                self.player.player_stats.energy = 100
        self.close_eat()
        self.save_game()

            
    def game_speed(self):
        self.close_eat()
        self.close_map()
        

    def increase(self):
        self.close_eat()
        self.close_map()
        if self.mile_counter.update_delay > 100:
            self.mile_counter.update_delay -= 500

        if self.mile_counter.update_delay == 100:
            self.speed_image= REALLY_FAST_IMAGE

        elif self.mile_counter.update_delay == 600:
            self.speed_image= FAST_IMAGE

        elif self.mile_counter.update_delay == 1100:
            self.speed_image= AVERAGE_IMAGE

        elif self.mile_counter.update_delay == 1600:
            self.speed_image= SLOW_IMAGE

        elif self.mile_counter.update_delay == 2100:
            self.speed_image= REALLY_SLOW_IMAGE

        

    def decrease(self):
        
        self.close_eat()
        self.close_map()
        if self.mile_counter.update_delay <= 2000:
            self.mile_counter.update_delay += 500

        if self.mile_counter.update_delay == 100:
            self.speed_image= REALLY_FAST_IMAGE

        elif self.mile_counter.update_delay == 600:
            self.speed_image= FAST_IMAGE

        elif self.mile_counter.update_delay == 1100:
            self.speed_image= AVERAGE_IMAGE

        elif self.mile_counter.update_delay == 1600:
            self.speed_image= SLOW_IMAGE

        elif self.mile_counter.update_delay == 2100:
            self.speed_image= REALLY_SLOW_IMAGE

        

        

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

            

            for button in self.all_sprites:
                button.handle_event(event)

            for button in self.waypoint_action_sprites:
                button.handle_event(event)
                
            for button in self.food_sprites:
                button.handle_event(event)

            for button in self.random_event_sprites:
                button.handle_event(event)

            for button in self.water_event_sprites:
                button.handle_event(event)

    def close_water(self):
        if self.hydration_event_showing:
            self.player.player_stats.water_warning_acknowledged = True
            self.status = self.prior_status
            
            self.prior_status = ""
            self.hydration_event_showing = False
            self.action_sprite_logic()
            
            if self.player.mile != self.waypoint_object.mile:
                self.mile_counter.pause("False")
                self.pause_sprite = False
                self.display_random_trail = True
                self.display_random_trail

        

    def run_logic(self):
        if self.player.player_stats.out_of_water\
           and not self.player.player_stats.water_warning_acknowledged:
            if self.prior_status == "":
                self.prior_status = self.status
            
            self.status = "Hydration_Warning"
            
            self.waypoint_action_sprites.empty()            
            self.hydration_event_showing = True
            
        self.player.update()

        self.next_resupply.update(self.waypoint_object)
        
        self.next_water.update(self.waypoint_object)
        self.next_camping.update(self.waypoint_object)
        
        if not self.player.player_stats.energy_exempt:
            if self.player.player_stats.energy <= 0:
                self.done = True
                self.game_state = GameState.GAMEOVER
        
        if self.player.hiker_funds.calculate_available() <= 0\
           or self.player.player_stats.health <= 0:
            self.done = True
            self.game_state = GameState.GAMEOVER
            
        if self.player.mile == self.waypoint_object.mile:
            self.mile_counter.pause("False") ## set running to false
            self.pause_sprite = True
            self.display_random_trail = False

            if self.random_event_display != None:
                if self.random_event_display.sleep_event == "magic":           
                    if self.player.player_stats.energy <= 80:
                        self.player.player_stats.energy +=20
                    else:
                        self.player.player_stats.energy = 100

        elif self.status == "Hydration_Warning":
            self.mile_counter.pause("False") ## set running to false
            self.pause_sprite = True
            self.display_random_trail = False            
                    
        else:
            self.mile_counter.update()
            self.pause_sprite = False
            self.display_random_trail = True
            

        if self.status == "To Town":
            self.show_waypoint_actions = False
            if self.waypoint_object.distance > 0 and self.walking:
                adjust = self.waypoint_object.distance/5
                energy_adjust = ((self.waypoint_object.distance/.1)\
                                *self.player.player_stats.energy_deduction)/5            
   
            else:
                adjust = 0
                energy_adjust  = 0
                
            now = pg.time.get_ticks()
            if now - self.town_update > self.to_town_delay:
                self.town_update = now
                              
                self.town_count += 1
                self.player.today_miles += adjust
                self.player.player_stats.energy -= energy_adjust
                if self.town_count == 5:
                    self.town_count = 0
                    self.status = "In Town"
                    
                    self.to_town_showing = False
                    
        if self.status == "In Town":
            self.resupply()
            

        if self.status == "Sleeping":
            now = pg.time.get_ticks()
            if now - self.sleep_update > self.sleep_delay:
                self.sleep_update = now
                              
                self.sleep_count += 1
                if self.sleep_count == 5:
                    sleep_energy = 30
            
                    if self.player.player_stats.energy < 100 - sleep_energy:
                        self.player.player_stats.energy += sleep_energy
                    else:
                        self.player.player_stats.energy = 100
                        
                    self.sleep_count = 0
                    self.status = "Hiking"
                     
                    self.date_display.update()
                    self.sleep_display_showing = False

                    
                    self.mile_counter.pause("False") #set back to running

                    self.waypoint_display.comment = "Good Morning! Let's get hiking!"
                    self.player.today_miles = 0.0

                    if self.random_event_display != None:
                        self.random_event_showing = True
                        if self.random_event_display.sleep_event == "bear":
                            self.player.breakfast = 0
                            self.player.lunch = 0
                            self.player.dinner = 0
                            self.player.snacks = 0
               
                    else:
                        self.waypoint_action_sprites.add(self.next_btn)

        #print("Game Status", self.status)

        self.player.status = self.status
                            


    def draw(self):
        pg.draw.rect(self.screen, (0, 71, 4),(227, 0, 430, 60))
        
        if self.status == "Sleeping":
            self.screen.blit(self.night_background,(227,485))
        else:
            self.screen.blit(self.background,(227,485))
        
        pg.draw.rect(self.screen, (30, 30, 30),(657, 0, 140, 600))

        self.screen.blit(MAP_BTN,(675, 110))
        self.screen.blit(self.speed_image,(660, 257))
        self.screen.blit(EAT_BTN,(685, 440))
        
        title = drop_shadow_text(self.player.name + "'s Adventure",
             "franklingothicheavy", 35, pg.Color("black"), pg.Color("white"),0, 0, 1)

        self.screen.blit(title, center_of_surface(title, 442, 30))

        self.date_display.draw()
        self.status_bar.update(self.player)

        self.mile_display.draw()
        self.sign_display.draw()

        if self.hydration_event_showing:
            self.hydration_event_display.draw()
            self.water_event_sprites.add(self.close_water_btn)
            self.water_event_sprites.draw(self.screen)

        elif self.display_random_trail:            
            self.random_trail_image.draw()
   
        elif self.sleep_display_showing:
            if self.status == "Sleeping":
                self.sleep_display.draw()

        elif self.to_town_showing:
            if self.status == "To Town":
                self.to_town_display.draw()
            
        else:
            self.waypoint_display.draw()
            if self.player.player_stats.shelters_only and self.waypoint_object.category =="Campsite"\
               and self.status != "Start":                   
                self.screen.blit(self.no_camping,(246,153))
                
        if self.random_event_showing and not self.display_random_trail:
            if self.random_event_display != None:
                self.random_event_display.draw()
                self.random_event_sprites.draw(self.screen)

        self.map_display.draw()
        self.eat_display.draw()

        if not self.pause_sprite:

            self.hiker_group.update()
            self.hiker_group.draw(self.screen)

        if self.player.mile == self.waypoint_object.mile:             
            self.waypoint_action_sprites.draw(self.screen)

        if not self.eat_display.done:
            self.food_sprites.draw(self.screen)

            
        self.all_sprites.draw(self.screen)

        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)
        cursor_AT(self.screen, True)
        pg.display.flip()
        self.clock.tick(60)

class Player:
    def __init__(self, current_waypoint = 1, current_mile = 0.0):
        self.name = ""
        self.year = self.start_year()
        self.start_month = 3
        self.start_day = 15
        self.current_month = 3
        self.current_day = 15
        self.hiker_funds = Hiker_Funds()
        self.today_miles = 0.0
        self.gear = ""
        self.base_weight = 0       
        self.breakfast = 0
        self.lunch = 0
        self.dinner = 0
        self.snacks = 0        
        self.liters = 0
        self.current_waypoint = current_waypoint
        self.mile = current_mile
        self.pack_weight = self.calculate_Packweight()
        self.mail_drops = []       
        self.player_stats = Player_Stats()
        self.random_events = None

        self.to_buy = [("Tent", False), ("Tent Poles", False), ("Repair Tape", False),
                       ("Hiking Poles", False), ("Shoes", False), ("Socks", False)]

        self.status = "Start"
        
        self.game_state = GameState.MENU

        

    

    def start_year(self):
        date_now = date.datetime.now()
        year = date_now.year + 1
        return year

    def calculate_Packweight(self):
        foodweight = (self.breakfast * .5) + (self.lunch * .5)\
                     + (self.dinner * .5) + (self.snacks * .25)
        waterweight = self.liters * 2.2
        
        self.packweight = self.base_weight + waterweight + foodweight

        return self.packweight

    def get_WeightOfWater(self):
        return self.liters * 2.2       

    def update(self):
        self.to_buy = self.player_stats.to_buy 

        if self.calculate_Packweight() >= 35:
            self.player_stats.energy_consumption_rate = 1.25 
            self.player_stats.energy_deduction = self.player_stats.energy_consumption_rate\
                                                 * self.player_stats.energy_percent      

        elif self.calculate_Packweight() < 35 and self.calculate_Packweight()> 30 :
            self.player_stats.energy_consumption_rate = 1
            self.player_stats.energy_deduction = self.player_stats.energy_consumption_rate\
                                                 * self.player_stats.energy_percent

        else:
            self.player_stats.energy_consumption_rate = .75
            self.player_stats.energy_deduction = self.player_stats.energy_consumption_rate\
                                                 * self.player_stats.energy_percent

        self.player_stats.miles_since_last_zero = self.mile - self.player_stats.last_zero_mile
        self.player_stats.miles_since_last_laundry = self.mile - self.player_stats.last_laundry_mile




class PlayerMenu:
    def __init__(self, screen, player):        
        self.done = False
        self.clock = pg.time.Clock()
        self.screen = screen
        self.player = player
        self.showAlert = False
        self.message = []
        self.alert = Alert(self.screen, self.message, self.showAlert)
        self.game_state = GameState.PLAYERMENU
        self.background  = pg.transform.scale(pg.image.load(resource_path('images/player.jpg')),
                                               (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.player_set = False
        self.display_start_funds = True
        self.display_gear_food = False
        self.nameInput = InputText(False, self.screen, self.player, 337,
                                   130, 350, 45, "black",
                                   "springgreen", "georgia", 30)      

        self.weatherDisplay = WeatherDisplay(False,self.screen, self.player,
                                             112, 375, 576, 100,"black",
                                             "springgreen", "georgia", 30)        

        self.dateSpinner = DateSpinner(False, self.screen, self.player, 112, 200,
                                       200, self.weatherDisplay)
        
        self.hiker_funds = self.player.hiker_funds 
        
        self.fundsSpinner = FundsSpinner(False, self.screen, self.hiker_funds, self.player,
                                         337, 200, 350)        
        
        self.availableFund = AvailableFunds(False, self.screen, self.hiker_funds)
        
        self.packWeight = PackWeight(False, self.screen, self.player)        

        self.packPicker = PackInfo(False,self.screen,self.hiker_funds, self.player)        

        self.mealsSpinner = MealsWaterSpinner(False, self.screen, self.hiker_funds, self.player,
                                              self.availableFund, self.packWeight,
                                         425, 130, 325)      

        self.player_menu_sprites = pg.sprite.Group()
        self.funds_start_sprites = pg.sprite.Group()
        self.gear_food_sprites = pg.sprite.Group()

        self.next = Button(
            525, 500, 200, 50, self.next,
            pg.font.SysFont("franklingothicheavy",24),
            'Next', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)
        
        self.back = Button(
            300, 500, 200, 50, self.back,
            pg.font.SysFont("franklingothicheavy",24),
            'Back', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.play_game = Button(
            525, 500, 200, 50, self.play_game,
            pg.font.SysFont("franklingothicheavy",24),
            'Play Game', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.quit_button = Button(
            75, 500, 200, 50, self.quit_game,
            pg.font.SysFont("franklingothicheavy",24),
            'Exit Game', pg.Color("white"), WOOD_BTN, WOOD_BTN, WOOD_BTN)

        self.player_menu_sprites.add(self.quit_button)
        
        

    def next(self):
        self.message.clear()
 
        if self.player.name == '':
            self.nameInput.error = "Name is Required"
            self.message.append("- Everyone Needs a Name!")

        if self.hiker_funds.funds == 0:
            self.message.append("- You're not going anywhere with that much money")

        if self.nameInput.error =="Too Long":
            self.message.append("- Pick a shorter name, please")

        if len(self.message) > 0:
            self.showAlert = True
            self.alert.showing = True
            self.alert.alert_sprites.empty()

        elif self.nameInput.error =="" and len(self.message) == 0:
            self.display_start_funds = False
            self.display_gear_food = True

        self.funds_start_sprites.empty()
        self.gear_food_sprites.empty()

        self.packWeight.add_to_display(self.screen)
        self.availableFund.add_to_display(self.screen)
        

    def back(self):
        self.display_start_funds = True
        self.display_gear_food = False
        self.funds_start_sprites.empty()
        self.gear_food_sprites.empty()

    def play_game(self):
        self.message.clear()
        if self.player.gear == "":
            self.message.append("- A Gear Choice is Required")
        if self.player.snacks == 0 and self.player.breakfast == 0\
           and self.player.lunch==0 and self.player.dinner==0:
            self.message.append("- At least take a snack!")
        if self.player.liters == 0:
            self.message.append("- Water is a necessity! 0.5 liters required")
        if self.hiker_funds.calculate_available() <=0:
            self.message.append("- You're not going anywhere with that much money")

        if len(self.message) > 0:
            self.showAlert = True
            self.alert.showing = True
            self.alert.alert_sprites.empty()

        else:
            self.player.hiker_funds = self.hiker_funds
            self.game_state = GameState.PLAYGAME
            self.done = True              

    def quit_game(self):        
        self.done = True
        self.game_state = GameState.QUIT

    def run(self):
        while not self.done:
            self.dt = self.clock.tick(60)
            self.handle_events()
            self.run_logic()
            self.draw()

    def handle_events(self):

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
                self.game_state = GameState.QUIT
   
            for button in self.player_menu_sprites:
                button.handle_event(event)

            for button in self.dateSpinner.date_sprites:
                button.handle_event(event)

            for button in self.fundsSpinner.fund_sprites:
                button.handle_event(event)

            for button in self.funds_start_sprites:
                button.handle_event(event)

            for button in self.gear_food_sprites:
                button.handle_event(event)

            for button in self.alert.alert_sprites:
                button.handle_event(event)

            self.packPicker.handle_events(event)

            for button in self.mealsSpinner.consumables_sprites:
                button.handle_event(event)
            
            self.nameInput.event_handler(event)            
            
            if self.player.name != '':
                self.nameInput.error = ""
                
            if self.nameInput.width_text > 168:
                self.nameInput.error = "Too Long"

    def run_logic(self):
        if self.display_start_funds:
            self.funds_start_sprites.update(self.dt)
        if self.display_gear_food:
            self.gear_food_sprites.update(self.dt)
        self.mealsSpinner.consumables_sprites.update(self.dt)


    def draw(self):
        blaze = pg.transform.scale(BLAZE, (25, 75))
        texture  = pg.transform.scale(CLOUD,(200,45))

        self.screen.blit(self.background,(0,0))

        title = drop_shadow_text("Thru-Hike Settings",
             "impact", 65, pg.Color("black"), pg.Color("white"),432, 50, 1)

        self.screen.blit(title, center_of_surface(title, 400, 65))
        self.screen.blit(blaze, (50,28))
        self.screen.blit(blaze, (725,28))

        frame(self.screen, 0, 0, 800, 600, 6,
              pg.Color("black"),pg.Color("darkgray"), 2)

        if self.showAlert == True:
            self.alert.draw(self.screen)
            self.showAlert = self.alert.showing          

        elif self.display_start_funds:
            self.nameInput.visible = True
            self.dateSpinner.visible = True
            self.weatherDisplay.visible = True
            self.fundsSpinner.visible = True
            self.availableFund.visible = False
            self.packWeight.visible = False
            self.packPicker.visible = False
            self.packPicker.conv_box = pg.Rect(-25, 0, 0, 0)
            self.packPicker.lightweight_box = pg.Rect(-25, 0, 0, 0)
            self.packPicker.ultralight_box = pg.Rect(-25, 0, 0, 0)
            self.mealsSpinner.visible = False
            self.mealsSpinner.consumables_sprites.empty()

            self.screen.blit(texture,(112,130))
            pg.draw.rect(self.screen, pg.Color("black"), (112,130, 200, 45),2)        

            namelabel = drop_shadow_text("Trail Name:", "impact", 
                     30, pg.Color("white"), pg.Color("black"),0, 0, 0)

            self.screen.blit(namelabel,(145,135))

            self.nameInput.add_to_display(self.screen)

            self.weatherDisplay.add_to_display(self.screen, self.player)
        
            self.dateSpinner.draw(self.screen)

            self.fundsSpinner.draw(self.screen)    

            errorlabel = pg.font.SysFont("impact", 18)
            TextSurf, TextRect = text_objects(self.nameInput.error,
                                              errorlabel, pg.Color("darkred"))
            TextRect.center = (617,150)
            self.screen.blit(TextSurf, TextRect)            
            
            self.funds_start_sprites.add(self.next)

            if self.showAlert == False:
                self.funds_start_sprites.draw(self.screen)

        elif self.display_gear_food:
            self.nameInput.visible = False
            self.dateSpinner.visible = False
            self.dateSpinner.date_sprites.empty()
            self.weatherDisplay.visible = False
            self.fundsSpinner.fund_sprites.empty()
            self.availableFund.visible = True
            self.packWeight.visible = True
            self.packPicker.visible = True
            self.mealsSpinner.visible = True

            if self.player.gear == "Lightweight":
                self.packPicker.activeChoice = self.packPicker.lightweight_box
            elif self.player.gear == "Conventional":
                self.packPicker.activeChoice = self.packPicker.conv_box
            elif self.player.gear == "Ultralight":
                self.packPicker.activeChoice = self.packPicker.ultralight_box
            else:
                self.packPicker.activeChoice = None

            self.packPicker.draw(self.screen)

            self.mealsSpinner.draw(self.screen)

            self.packWeight.add_to_display(self.screen)
            self.availableFund.add_to_display(self.screen)
            self.gear_food_sprites.add(self.back, self.play_game)
            self.gear_food_sprites.draw(self.screen)

        if self.showAlert == False:
            self.player_menu_sprites.draw(self.screen)
   
        cursor_AT(self.screen, True)
        
        pg.display.update()
        self.clock.tick(60)

    def current_state(self):
        return self.game_state

def main():
    pg.init()

    gameDisplay = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pg.display.set_caption('Appalachian Trail')
    gameIcon = pg.image.load(resource_path('images/icon.png'))
    pg.display.set_icon(gameIcon)
    game_state = GameState.MENU

    while True:
        # State for menu
        if game_state == GameState.MENU:
            player = Player()
            menu = Menu(gameDisplay, player)
            menu.run()
            player = menu.player            
            game_state = menu.current_state()

        # State for getting explanations
        elif game_state == GameState.WELCOME:
            welcome = Welcome(gameDisplay)
            welcome.run()            
            game_state = welcome.current_state()            

        # State for setting up new player/game
        elif game_state == GameState.PLAYERMENU:
            player_menu = PlayerMenu(gameDisplay, player)            
            player_menu.run()
            game_state = player_menu.current_state()

        # State for setting up playing game
        elif game_state == GameState.PLAYGAME:
            game = Game(gameDisplay, player)
            game.run()
            game_state = game.current_state()
            
        # State for gameover  
        elif game_state == GameState.GAMEOVER:
            game_over = GameOver(gameDisplay, player)
            game_over.run()
            game_state = game_over.current_state()
            player = Player()
            

        elif game_state == GameState.QUIT:            
            pg.quit()
            quit()

if __name__ == '__main__':
    main()
