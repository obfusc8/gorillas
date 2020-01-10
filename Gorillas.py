import random
import sys
import pygame
from pygame.math import Vector2

import GameImages
import math
import time

# GET SYSTEM ARGUMENTS #
if len(sys.argv) > 1:
    # sys.argv[1]...
    pass

# SCREEN SETTINGS
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FRAME_RATE = 30

# GLOBAL CONSTANTS #
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
PIXEL_COLORS = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]
BUILDING_COLORS = [(173, 170, 173), (0, 170, 173), (173, 0, 0)]
LIGHT_WINDOW = (255, 255, 82)
SKY_COLOR = (0, 0, 173)
DARK_WINDOW = (82, 85, 82)
GORILLA_COLOR = (255, 170, 82)
BANANA_COLOR = (255, 255, 82)
SUN_COLOR = (255, 255, 0)
EXPLOSION_COLOR = (255, 0, 0)
DARK_RED_COLOR = (173, 0, 0)


def makeSurfaceFromASCII(shape, fgColor=COLOR_WHITE, bgColor=COLOR_BLACK):
    shape = shape.split('\n')[1:-1]
    width = max([len(x) for x in shape])
    height = len(shape)
    image = pygame.Surface((width, height), pygame.SRCALPHA)

    pArr = pygame.PixelArray(image)
    for y in range(height):
        for x in range(len(shape[y])):
            if shape[y][x] == 'X':
                pArr[x][y] = fgColor

    image = pygame.transform.scale2x(image)

    return image


class Gorilla(pygame.sprite.Sprite):

    def __init__(self, on_left=True):
        pygame.sprite.Sprite.__init__(self)
        self.base_image = pygame.Surface((150, 150), pygame.SRCALPHA)
        xy = ((self.base_image.get_width()-GORILLA_DOWN.get_width())//2, self.base_image.get_height()-GORILLA_DOWN.get_height())
        self.image_down = self.base_image.copy()
        self.mask = pygame.mask.from_surface(self.image_down)
        self.gor_rect = self.image_down.blit(GORILLA_DOWN, xy)
        self.image_left = self.base_image.copy()
        self.image_left.blit(GORILLA_LEFT, xy)
        self.image_right = self.base_image.copy()
        self.image_right.blit(GORILLA_RIGHT, xy)

        self.image = self.image_down.copy()
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.on_left = on_left
        if on_left:
            self.aim_start = math.radians(-45)
        else:
            self.aim_start = math.radians(-135)
        self.aim = self.aim_start
        self.celebrate = False
        self.celebrations = 6
        self.turn = False
        self.pos = (0, 0)
        self.is_dead = False
        self.left_up = 0
        self.right_up = 0
        self.velocity = 0
        gorillas.add(self)

    def update(self, *args):
        global game_over
        if self.turn and not self.is_dead:
            self.aim_reticule()
            if self.velocity > 0:
                pygame.draw.rect(self.image, (0, 255, 0), (self.gor_rect.centerx-self.velocity//4, self.gor_rect.bottom-10, self.velocity//2, 10))
        elif self.left_up:
            self.image = self.image_left.copy()
            self.left_up = max(0, self.left_up - 1)
        elif self.right_up:
            self.image = self.image_right.copy()
            self.right_up = max(0, self.right_up - 1)
        elif self.celebrate:
            if self.celebrations > 0:
                if self.celebrations % 2 == 0:
                    self.right_up = FRAME_RATE
                else:
                    self.left_up = FRAME_RATE
                self.celebrations -= 1
            else:
                self.celebrate = False
                player1.turn = False
                player2.turn = False
                game_over = True
                ############################################################# GAME OVER
        else:
            self.image = self.original_image.copy()

    def aim_reticule(self):
        x_pos = self.gor_rect.centerx + int(50 * math.cos(self.aim)) - (RETICULE.get_width() // 2)
        y_pos = self.gor_rect.top+5 + int(50 * math.sin(self.aim)) - (RETICULE.get_height() // 2)
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.original_image, (0, 0))
        self.image.blit(RETICULE, (x_pos, y_pos))

    def aim_right(self):
        self.aim = min(0.0, self.aim + math.radians(1))

    def aim_left(self):
        self.aim = max(math.radians(-180), self.aim - math.radians(1))

    def reset(self):
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.original_image, (0, 0))
        self.aim = self.aim_start

    def position(self, xy):
        self.rect.midbottom = xy
        if self.on_left:
            x_pos = self.rect.centerx - 20
        else:
            x_pos = self.rect.centerx + 20
        y_pos = self.rect.bottom - GORILLA_DOWN.get_height()
        self.pos = (x_pos, y_pos)

    def throw(self, velocity):
        Banana(self.pos, self.aim, self.on_left, velocity)
        self.velocity = 0
        self.turn = False
        if self.on_left:
            self.left_up = FRAME_RATE
        else:
            self.right_up = FRAME_RATE

    def power_up(self):
        self.velocity = min(self.velocity + 2, 200)

    def hit(self, xy, size):
        x = xy[0] - self.rect.x
        y = xy[1] - self.rect.y
        pygame.draw.circle(self.original_image, (0, 0, 0, 0), (x, y), size//2)
        self.update()
        self.is_dead = True


class Building(pygame.sprite.Sprite):

    def __init__(self, width=None, height=None):
        win_w = 10
        win_wm = 15
        win_h = 20
        win_hm = 20
        building_m = 10
        building_line = 2
        if not width:
            width = random.randrange(80, 140, 30)
        if not height:
            height = random.randrange(100, 350, 30)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, random.choice(BUILDING_COLORS), (0, 0, width, height))
        for i in range(height//(win_h+win_hm)):
            for j in range(width//(win_w+win_wm)):
                pygame.draw.rect(self.image,
                                 random.choice([DARK_WINDOW, LIGHT_WINDOW]),
                                 (j*(win_w+win_wm)+building_m,
                                  i*(win_h+win_hm)+building_m,
                                  win_w, win_h))
        pygame.draw.rect(self.image, random.choice(SKY_COLOR), (0, 0, width, height), building_line)
        self.mask = pygame.mask.from_surface(self.image)
        buildings.add(self)

    def update(self, *args):
        pass

    def hit(self, xy, size):
        x = xy[0] - self.rect.x
        y = xy[1] - self.rect.y
        pygame.draw.circle(self.image, (0, 0, 0, 0), (x, y), size//2)
        self.mask = pygame.mask.from_surface(self.image)


class Boom(pygame.sprite.Sprite):

    def __init__(self, pos, hit_gorilla=False):
        if hit_gorilla:
            self.size = 200
        else:
            self.size = 30
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((self.size, self.size))
        self.image.set_colorkey(COLOR_BLACK)
        pygame.draw.circle(self.image, (255, 0, 0, 255), (self.size//2, self.size//2), self.size//2)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = pos
        self.alpha = 250
        booms.add(self)

    def update(self, *args):
        self.alpha -= 10
        self.image.set_alpha(self.alpha)
        if self.alpha <= 0:
            self.kill()
            del self
            return

        buildings_hit = pygame.sprite.spritecollide(self, buildings, False, pygame.sprite.collide_mask)
        for b in buildings_hit:
            b.hit(self.rect.center, self.size)

        gorillas_hit = pygame.sprite.spritecollide(self, gorillas, False, pygame.sprite.collide_mask)
        for g in gorillas_hit:
            if g == player:  # WILL ALREADY BE SWAPPED TO NOT THROWING PLAYER
                g.hit(self.rect.center, self.size)


class Sun(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        base_surface = pygame.Surface((SUN_NORMAL.get_width(), SUN_NORMAL.get_height()), pygame.SRCALPHA)
        self.image_not_shocked = base_surface.copy()
        self.image_not_shocked.blit(SUN_NORMAL, (0, 0))
        self.image_shocked = base_surface.copy()
        self.image_shocked.blit(SUN_SHOCKED, (0, 0))
        self.image = self.image_not_shocked
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (SCREEN_WIDTH // 2, 50)
        self.shocked = False
        suns.add(self)

    def update(self):
        if pygame.sprite.spritecollideany(self, bananas, pygame.sprite.collide_mask):
            self.shocked = True
        if self.shocked:
            self.image = self.image_shocked
        else:
            self.image = self.image_not_shocked

    def reset(self):
        self.shocked = False


class Banana(pygame.sprite.Sprite):

    def __init__(self, pos, aim, on_left, velocity):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((BANANA_UP.get_width(), BANANA_UP.get_height()), pygame.SRCALPHA)
        self.image.blit(BANANA_UP, (0, 0))
        self.original_image = self.image.copy()
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = 0
        self.aim = aim
        if on_left:
            self.spin = -1
        else:
            self.spin = 1
        self.start_time = game_timer
        self.x = pos[0]
        self.y = pos[1]
        self.xv = math.cos(-self.aim) * velocity
        self.yv = math.sin(-self.aim) * velocity
        self.gravity = 9.8
        self.wind = 0
        bananas.add(self)

    def update(self, *args):
        global game_over
        building = pygame.sprite.spritecollideany(self, buildings, pygame.sprite.collide_mask)
        if building:
            loc = pygame.sprite.collide_mask(building, self)
            x = building.rect.x + loc[0]
            y = building.rect.y + loc[1]
            Boom((x, y))
            self.kill()
        gorillas_hit = pygame.sprite.spritecollide(self, gorillas, False, pygame.sprite.collide_mask)
        for gorilla in gorillas_hit:
            if gorilla != player:
                loc = pygame.sprite.collide_mask(gorilla, self)
                x = gorilla.rect.x + loc[0]
                y = gorilla.rect.y + loc[1]
                Boom((x, y), True)
                player.celebrate = True
                game_over = True
                self.kill()
        if not main_screen.get_rect().contains(self):
            pygame.draw.rect(main_screen, (255, 0, 0, 125), (int(self.pos[0]), 5, 20, 3))
            if self.pos[0] < -20 or self.pos[0] > SCREEN_WIDTH + 20:
                self.kill()
        if not len(bananas):
            swap_turns()
            del self
            return
        self.move()
        self.rotate()
        self.mask = pygame.mask.from_surface(self.image)

    def rotate(self):
        self.angle = (self.angle + 30 * self.spin) % 360
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        self.rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))

    def move(self):
        t = (game_timer - self.start_time) / (FRAME_RATE / 3)
        x = self.x + self.xv * t - (.5 * (self.wind / 5) * t ** 2)
        y = self.y - ((self.yv * t) - (0.5 * self.gravity * t ** 2))
        self.pos = (x, y)


class HitPixel(pygame.sprite.Sprite):

    def __init__(self, xy=(0, 0), size=5, alpha_fade=5):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((random.randrange(2, size), random.randrange(2, size)))
        self.image.fill(random.choice(PIXEL_COLORS))
        self.rect = self.image.get_rect()
        self.angle = random.random() * (2 * math.pi)
        self.rect.center = (int(xy[0]), int(xy[1]))
        self.speed = random.random() * 12
        self.image.set_alpha(255)
        self.alpha_fade = alpha_fade
        self.start_time = game_timer
        pixels.add(self)

    def update(self, *args):
        """
        if self.rect.x > SCREEN_WIDTH - self.image.get_width() or self.rect.x < 0:
            self.angle = math.pi - self.angle
        if self.rect.y > SCREEN_HEIGHT - self.image.get_height() or self.rect.y < 0:
            self.angle *= -1
        """
        self.rect.centerx += int(self.speed * math.cos(self.angle))
        self.rect.centery += int(self.speed * math.sin(self.angle) + (2**((game_timer - self.start_time)//6)))
        self.image.set_alpha(self.image.get_alpha() - self.alpha_fade)
        if self.image.get_alpha() <= 0:
            self.kill()
            del self


# PYGAME INIT #
pygame.init()
clock = pygame.time.Clock()
main_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GORILLAS")
TIME_START = pygame.time.get_ticks()
GAME_FONT = pygame.font.SysFont(None, 20)

# CUSTOM EVENTS #
MY_EVENT = pygame.USEREVENT + 0

# GAME SETTINGS
game_timer = 0
game_over = False

# GAME IMAGES #
GORILLA_DOWN = makeSurfaceFromASCII(GameImages.GOR_DOWN_ASCII, GORILLA_COLOR)
GORILLA_LEFT = makeSurfaceFromASCII(GameImages.GOR_LEFT_ASCII, GORILLA_COLOR)
GORILLA_RIGHT = makeSurfaceFromASCII(GameImages.GOR_RIGHT_ASCII, GORILLA_COLOR)
BANANA_UP = makeSurfaceFromASCII(GameImages.BAN_UP_ASCII, BANANA_COLOR)
SUN_NORMAL = makeSurfaceFromASCII(GameImages.SUN_NORMAL_ASCII, SUN_COLOR)
SUN_SHOCKED = makeSurfaceFromASCII(GameImages.SUN_SHOCKED_ASCII, SUN_COLOR)
RETICULE = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.circle(RETICULE, (0, 255, 0), (10, 10), 10, 2)
pygame.draw.line(RETICULE, (0, 255, 0), (10, 0), (10, 20), 3)
pygame.draw.line(RETICULE, (0, 255, 0), (0, 10), (20, 10), 3)

# SPRITE GROUPS #
gorillas = pygame.sprite.RenderPlain()
buildings = pygame.sprite.RenderPlain()
suns = pygame.sprite.GroupSingle()
bananas = pygame.sprite.GroupSingle()
booms = pygame.sprite.GroupSingle()
pixels = pygame.sprite.RenderPlain()

# players #
player1 = Gorilla(on_left=True)
player2 = Gorilla(on_left=False)
player = None
sun = Sun()


def setup_game():
    total_width = 0
    while total_width != SCREEN_WIDTH:
        if SCREEN_WIDTH - total_width <= 160:
            building = Building(SCREEN_WIDTH - total_width)
        else:
            building = Building()
        building.rect.bottomleft = (total_width, SCREEN_HEIGHT - 40)
        total_width += building.image.get_width()

    player1.position(buildings.sprites()[random.randrange(1, 2)].rect.midtop)
    player2.position(buildings.sprites()[random.randrange(-3, -2)].rect.midtop)

    swap_turns()


def swap_turns():
    global player
    if player and player == player1:
        player = player2
    else:
        player = player1
    if not player.is_dead:
        player.turn = True
    sun.reset()


def fireworks():
    x = random.randrange(100, SCREEN_WIDTH-100)
    y = random.randrange(50, SCREEN_HEIGHT//3)
    for i in range(60):
        HitPixel((x, y))


def main():
    global game_timer, player

    setup_game()

    done = False
    while not done:
        # GAME CLOCK #
        clock.tick(FRAME_RATE)
        game_timer += 1

        # EVENT HANDLER #
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if game_over:
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if game_over:
                    return

            """"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                player2.turn = False
                player = player1
                player.turn = True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                player1.turn = False
                player = player2
                player.turn = True
            """

            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left-click
                    xy = pygame.mouse.get_pos()
                    for i in range(60):
                        HitPixel(xy)

        # KEY-PRESS HANDLER #
        keys = pygame.key.get_pressed()
        if player and player.turn and not game_over:
            if keys[pygame.K_RIGHT]:
                player.aim_right()
            if keys[pygame.K_LEFT]:
                player.aim_left()
            if keys[pygame.K_SPACE]:
                player.power_up()
            if not keys[pygame.K_SPACE] and player.velocity > 0:
                player.throw(player.velocity)

        if game_over and game_timer % FRAME_RATE == 0:
            fireworks()

        # SCREEN UPDATES #
        main_screen.fill(SKY_COLOR)

        # SPRITE UPDATES #
        suns.update()
        bananas.update()
        gorillas.update()
        buildings.update()
        booms.update()
        pixels.update()

        # DRAW SPRITES #
        suns.draw(main_screen)
        buildings.draw(main_screen)
        gorillas.draw(main_screen)
        bananas.draw(main_screen)
        booms.draw(main_screen)
        pixels.draw(main_screen)

        pygame.display.update()

    # CLEAN UP & QUIT #

    pygame.quit()


# START #
if __name__ == "__main__":
    main()
