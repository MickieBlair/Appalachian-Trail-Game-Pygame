import pygame as pg
from functions import *
pg.init()

# Constants
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600

FONT = pg.font.SysFont('georgia', 32)

BLAZE = pg.image.load(resource_path('images/blaze.png'))

MAP_BTN = pg.image.load(resource_path('images/button/map.png'))
SPEED_BTN = pg.image.load(resource_path('images/button/speed.png'))
EAT_BTN = pg.image.load(resource_path('images/button/eat.png'))
DRINK_BTN = pg.image.load(resource_path('images/button/drink.png'))
LAUNDRY_BTN = pg.image.load(resource_path('images/laundry.png'))
GEAR_BTN = pg.image.load(resource_path('images/button/backpack.png'))


CASH_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/cash.png')),(35, 35))
ENERGY_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/energy.png')),(35, 35))
HEALTH_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/health.png')),(35, 35))
WEIGHT_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/weight.png')),(33, 33))
WATER_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/water.png')),(35, 35))
FOOD_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/food_symbol.png')),(35, 35))

REALLY_FAST_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/bobcat.png')),(125, 125))
FAST_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/deer.png')),(125, 125))
AVERAGE_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/rabbit.png')),(125, 125))
SLOW_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/turtle.png')),(125, 125))
REALLY_SLOW_IMAGE= pg.transform.scale(pg.image.load(resource_path('images/snail.png')),(125, 125))


CAMP_IMAGE = pg.image.load(resource_path('images/camp.png'))
HOSTEL_IMAGE = pg.image.load(resource_path('images/hostel.png'))
HOTEL_IMAGE = pg.image.load(resource_path('images/hotel.png'))
SHOP_IMAGE = pg.image.load(resource_path('images/grocery.png'))
MAIL_IMAGE = pg.image.load(resource_path('images/po.png'))
NO_MAIL_IMAGE = pg.image.load(resource_path('images/blankPO.png'))

##MAIL_BTN = pg.image.load(resource_path('images/check_mail_btn.png'))

##REFILL_BTN = pg.image.load(resource_path('images/refill.png'))
##TOWN_BTN = pg.image.load(resource_path('images/town.png'))
##CAMP_BTN = pg.image.load(resource_path('images/camp2.png'))



WOOD_BTN = pg.image.load(resource_path('images/button/board.png'))
HEADER = pg.image.load(resource_path('images/button/headerboard.png')) 

CLOSE_HOVER = pg.image.load(resource_path('images/button/closeX_hover.png')) 
CLOSE_DOWN = pg.image.load(resource_path('images/button/closeX_down.png'))
CLOSE_NORMAL = pg.image.load(resource_path('images/button/closeX_normal.png'))



IMAGE_HOVER = pg.image.load(resource_path('images/button/dark.jpg')) 
IMAGE_DOWN = pg.image.load(resource_path('images/button/dark.jpg'))
IMAGE_NORMAL = pg.image.load(resource_path('images/button/light.jpg'))

LEFT_HOVER = pg.image.load(resource_path('images/button/left_hover.jpg')) 
LEFT_DOWN = pg.image.load(resource_path('images/button/left_down.jpg')) 
LEFT_NORMAL = pg.image.load(resource_path('images/button/left_normal.jpg')) 

RIGHT_HOVER = pg.image.load(resource_path('images/button/right_hover.jpg')) 
RIGHT_DOWN = pg.image.load(resource_path('images/button/right_down.jpg')) 
RIGHT_NORMAL = pg.image.load(resource_path('images/button/right_normal.jpg'))

DOWN_HOVER = pg.image.load(resource_path('images/button/down_hover.png')) 
DOWN_DOWN = pg.image.load(resource_path('images/button/down_down.png')) 
DOWN_NORMAL = pg.image.load(resource_path('images/button/down_normal.png')) 

UP_HOVER = pg.image.load(resource_path('images/button/up_hover.png')) 
UP_DOWN = pg.image.load(resource_path('images/button/up_down.png')) 
UP_NORMAL = pg.image.load(resource_path('images/button/up_normal.png')) 

CHECK = pg.image.load(resource_path('images/button/check.png'))

# Colors
BROWNISH = pg.image.load(resource_path('images/colors/brownish.png')) 
CLOUD = pg.image.load(resource_path('images/colors/cloud.jpg')) 
GREEN = pg.image.load(resource_path('images/colors/green.png')) 
RED = pg.image.load(resource_path('images/colors/red.png'))
GRAY = pg.image.load(resource_path('images/colors/gray.png'))


# Weather
SUNNY = pg.image.load(resource_path('images/weather/sunny.png')) 
RAIN = pg.image.load(resource_path('images/weather/rain.png'))
CLOUDY = pg.image.load(resource_path('images/weather/cloudy.png'))
T_STORMS = pg.image.load(resource_path('images/weather/t-storms.png'))
PARTLY_CLOUDY = pg.image.load(resource_path('images/weather/partly_cloudy.png'))
WINDY = pg.image.load(resource_path('images/weather/windy.png'))
SLEET = pg.image.load(resource_path('images/weather/sleet.png'))
SNOW = pg.image.load(resource_path('images/weather/snow.png'))
COLD = pg.image.load(resource_path('images/weather/cold.png'))
WARM = pg.image.load(resource_path('images/weather/warm.png'))
HOT = pg.image.load(resource_path('images/weather/hot.png'))
