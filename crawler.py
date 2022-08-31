# imports
import pygame
import random
import sys
import os

"""
Settings:

Simulation/computation distance:
    Minimum (simulates tiles that are on screen)
    Normal (simulates tiles within a reasonable distance)
    Maximum (simulates tiles and collisions all the way up to the edge of the chunks)

Movement Sensitivity (has little to no affect on gameplay, just visual)
"""

# setup
pygame.init()
screen = pygame.display.set_mode((1080, 720), pygame.HWSURFACE)
pygame.display.set_caption('crawler')
#pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# constants
MOVESPEED = 4
IDLE = 'idle'
POINTING = 'pointing'
ATTACK = 'attack'
TILESIZE = 64

# fonts
font5 = pygame.font.FontType('font.ttf', 5)
font10 = pygame.font.FontType('font.ttf', 10)
font15 = pygame.font.FontType('font.ttf', 15)
font20 = pygame.font.FontType('font.ttf', 20)
font30 = pygame.font.FontType('font.ttf', 30)
font40 = pygame.font.FontType('font.ttf', 40)
font50 = pygame.font.FontType('font.ttf', 50)

# useful images
def getImage(pos):
    return pygame.image.load(f'tiles\\{pos.x}_{pos.y}.png')

def getUiImage(pos):
    return pygame.image.load(f'ui\\{pos.x}_{pos.y}.png')

def getCharImage(pos):
    return pygame.image.load(f'characters\\{pos.x}_{pos.y}.png')

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.bool = (x, y)

flowerBedImage = getImage(Pos(3, 7))

idleMouseImage = getUiImage(Pos(26, 19))
pointingMouseImage = getUiImage(Pos(4, 25))
attackMouseImage = getUiImage(Pos(10, 25))
pygame.display.set_icon(attackMouseImage)

playerImg = getCharImage(Pos(0, 10))
playerMoveSensitivity = 64
screenCenterX = screen.get_width() / 2
screenCenterY = screen.get_height() / 2

# useful functions

def drawText(text, pos, font, color, anchor='center'):
    text = font.render(text, True, color)
    textRect = text.get_rect()
    if anchor == 'center':
        textRect.center = pos.bool
    elif anchor == 'topleft':
        textRect.topleft = pos.bool
    screen.blit(text, textRect)

# base classes

class Camera:
    def __init__(self, pos):
        self.pos = pos
    def move(self, keyboard, player):
        if keyboard.w and player.hitbox.colliderect(player.rectUp):
            self.pos.y += MOVESPEED
        elif keyboard.s and player.hitbox.colliderect(player.rectDown):
            self.pos.y -= MOVESPEED

        if keyboard.a and player.hitbox.colliderect(player.rectLeft):
            self.pos.x += MOVESPEED
        elif keyboard.d and player.hitbox.colliderect(player.rectRight):
            self.pos.x -= MOVESPEED

class Keyboard:
    def __init__(self):
        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.quit = False
        self.e = False
    def check(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == pygame.KEYDOWN:
                # movement key handling
                if event.key == pygame.K_w:
                    self.w = True
                elif event.key == pygame.K_s:
                    self.s = True
                elif event.key == pygame.K_a:
                    self.a = True
                elif event.key == pygame.K_d:
                    self.d = True
                
                # special key handling
                if event.key == pygame.K_e:
                    self.e = True
            if event.type == pygame.KEYUP:
                # movement key handling
                if event.key == pygame.K_w:
                    self.w = False
                elif event.key == pygame.K_s:
                    self.s = False
                elif event.key == pygame.K_a:
                    self.a = False
                elif event.key == pygame.K_d:
                    self.d = False
                
                # special key handling
                if event.key == pygame.K_e:
                    self.e = False
    def keyFix(self):
        if self.e: self.e = False

class Mouse:
    def __init__(self):
        self.state = IDLE
        self.leftClick = 0
        self.middleClick = 0
        self.rightClick = 0
    def check(self):
        self.leftClick, self.middleClick, self.rightClick = pygame.mouse.get_pressed()
    def draw(self):
        if pygame.mouse.get_focused():
            if self.state == IDLE:
                mousePos = pygame.mouse.get_pos()
                screen.blit(idleMouseImage, mousePos)
            elif self.state == POINTING:
                mousePos = pygame.mouse.get_pos()
                screen.blit(pointingMouseImage, (mousePos[0]-12, mousePos[1]-4))
            elif self.state == ATTACK:
                mousePos = pygame.mouse.get_pos()
                screen.blit(attackMouseImage, mousePos)
        

# sprite classes
class Obj:
    def __init__(self, rect, image):
        self.rect = rect
        self.image = image
    def draw(self, cam):
        drawPos = [rect.x + cam.pos.x, rect.y + cam.pos.y]
        screen.blit(drawPos, self.image)

class Tile:
    def __init__(self, pos, image, solid, type, preset=None):
        if preset == None:
            self.pos = pos
            self.rect = pygame.Rect(self.pos.bool, (32, 32))
            self.image = image
            self.solid = solid
            self.type = type
    def draw(self, camera):
        screen.blit(self.image, (self.pos.x + camera.pos.x, self.pos.y + camera.pos.y))
    def onScreen(self):
        if pygame.Rect((0, 0, screen.get_width(), screen.get_height())).colliderect(self.rect.move(camera.pos.x, camera.pos.y)):
            return True
        else:
            return False

class Player:
    def __init__(self):
        self.pos = None
        self.image = playerImg
        self.pos = Pos(screen.get_width()/2 - self.image.get_width()/2, screen.get_height()/2 - self.image.get_height()/2)
        self.hitbox = pygame.Rect(screen.get_width()/2 - self.image.get_width()/2, screen.get_height()/2 - self.image.get_height()/2, self.image.get_width(), self.image.get_height())
        self.rectUp = pygame.Rect(screenCenterX - playerMoveSensitivity, screenCenterY - playerMoveSensitivity, playerMoveSensitivity * 2, 4)
        self.rectDown = pygame.Rect(screenCenterX - playerMoveSensitivity, screenCenterY + playerMoveSensitivity - 4, playerMoveSensitivity * 2, 4)
        self.rectLeft = pygame.Rect(screenCenterX - playerMoveSensitivity, screenCenterY - playerMoveSensitivity, 4, playerMoveSensitivity * 2)
        self.rectRight = pygame.Rect(screenCenterX + playerMoveSensitivity, screenCenterY - playerMoveSensitivity, 4, playerMoveSensitivity * 2)
        
    def draw(self):
        screen.blit(self.image, (self.pos.x, self.pos.y))
    def move(self, keyboard):
        # up and down
        if keyboard.w and not self.hitbox.colliderect(self.rectUp):
            self.pos.y -= MOVESPEED
            self.hitbox = self.hitbox.move(0, -MOVESPEED)
        elif keyboard.s and not self.hitbox.colliderect(self.rectDown):
            self.pos.y += MOVESPEED
            self.hitbox = self.hitbox.move(0, MOVESPEED)

        # left and right
        if keyboard.a and not self.hitbox.colliderect(self.rectLeft):
            self.pos.x -= MOVESPEED
            self.hitbox = self.hitbox.move(-MOVESPEED, 0)
        elif keyboard.d and not self.hitbox.colliderect(self.rectRight):
            self.pos.x += MOVESPEED
            self.hitbox = self.hitbox.move(MOVESPEED, 0)

# demo loop
tiles = []
for x in range(20):
    for y in range(20):
        #tiles.append(Tile(Pos((x)*TILESIZE, (y)*TILESIZE), random.choice([getImage(Pos(5, 0)), getImage(Pos(5, 1))]), False, 1))
        tiles.append(Tile(Pos((x)*TILESIZE, (y)*TILESIZE), getImage(Pos(3, 7)), False, 1))
usefulTiles = []

keyboard = Keyboard()
camera = Camera(Pos(0, 0))
player = Player()

running = True
while running:
    # clears screen
    screen.fill((25,30,35))
    
    # checks for key presses
    keyboard.check()
    camera.move(keyboard, player)
    if keyboard.quit:
        running = False
    
    # updates tiles
    usefulTiles = []
    """for t in tiles:
        if t.onScreen():
            usefulTiles.append(t)"""
    for t in tiles:
        t.draw(camera)

    # player things
    player.move(keyboard)
    player.draw()

    # updates display
    keyboard.keyFix()
    clock.tick(60)
    pygame.display.update()

pygame.quit()
sys.exit()
