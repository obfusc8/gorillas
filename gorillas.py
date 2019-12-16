#!/usr/bin/env python

import os
import pygame
import random

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")
WHITE = (255,255,255)

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

# classes for our game objects
class Gorilla(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("gorilla.bmp", WHITE)
        self.image = pygame.transform.scale(self.image, (50, 54))
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

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

def main():
    screen_width = 1200
    screen_height = 800
    background = (0,50,100)
    clock_speed = 60

    pygame.init()
    screen = pygame.display.set_mode((screen_width,screen_height))
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

    # Get positions of Gorillas
    left_x = buildings.sprites()[1].rect.x + buildings.sprites()[1].rect.width//2
    left_y = screen_height - buildings.sprites()[1].rect.height
    right_x = buildings.sprites()[-2].rect.x + buildings.sprites()[-2].rect.width//2
    right_y = screen_height - buildings.sprites()[-2].rect.height

    g1 = Gorilla()
    g1.rect.x = left_x - 25
    g1.rect.y = left_y - 54

    g2 = Gorilla()
    g2.rect.x = right_x - 25
    g2.rect.y = right_y - 54
    gorillas = pygame.sprite.RenderPlain((g1, g2))
    
    while not done:
        clock.tick(clock_speed)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True

        screen.fill(background)

        buildings.draw(screen)
        gorillas.draw(screen)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
