#!/usr/bin/env python

import os
import pygame
import random
import sys

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")
WHITE = (255,255,255)
GOR_COLOR = (255, 170, 82)
screen_width = 1200
screen_height = 800
background = (0,50,100)
clock_speed = 60

GOR_DOWN_ASCII = """

          XXXXXXXX
          XXXXXXXX
         XX      XX
         XXXXXXXXXX
         XXX  X  XX
          XXXXXXXX
          XXXXXXXX
           XXXXXX
      XXXXXXXXXXXXXXXX
   XXXXXXXXXXXXXXXXXXXXXX
  XXXXXXXXXXXX XXXXXXXXXXX
 XXXXXXXXXXXXX XXXXXXXXXXXX
 XXXXXXXXXXXX X XXXXXXXXXXX
XXXXX XXXXXX XXX XXXXX XXXXX
XXXXX XXX   XXXXX   XX XXXXX
XXXXX   XXXXXXXXXXXX   XXXXX
 XXXXX  XXXXXXXXXXXX  XXXXX
 XXXXX  XXXXXXXXXXXX  XXXXX
  XXXXX XXXXXXXXXXXX XXXXX
   XXXXXXXXXXXXXXXXXXXXXX
       XXXXXXXXXXXXX
     XXXXXX     XXXXXX
     XXXXX       XXXXX
    XXXXX         XXXXX
    XXXXX         XXXXX
    XXXXX         XXXXX
    XXXXX         XXXXX
    XXXXX         XXXXX
     XXXXX       XXXXX
"""

# Make surface from ASCII
def makeSurfaceFromASCII(ascii, fgColor=(255,255,255), bgColor=(0,0,0)):
    """Returns a new pygame.Surface object that has the image drawn on it as specified by the ascii parameter.
    The first and last line in ascii are ignored. Otherwise, any X in ascii marks a pixel with the foreground color
    and any other letter marks a pixel of the background color. The Surface object has a width of the widest line
    in the ascii string, and is always rectangular."""

    """Try experimenting with this function so that you can specify more than two colors. (Pass a dict of
    ascii letters and RGB tuples, say."""
    ascii = ascii.split('\n')[1:-1]
    width = max([len(x) for x in ascii])
    height = len(ascii)
    surf = pygame.Surface((width, height))
    surf.fill(bgColor)

    pArr = pygame.PixelArray(surf)
    for y in range(height):
        for x in range(len(ascii[y])):
            if ascii[y][x] == 'X':
                pArr[x][y] = fgColor
    return surf

def placeGorilla(buildings, pos):
    x = buildings.sprites()[pos].rect.x + buildings.sprites()[pos].rect.width//2
    y = screen_height - buildings.sprites()[pos].rect.height
    return x, y    

# functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self):
            pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print("Cannot load sound: %s" % fullname)
        raise SystemExit(str(geterror()))
    return sound

# classes for the game objects
class Gorilla(pygame.sprite.Sprite):

    def __init__(self, xy=None):
        self.width = 50
        self.height = 54
        pygame.sprite.Sprite.__init__(self)
        self.image = GOR_DOWN_SURF
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        if xy == None:
            self.x = 0
            self.y = 0
        else:
            self.rect.x = xy[0] - self.width//2
            self.rect.y = xy[1] - self.height

    def setXY(self, xy):
        self.rect.x = xy[0] - self.width//2
        self.rect.y = xy[1] - self.height

class Building(pygame.sprite.Sprite):
    
    def __init__(self, width=None, height=None):
        b_width = width
        if width == None: b_width = random.randrange(70, 200, 10)
        b_height = height
        if height == None: b_height = random.randrange(100, 500, 10)

        w_width = 8
        w_margin = 10
        
        w_height = 15
        h_margin = 15

        rows = (b_height - h_margin) // (w_height + h_margin)
        cols = (b_width - w_margin) // (w_width + w_margin)
        
        wall = [(51, 204, 204),(204,0,0),(192,192,192)]
        window = [(255,255,0),(255,255,0),(80,80,80)]
        
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([b_width, b_height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)

        pygame.draw.rect(self.image, random.choice(wall), [0, 0, b_width, b_height])
        
        for row in range(rows):
            for col in range(cols):
                pygame.draw.rect(self.image, random.choice(window),
                                 [(w_width + w_margin) * col + w_margin,
                                  (w_height + h_margin) * row + h_margin,
                                   w_width, w_height])

        self.rect = self.image.get_rect()

class Banana():
    def __init__(self):
        pass

    def __repr__(self):
        pass

GOR_DOWN_SURF = makeSurfaceFromASCII(GOR_DOWN_ASCII, GOR_COLOR, background)

def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('GORILLAS')
    clock = pygame.time.Clock()
    done = False

    # Generate buildings
    buildings = pygame.sprite.RenderPlain(())
    total_width = 0
    full = False
    while not full:
        if total_width > screen_width-250:
            full = True
            b = Building(max(0,screen_width - total_width - 6))
        else:
            b = Building()
        b.rect.x = total_width + 3
        b.rect.y = screen_height - b.image.get_height()
        total_width += b.image.get_width() + 3
        buildings.add(b)

    # Generate gorillas
    g1 = Gorilla(placeGorilla(buildings, 1))
    g2 = Gorilla(placeGorilla(buildings, -2))
    gorillas = pygame.sprite.RenderPlain((g1, g2))
    
    while not done:
        clock.tick(clock_speed)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True

        screen.fill(background)

        buildings.draw(screen)
        gorillas.draw(screen)
        
        pygame.display.update()

    pygame.quit()
    sys.exit(1)

if __name__ == "__main__":
    main()
