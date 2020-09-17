import sys
import os
import pygame as pg
import pickle

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def save_game(player):        
        player_object = player
        picklefile = open('player_object', 'wb')
        pickle.dump(player_object, picklefile)
        picklefile.close()





    

def cursor_AT(gameDisplay, status):
    if status:
        mouse_cursor = pg.image.load(resource_path('images/cursor.png')).convert_alpha()

        x, y = pg.mouse.get_pos()
        x -= mouse_cursor.get_width()/11
        y -= mouse_cursor.get_height()/11

        gameDisplay.blit(mouse_cursor,(int(x), int(y)))
        pg.mouse.set_visible(False)
        
    else:
        pg.mouse.set_visible(True)


def drop_shadow_text(text, font, size, color_shadow, color_text, x, y, offset):
    labelText = pg.font.SysFont(font, size)
    
    TextSurfShadow, TextRectShadow = text_objects(text, labelText, color_shadow)
    surface_size = TextSurfShadow.get_width(), TextSurfShadow.get_height()
    TextRectShadow.center = (x,y)
    TextSurfTop, TextRectTop = text_objects(text, labelText, color_text)
    TextRectTop.center = (x-offset,y-offset)
    
    img = pg.Surface(surface_size,  pg.SRCALPHA, 32)
    img.blit(TextSurfShadow,(offset, offset))
    img.blit(TextSurfTop,(0,0))
    
    return img

def center_of_surface(surface, w, h):
    x = w - surface.get_width() // 2
    y = h - surface.get_height() // 2
    return x, y

#Month Name
def month_names(month):
    if month == 1:
        return "January"
    elif month == 2:
        return "February"
    elif month == 3:
        return "March"
    elif month == 4:
        return "April"
    elif month == 5:
        return "May"
    elif month == 6:
        return "June"
    elif month == 7:
        return "July"
    elif month == 8:
        return "August"
    elif month == 9:
        return "September"
    elif month == 10:
        return "October"
    elif month == 11:
        return "November"
    elif month == 12:
        return "December"

#Display Frame
def frame(gameDisplay, x, y, w, h, thickness,outer_color, inner_color, outline):
    pg.draw.rect(gameDisplay,outer_color , (x,y,w,h), thickness)
    pg.draw.rect(gameDisplay,inner_color , ((x+thickness/2)-1,(y+thickness/2)-1,
                                            (w-thickness)+1,(h-thickness)+1), outline)
    
    pg.draw.rect(gameDisplay,pg.Color("black") , (5,4,791,592), 1)
    
# Text Object    
def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

# draw some text into an area of a surface
# automatically wraps words
# returns any text that didn't get blitted
def drawText(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pg.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]
    

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], True, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]

    return text

def round_rect(surface, rect, color, rad=20, border=0, inside=(0,0,0,0)):
    """
    Draw a rect with rounded corners to surface.  Argument rad can be specified
    to adjust curvature of edges (given in pixels).  An optional border
    width can also be supplied; if not provided the rect will be filled.
    Both the color and optional interior color (the inside argument) support
    alpha.
    """
    rect = pg.Rect(rect)
    zeroed_rect = rect.copy()
    zeroed_rect.topleft = 0,0
    image = pg.Surface(rect.size).convert_alpha()
    image.fill((0,0,0,0))
    _render_region(image, zeroed_rect, color, rad)
    if border:
        zeroed_rect.inflate_ip(-2*border, -2*border)
        _render_region(image, zeroed_rect, inside, rad)
    surface.blit(image, rect)


def _render_region(image, rect, color, rad):
    """Helper function for round_rect."""
    corners = rect.inflate(-2*rad, -2*rad)
    for attribute in ("topleft", "topright", "bottomleft", "bottomright"):
        pg.draw.circle(image, color, getattr(corners,attribute), rad)
    image.fill(color, rect.inflate(-2*rad,0))
    image.fill(color, rect.inflate(0,-2*rad))
