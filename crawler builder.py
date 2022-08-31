from PIL import Image
import pygame
import random
import sys
import os

# setup
pygame.init()
screen = pygame.display.set_mode((1080, 720), pygame.HWACCEL, pygame.HWSURFACE)
pygame.display.set_caption('bleh')
#pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# constants
MOVESPEED = 16
IDLE = 'idle'
POINTING = 'pointing'
ATTACK = 'attack'
TILESIZE = 64
EMPTY = 'empty'
SET = 'set'

# colors
backgroundColor = (25,30,35)
guiColor1 = (30, 80, 160)
guiColor2 = (50, 100, 180)
guiColor3 = (50, 100, 180, 128)
guiTextColor = (255, 255, 255)

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

def getNormalImage(path):
    return pygame.image.load(path)

def getUiImage(pos):
    return pygame.image.load(f'ui\\{pos.x}_{pos.y}.png')

def getCharImage(pos):
    return pygame.image.load(f'characters\\{pos.x}_{pos.y}.png')

def drawRect(rect, color):
    s = pygame.Surface((rect[2:]), pygame.SRCALPHA)
    s.fill(color)
    screen.blit(s, rect[:2])

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.coords = (x, y)

idleMouseImage = getUiImage(Pos(26, 19))
pointingMouseImage = getUiImage(Pos(4, 25))
attackMouseImage = getUiImage(Pos(10, 25))
brushImage = getNormalImage('ui\\brush.png')
eraserImage = getNormalImage('ui\\eraser.png')
emptyTile = getImage(Pos(0, 5))
pygame.display.set_icon(attackMouseImage)

playerImg = getCharImage(Pos(1, 11))
playerMoveSensitivity = 64
screenCenterX = screen.get_width() / 2
screenCenterY = screen.get_height() / 2

# useful functions

def drawText(text, pos, font, color, anchor='center'):
    text = font.render(text, True, color)
    textRect = text.get_rect()
    if anchor == 'center':
        textRect.center = pos.coords
    elif anchor == 'topleft':
        textRect.topleft = pos.coords
    screen.blit(text, textRect)

def openFile(f):
    """
    Purpose is to read files and interpret them into groundTile, decorTile, ghostTile, and textLayer layers.

    Example of file:

    TownChunk1, It's a chunk of town, 0_5, 0_4...

    First two lines are the name of the file, second is a description. The files shouldn't be too big, so no need for compression.
    """
    pass

def saveFile(groundtile, decorTile, ghostTile, signLayer):
    """
    Purpose is to save world data into files for the actual game to open and read.
    """
    pass

# gui classes

class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.touchingMouse = False
    def draw(self):
        if self.touchingMouse:
            pass
        else:
            pygame.draw.rect(screen, guiColor1, self.rect)
            drawText(self.text, Pos(self.rect.centerx, self.rect.centery), self.font, guiTextColor)
    def check(self, mouse):
        coords = pygame.mouse.get_pos()
        self.touchingMouse = self.rect.collidepoint(mouse.coords)

class ImageButton:
    def __init__(self, rect, image):
        self.rect = pygame.Rect(rect)
        self.image = image
        self.touchingMouse = False
        self.selected = False
    def draw(self):
        if self.touchingMouse or self.selected:
            drawRect(self.rect, guiColor3)
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image, self.rect)
    def check(self, mouse):
        self.touchingMouse = self.rect.collidepoint(mouse.coords)

# helpful classes

class Camera:
    def __init__(self, pos):
        self.pos = pos
    def move(self, keyboard):
        if keyboard.w:
            self.pos.y += MOVESPEED
        elif keyboard.s:
            self.pos.y -= MOVESPEED

        if keyboard.a:
            self.pos.x += MOVESPEED
        elif keyboard.d:
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
        self.e = False

class Mouse:
    def __init__(self):
        self.state = IDLE
        self.previousLeftClick = False
        self.leftClick = False
        self.middleClick = False
        self.rightClick = False
        self.scrollUp = False
        self.scrollDown = False
        self.pos = Pos(0, 0)
        self.coords = (0,0)
    def check(self):
        self.leftClick, self.middleClick, self.rightClick, self.scrollUp, self.scrollDown = pygame.mouse.get_pressed(num_buttons=5)
        self.pos.x, self.pos.y = pygame.mouse.get_pos()
        self.coords = pygame.mouse.get_pos()
    def fix(self):
        self.previousLeftClick = self.leftClick
        self.leftClick = None

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
            self.rect = pygame.Rect(self.pos.coords, (TILESIZE, TILESIZE))
            self.image = image
            self.solid = solid
            self.type = type
        else:
            self.pos = pos
            self.rect = pygame.Rect(self.pos.coords, (TILESIZE, TILESIZE))
            self.image = preset.image
            self.solid = preset.solid
            self.type = preset.type
            self.layer = preset.layer
            self.name = preset.name
            self.tags = preset.tags
    def draw(self, camera):
        if self.image != None:
            screen.blit(self.image, (self.pos.x + camera.pos.x, self.pos.y + camera.pos.y))
            self.rect = pygame.Rect((self.pos.x + camera.pos.x, self.pos.y + camera.pos.y), (TILESIZE, TILESIZE))
        else:
            return

class TileData:
    def __init__(self, image, solid, type, layer, name, tags):
        self.image = image
        self.solid = solid
        self.type = type
        self.layer = layer
        self.name = name
        self.tags = tags

# loop init
keyboard = Keyboard()
mouse = Mouse()
camera = Camera(Pos(0,0))
groundTiles = []
usefulGroundTiles = []
renderTiles = []
gridX = 32
gridY = 32
for x in range(gridX):
    for y in range(gridY):
        groundTiles.append(Tile(Pos(x*TILESIZE, y*TILESIZE), emptyTile, False, EMPTY))

brushButton = ImageButton((15, 15, 50, 50), brushImage)
eraserButton = ImageButton((65, 15, 50, 50), eraserImage)
buttons = [brushButton, eraserButton]
toolbarHeight = 80

running = True
while running:
    # clears screen
    screen.fill(backgroundColor)

    # important class updates
    keyboard.check()
    mouse.check()
    camera.move(keyboard)

    if keyboard.quit:
        running = False
        break

    brushButton.check(mouse)
    eraserButton.check(mouse)

    # get useful ground tiles
    usefulGroundTiles = []
    for t in groundTiles:
        if t.rect.centerx > -TILESIZE / 2 and t.rect.centerx < screen.get_width() + TILESIZE / 2 and t.rect.y > -TILESIZE and t.rect.y < screen.get_height():
            usefulGroundTiles.append(t)

    if mouse.leftClick:
        # tile calculations
        for t in usefulGroundTiles: # add tiles
            if t.rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) and t.type == EMPTY and pygame.mouse.get_pos()[1] > toolbarHeight and brushButton.selected:
                t.image = getImage(Pos(5,0))
                t.type = SET

        for t in usefulGroundTiles: # remove tiles
            if t.rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) and t.type == SET and pygame.mouse.get_pos()[1] > toolbarHeight and eraserButton.selected:
                t.image = None
                t.type = EMPTY

        # button calculations
        if brushButton.touchingMouse: # brush button
            brushButton.selected = True
        elif pygame.mouse.get_pos()[1] < toolbarHeight:
            brushButton.selected = False

        if eraserButton.touchingMouse: # eraser button
            eraserButton.selected = True
        elif pygame.mouse.get_pos()[1] < toolbarHeight:
            eraserButton.selected = False

    """if mouse.rightClick:
        for t in groundTiles:
            if t.rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) and t.type == SET and pygame.mouse.get_pos()[1] > 99:
                t.image = emptyTile
                t.type = EMPTY"""

    for t in groundTiles:
        if t.image != None:
            t.draw(camera)

    drawRect((0,0,screen.get_width(),toolbarHeight), guiColor1)
    brushButton.draw()
    eraserButton.draw()

    keyboard.keyFix()
    mouse.fix()
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
