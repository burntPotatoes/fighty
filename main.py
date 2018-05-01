import parse
import pygame
import math
import sys
import random
import time
from pathfinder import ai

class Enemy:
    def __init__(self):
        pass


# appends the folder/name.png thingy to the file, instead of 1just name
def load_pics(folder, name):
    location = folder + name + ".png"
    return pygame.image.load(location).convert_alpha()


# more stackoverflow stuff
def slow_music():
    pass

# finds grid location from coordinates
# GRID SPECIFICATIONS: center of walls start 100 + 37 from the left (100 is taken up by the ui)
#                      and 0 from the top. It is 12x8, first one and last two never have walls
#                      Each wall is 75x75, and is in total a
#                      900x600 grid
def grid_location(x, y):
    loc = [0, 0]
    # x
    loc[0] = int((x - 100)//75)
    loc[1] = int(y//75)
    if loc[0] > 11:
        loc[0] = 11
    elif loc[0] < 0:
        loc[0] = 0
    if loc[1] > 7:
        loc[1] = 7
    elif loc[1] < 0:
        loc[1] = 0

    return loc

# move to the next path tile thing
def move_next_path(curEnemy, egridloc, epath, espeed,):
    if len(epath) > 1:
        # check all 4 directions
        # epath is (y, x) but egridloc is (x, y) cuz reasons
        if egridloc[0] < epath[1][1]:  # move left
            enemyX[curEnemy] += espeed * timeSlow[1]
        elif egridloc[0] > epath[1][1]:  # move right
            enemyX[curEnemy] -= espeed * timeSlow[1]
        elif egridloc[1] > epath[1][0]:  # move up
            enemyY[curEnemy] -= espeed * timeSlow[1]
        elif egridloc[1] < epath[1][0]:  # move down
            enemyY[curEnemy] += espeed * timeSlow[1]


# some stackoverflow bs ¯\_(ツ)_/¯
def rot_center(image, angle):
    """rotate a Surface, maintaining position."""
    loc = image.get_rect().center  # rot_image is not defined
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite


def draw_crosshair(cX, cY, dis, inAcc):
    # more spacing = more inaccurate
    spacing = dis / 55 * inAcc + 3
    # right, left, up, down
    if relCD[curWpn] <= 0:
        pygame.draw.circle(screen, crossCol, (cX, cY), 3)
        pygame.draw.line(screen, crossCol, (cX + spacing - 1, cY), (cX + spacing + 3, cY))
        pygame.draw.line(screen, crossCol, (cX - spacing, cY), (cX - spacing - 3, cY))
        pygame.draw.line(screen, crossCol, (cX, cY - spacing), (cX, cY - spacing - 3))
        pygame.draw.line(screen, crossCol, (cX, cY + spacing - 1), (cX, cY + spacing + 3))

    else:  # draw an X during reload
        pygame.draw.line(screen, crossCol, (cX - 10, cY - 10), (cX + 10, cY + 10))
        pygame.draw.line(screen, crossCol, (cX + 10, cY - 10), (cX - 10, cY + 10))


# this calculates angles and shit for the bullets
def calc_bullet(bX, bY, acc):
    global curBul, bulTarX, bulTarY, bulProj, bulAng
    bulAng[curBul] = (math.atan2(-(bulTarY[curBul] - bY), bulTarX[curBul] - bX))
    if acc > 0:
        randomAng = math.radians(random.uniform(-acc, acc))  # add some randomness to the bullets
        bulAng[curBul] = bulAng[curBul] + randomAng

    bulTarY[curBul] = - math.sin(bulAng[curBul]) * bulProj[curBul]
    bulTarX[curBul] = math.cos(bulAng[curBul]) * bulProj[curBul]


# this creates the health bar and mana bar
def create_UI(hp, mp):
    screen.fill(UIHp, (20, 30, 20, hp * 20))
    pygame.draw.rect(screen, [0, 0, 0], [20, 30, 20, 200], 2)
    pygame.draw.line(screen, [0, 0, 0], [20, 130], [40, 130], 3)
    for i in range(10):
        pygame.draw.line(screen, [0, 0, 0], [20, 30 + 20 * i], [40, 30 + 20 * i])

    screen.fill(UIMana, (60, 30, 20, int(mp * 2)))
    pygame.draw.rect(screen, [0, 0, 0], [60, 30, 20, 200], 2)


# This function creates the little weapon sprites for switching weapons / displaying ammo
def weapon_UI(img, ammo, max_ammo, num, selected):  # num = weapon from 0 - 2 (top to bottom)
    global relCD
    screen.blit(img, (12, 250 + num * 120))
    if selected == num:
        pygame.draw.rect(screen, (0, 0, 0), (8, 250 + num * 120, 84, 70), 1)

    # ammo display
    ammo_words = str(ammo) + " / " + str(max_ammo)
    if relCD[num] > 0:
        ammo_words = "REL " + str(round(relCD[num] / 60, 1))
    elif ammo <= -1:
        ammo_words = "INF"
    ammo_text = ammoFont.render(ammo_words , False, (0, 0, 0))
    screen.blit(ammo_text, (50 - len(ammo_words) * 4.5, 330 + num * 120))


# This moves the player in the 4 cardinal directions + diagonally
def move_player(buttons, pSpd):
    global posX, posY
    num = [0, 0]

    # redoing dis shit, num[0] = x movement, num[1] = y movement
    if buttons[pygame.K_w]:
        if not wall_collision(posX, posY - (pSpd / 2), 18):
            num[0] = - pSpd
    elif buttons[pygame.K_s]:
        if not wall_collision(posX, posY + (pSpd / 2), 18):
            num[0] = pSpd
    if buttons[pygame.K_d]:
        if not wall_collision(posX + (pSpd / 2), posY, 18):
            num[1] = pSpd
    elif buttons[pygame.K_a]:
        if not wall_collision(posX - (pSpd / 2), posY, 18):
            num[1] = - pSpd

    # move da player
    if num[0] and num[1] != 0:
        posX += num[1] * 0.7
        posY += num[0] * 0.7
    else:
        posX += num[1]
        posY += num[0]

    # boundaries
    if posX < 120:
        posX = 120
    elif posX > disLength - 20:
        posX = disLength - 20
    if posY < 20:
        posY = 20
    elif posY > disHeight - 20:
        posY = disHeight - 20


# checks for a wall collision given x and y coordinates
def wall_collision(x, y, hitbox):
    global wallRandom, wallRandomY
    for i in range(len(wallRandom)):
        if wallRandom[i] + hitbox + 37 > x > wallRandom[i] - hitbox - 37 and \
                        wallRandomY[i] + hitbox + 37 > y > wallRandomY[i] - hitbox - 37:
            return True
    return False

# check if a fired bullet hits an enemy. x and y are the bullet coords, enemy_x and enemy_y are an array of enemy locations
# returns -1 if no hit, otherwise returns the list location of the hit enemy
def enemy_collision(x, y, enemy_x, enemy_y, enemy_active, box_e, box_bul):
    global numEnemy
    for i in range(numEnemy):
        if enemy_x[i] - box_e[i] / 2 - box_bul < x < enemy_x[i] + box_e[i] / 2 + box_bul and \
                        enemy_y[i] - box_e[i] / 2 - box_bul < y < enemy_y[i] + box_e[i] / 2 + box_bul and enemy_active:
            return i
    return -1

def spawn_enemy():
    pass

def draw_map(wall_col, rand, randY):
    pygame.draw.rect(screen, wall_col, (102, 2, 896, 596), 5)
    screen.fill((45, 45, 45), rect = (disLength - 7, 75, 7, 75))
    screen.fill((45, 45, 45), rect = (disLength - 7, disHeight - 150, 7, 75))
    for i in range(len(rand)):
        screen.fill(wall_col, rect = (rand[i] - 38, randY[i] - 38, 76, 76))


def main_menu():
    pass


'''
|= = = = = = = = = = = = = = = = MAIN CODE STARTS NOW = = = = = = = = = = = = = = = = =|

TODO LIST:
    - add enemies
        - pathfinding and map generation in 75x75 grid
        pathfinding ideas:
        check which quadrant the player is in
        If low hp or need backup, find cover and run away, otherwise, advance.
        Add randomness so that enemies split up and sometimes surround the player.d
    - add barriers DONE (mostly)
    - add better visuals on hit for bullets (maybe 2 or 3 frames of effects instead of 1 pic)
    - add knife/ LIGHT SABRE (deflects bullets!)
    - multiple levels?!
    - sound effects

BUGS: ¯\_(ツ)_/¯
    - no bugs obviously all features

'''

# initiate pygame and cursors`
pygame.mixer.pre_init(22050, -16, 6, 512)
pygame.mixer.init()
pygame.init()
pygame.font.init()
time.sleep(1)

cursor = pygame.cursors.compile(pygame.cursors.textmarker_strings)
pygame.mouse.set_cursor(*pygame.cursors.diamond)
pygame.mouse.set_visible(False)


# setup the screen and main clock
disLength = 1000
disHeight = 600
screen = pygame.display.set_mode((disLength, disHeight))
pygame.display.set_caption("shooty")
clock = pygame.time.Clock()

ammoFont = pygame.font.SysFont('Courier New', 15)

# background and objects like walls
backCol = [240, 240, 240]
UIBod = [125, 125, 225]
UICol = [220, 240, 240]
UISlow = [190, 200, 220]
UIHp = [250, 70, 70]
UIMana = [100, 100, 240]
wallCol = [120, 120, 120]
crossCol = [0, 40, 10]

# GRID SPECIFICATIONS: center of walls start 125 + 37 from the left (100 is taken up by the ui)
#                      and 0 from the top. It is 11x8, first one and last two never have walls
#                      Ends at last 50 units from the right. Each wall is 75x75, and is in total a
#                      825x600 grid
wallRandom = []
wallRandomY = []
wallCoords = []  # walls on the 12x8 array
wallCount = 0  # number of walls in total, should not exceed 8
wallCountC = 0  # number of walls in a single column, should not exceed 3
ran = 0
wallGrid = []

for i in range(12):  # x axis
    wallGrid.append([])
    wallCountC = 0
    for k in range(8):  # y axis
        # better walls[tm]
        if random.randint(0, 60) + ran >= 56 and 2 <= i <= 10 and wallCountC < 3 and wallCount < 9:
            wallGrid[i].append(1)
            wallCountC += 1
            wallCount += 1
            ran = 5
            wallRandom.append(100 + i * 75 + 37)  # center of the wall X and Y
            wallRandomY.append(k * 75 + 37)
            wallCoords.append([i, k])
        else:
            wallGrid[i].append(0)
            ran = 0

# global game variables
level = 0
timescale = 1.0
timeBuffer = [0, 20]  # used so that pressing space doesn't accidentally do it 2 times
timeSlow = [1.0, 1.0]  # self slow, enemy slow

# player variables
playerImg = pygame.image.load("player.png").convert_alpha()
posX = 150.0  # start in the top left corner
posY = 50.0
baseSpeed = 4.5
health = [10, 10]  # min/max hp
mana = [100, 100]  # min/max mana
manaChargeDelay = [0, 30]  # number of ticks of delay before mana starts to recharge
manaUseSpeed = [20, 10]  # usage rate / recharge rate per second
fireCD = 0.0  # used when shooting
wpnAmmo = [parse.wAmmo[0], parse.wAmmo[1]]
wpnInAcc = [parse.wAcc[0], parse.wAcc[1]]
relCD = [0, 0]  # used by weapon 1 and weapon 2 when reloading.
curWpn = 0
speed = baseSpeed * parse.wSpeed[curWpn]  # this changes based on the weapon
atkSound = pygame.mixer.Sound(parse.wSound[curWpn])

# for ai
gridLoc = [0, 0]

# effect pictures and stuff
expSmall = pygame.image.load("effects/exp_small.png").convert_alpha()

# player bullet variables
bulImg = [parse.wBul] * 12  # should probably add different pictures
effImg = [expSmall] * 12
effImg2 = [""] * 12
bulX = [-50.0] * 12
bulY = [-50.0] * 12
active = [0] * 12
bulDmg = [0] * 12
bulProj = [0.0] * 12
bulTarX = [-50.0] * 12
bulTarY = [-50.0] * 12
bulAng = [0.0] * 12
bulExpSound = [parse.wExpSound[curWpn]] * 12
bulHitSound = [parse.wHitSound[curWpn]] * 12
curBul = 0

outOfAmmoSound = pygame.mixer.Sound('sounds/noammo.wav')

# 2nd frame of effects (optional)
for i in range(len(parse.wEff)):
    try:
        parse.wEff2.append(load_pics("effects/", "1" + parse.wEff[i]))
    except pygame.error:
        parse.wEff2.append("")
# weapon sprites and effects
for i in range(len(parse.wImg)):
    parse.wImg[i] = load_pics("weapons/", parse.wImg[i])
for i in range(len(parse.wBul)):
    parse.wBul[i] = load_pics("projectiles/", parse.wBul[i])
for i in range(len(parse.wEff)):
    parse.wEff[i] = load_pics("effects/", parse.wEff[i])

# ENEMY STUFF
# global stats
numEnemy = 6  # add more if needed!

# individual stats
for i in range(len(parse.eImg)):
    parse.eImg[i] = load_pics("enemy_pic/", parse.eImg[i])

enemyReEvaluate = [0, 10]  # every 10 ticks re evaluate the path chosen

enemyHP = [parse.eHP[0]] * numEnemy
enemyMaxHP = enemyHP * numEnemy  # used for the HP bar
enemyImg = [parse.eImg[0]] * numEnemy
enemyBox = [parse.eBox[0]] * numEnemy
enemySpeed = [parse.eSpeed[0]] * numEnemy
enemyX = [disLength + 40] * numEnemy
enemyY = [75 + 37] * numEnemy
enemyGridLoc = grid_location(75 + 37, disLength - 10) * numEnemy
enemyTar = [[0, 0]] * numEnemy  # an array of tile positions, where the enemy wants to move
enemyNextTar = [[0, 0]] * numEnemy  # which x, y direction enemy should move to (e.g. [-1,0] is West)
enemyPath = [[]] * numEnemy
enemyActive = [False] * numEnemy

enemySpawn = 0
# load sounds, channel 0 is reserved for music, all others used for sound effects
ingameMusic = pygame.mixer.Sound('sounds/background music.wav')
pygame.mixer.set_num_channels(10)
channel0 = pygame.mixer.Channel(0)
channel0.play(ingameMusic, loops=-1)
# slow motion music

# ========= GAME LOGIC ========= #

# get the weapons that the player has equipped
EqWpnName = ["Sub Machine Gun", "Pistol"]  # the 2 weapons used
for i in range(1, -1, -1):
    if EqWpnName[i] in parse.wName:
        ArrayLoc = parse.wName.index(EqWpnName[i])
        # theres DEFINITELY a better way of doing dis
        parse.wName = [parse.wName[ArrayLoc]] + parse.wName
        parse.wDmg = [parse.wDmg[ArrayLoc]] + parse.wDmg
        parse.wRate = [parse.wRate[ArrayLoc]] + parse.wRate
        parse.wProj = [parse.wProj[ArrayLoc]] + parse.wProj
        parse.wAmmo = [parse.wAmmo[ArrayLoc]] + parse.wAmmo
        parse.wRel = [parse.wRel[ArrayLoc]] + parse.wRel
        parse.wAcc = [parse.wAcc[ArrayLoc]] + parse.wAcc
        parse.wCoil = [parse.wCoil[ArrayLoc]] + parse.wCoil
        parse.wImg = [parse.wImg[ArrayLoc]] + parse.wImg
        parse.wBul = [parse.wBul[ArrayLoc]] + parse.wBul
        parse.wSpeed = [parse.wSpeed[ArrayLoc]] + parse.wSpeed
        parse.wEff = [parse.wEff[ArrayLoc]] + parse.wEff
        parse.wEff2 = [parse.wEff2[ArrayLoc]] + parse.wEff2
        parse.wSound = [parse.wSound[ArrayLoc]] + parse.wSound
        parse.wExpSound = [parse.wExpSound[ArrayLoc]] + parse.wExpSound
        parse.bulHitSound = [parse.wHitSound[curWpn]] + parse.wHitSound
        parse.wCost = [parse.wCost[ArrayLoc]] + parse.wCost
        parse.wOwned = [parse.wOwned[ArrayLoc]] + parse.wOwned
    else:
        print("A weapon was not found in the data!!! F")

wpnName = [parse.wName[0], parse.wName[1]]  # the 2 weapons used
wpnAmmo = [parse.wAmmo[0], parse.wAmmo[1]]
wpnInAcc = [parse.wAcc[0], parse.wAcc[1]]
relCD = [0, 0]  # used by weapon 1 and weapon 2 when reloading.
curWpn = 0
speed = baseSpeed * parse.wSpeed[curWpn]  # this changes based on the weapon
atkSound = pygame.mixer.Sound(parse.wSound[curWpn])

while True:
    screen.fill(backCol)

    enemySpawn -= 1 * timeSlow[1]
    # tick down timers, recharge mana
    enemyReEvaluate[0] += -1
    for i in range(2):
        if relCD[i] > 0 and curWpn == i:
            relCD[i] += -1 * timeSlow[0]
        elif relCD[i] > 0 and curWpn != i:
            relCD[i] = parse.wRel[i] * 60
        if -1 <relCD[i] <= 0:
            wpnAmmo[i] = parse.wAmmo[i]
            relCD[i] += -1

    timeBuffer[0] += -1
    fireCD += -1 * timeSlow[0]

    # use mana if ability is active
    if timeSlow[0] != 1 or timeSlow[1] != 1:
        mana[0] -= manaUseSpeed[0] / 60
    else:  # recharge mana after the delay
        manaChargeDelay[0] += -1
        if manaChargeDelay[0] <= 0 and mana[0] < mana[1]:
            mana[0] += manaUseSpeed[1] / 60
    if mana[0] <= 0:
        timeSlow[0] = 1.0
        timeSlow[1] = 1.0

    # ------------ ENEMY STUFF ------------ #

    # enemy spawning
    # remember to set max HP here!
    if enemySpawn <= 0:
        # lower spawn rates if lots of enemies already there
        numEnemyAlive = enemyActive.count(True)
        enemySpawn = random.randint(100, 150) + (numEnemyAlive * random.randint(15, 25))
        if numEnemyAlive < numEnemy:
            # gets the next dead enemy in list
            next = enemyActive.index(False)

            # reset stats
            enemyHP[next] = parse.eHP[0]
            enemyMaxHP[next] = 8 # used for the HP bar
            enemyImg[next] = parse.eImg[0]
            enemyBox[next] = parse.eBox[0]
            enemySpeed[next] = parse.eSpeed[0]

            # spawn enemy, randomize location
            spawnLoc = random.randint(0, 1)
            if spawnLoc == 0:
                enemyX[next] = disLength + 40
                enemyY[next] = 75 + 37
            elif spawnLoc == 1:
                enemyX[next] = disLength + 40
                enemyY[next] = disHeight - 75 - 37

            enemyActive[next] = True

    # Every 0.5sec, evaluate a path for every enemy to the player
    # path finding for the enemies, using some shady algorithm from online
    if enemyReEvaluate[0] <= 0:
        gridLoc = grid_location(posX, posY)

        # reset the delay, checks once per 0.5s
        enemyReEvaluate[0] = enemyReEvaluate[1]
        # loop through all of the enemies and get da paths
        for i in range(numEnemy):
            if enemyActive[i]:
                enemyGridLoc[i] = grid_location(enemyX[i], enemyY[i])
                #print("loc:", enemyGridLoc)
                enemyPath[i] = ai.find_path(wallGrid, enemyGridLoc[i], gridLoc)
                #print("path:", enemyPath)

    # enemy movement
    for i in range(numEnemy):
        if enemyActive[i]:
            # do everything
            move_next_path(i, enemyGridLoc[i], enemyPath[i], enemySpeed[i])
            # draw!
            screen.blit(enemyImg[i], (enemyX[i] - enemyBox[i] / 2, enemyY[i] - enemyBox[i] / 2))
            pygame.draw.rect(screen, (0, 0, 0), (enemyX[i] - 25, enemyY[i] - 40, 50, 10), 1)

    # ------------ PLAYER STUFF ------------ #
    pressed = pygame.key.get_pressed()

    # lose inaccuracy from recoil
    for i in range(2):
        if wpnInAcc[i] > parse.wAcc[i]:
            wpnInAcc[i] = wpnInAcc[i] - timeSlow[0] * ((wpnInAcc[i] - parse.wAcc[i]) * 0.03) - 0.01
        else:
            wpnInAcc[i] = parse.wAcc[i]

    # SLOW DOWN TIME...
    if timeBuffer[0] <= 0 and pressed[pygame.K_SPACE]:
        timeBuffer[0] = timeBuffer[1]
        if timeSlow[0] != 1 or timeSlow[1] != 1:
            timeSlow = [1.0, 1.0]
        else:
            timeSlow = [1.0, 0.3]  # self slow, enemy slow
            manaChargeDelay[0] = 30

    # move player and display player
    move_player(pressed, speed * timeSlow[0])
    screen.blit(playerImg, (posX - 20, posY - 20))

    # switch weapon (knife, wpn 0, wpn 1)
    if pressed[pygame.K_1]:  # knife later
        curWpn = 0
        atkSound = pygame.mixer.Sound(parse.wSound[curWpn])
        speed = baseSpeed * parse.wSpeed[curWpn]
        if fireCD <= 15:
            fireCD = 15
    elif pressed[pygame.K_2]:
        curWpn = 1
        atkSound = pygame.mixer.Sound(parse.wSound[curWpn])
        speed = baseSpeed * parse.wSpeed[curWpn]
        if fireCD <= 15:
            fireCD = 15

    # ------------ SHOOTING AND BULLET STUFF ------------ #
    # shooting
    mousePos = pygame.mouse.get_pos()
    mouse = pygame.mouse.get_pressed()

    # manual reload
    if pressed[pygame.K_r] and wpnAmmo[curWpn] < parse.wAmmo[curWpn]:
        relCD[curWpn] = parse.wRel[curWpn] * 60
    # shoot
    if mouse[0] == 1 and fireCD <= 0 and relCD[curWpn] <= 0:
        curBul += 1
        if curBul >= 12:
            curBul = 0
        # set some bullet variables
        bulX[curBul] = posX
        bulY[curBul] = posY
        active[curBul] = 1
        bulTarX[curBul] = mousePos[0]
        bulTarY[curBul] = mousePos[1]
        bulDmg[curBul] = parse.wDmg[curWpn]
        bulProj[curBul] = parse.wProj[curWpn]
        # TRIG YAY
        calc_bullet(bulX[curBul], bulY[curBul], wpnInAcc[curWpn])
        bulImg[curBul] = rot_center(parse.wBul[curWpn], math.degrees(bulAng[curBul]))
        effImg[curBul] = parse.wEff[curWpn]
        effImg2[curBul] = parse.wEff2[curWpn]
        # recoil!
        wpnInAcc[curWpn] += parse.wCoil[curWpn]
        # sounds
        atkSound.play()
        bulExpSound[curBul] = pygame.mixer.Sound(parse.wExpSound[curWpn])
        bulHitSound[curBul] = pygame.mixer.Sound(parse.wHitSound[curWpn])

        # set cooldown and automatic reload
        fireCD = 60 / parse.wRate[curWpn]
        wpnAmmo[curWpn] += -1
        if wpnAmmo[curWpn] == 0:
            relCD[curWpn] = parse.wRel[curWpn] * 60  # RELOAD HERE

    # out of ammo sound
    elif mouse[0] == 1 and fireCD <= 0 and relCD[curWpn] > 0:
        outOfAmmoSound.play()
        fireCD = 60 / parse.wRate[curWpn]
        if fireCD > relCD[curWpn]:
            fireCD = relCD[curWpn]

    # displaying and resetting bullets
    for i in range(12):
        if active[i] > 0:
            # check if the bullet hits a wall or enemy, else display it
            gap = int(math.sqrt(bulTarX[i] ** 2 + bulTarY[i] ** 2)) // 10 + 1  # number of times to check for collision
            for j in range(gap):
                # check if the bullet hits a wall
                enemyCheck = enemy_collision(bulX[i], bulY[i], enemyX, enemyY, enemyActive, enemyBox, 2)
                if wall_collision(bulX[i], bulY[i], 2) or bulX[i] + 10 > disLength or bulX[i] < 110 or bulY[i] + 10 > disHeight or bulY[i] < 10:
                    # draw the bullet for one frame before death
                    screen.blit(bulImg[i], (bulX[i] - (center[2] / 2), bulY[i] - (center[3] / 2)))
                    active[i] = -1
                    # change picture to explosion!!!
                    bulImg[i] = effImg[i]
                    bulExpSound[i].play()
                    break
                # check if the bullet hits an enemy
                elif enemyCheck > -1:
                    # effects on enemy (health loss, death check)
                    enemyHP[enemyCheck] -= bulDmg[i]
                    if enemyHP[enemyCheck] <= 0:
                        enemyActive[enemyCheck] = False
                        enemyX[enemyCheck] = disLength + 25
                        enemyY[enemyCheck] = 75 + 37
                    # draw the bullet for one frame before death
                    screen.blit(bulImg[i], (bulX[i] - (center[2] / 2), bulY[i] - (center[3] / 2)))
                    active[i] = -1
                    # change picture to explosion!!!
                    bulImg[i] = effImg[i]
                    bulHitSound[i].play()
                    break
                else:
                    bulX[i] += bulTarX[i] * timeSlow[0] / gap
                    bulY[i] += bulTarY[i] * timeSlow[0] / gap
                    # add hitting enemies here
                if j == gap - 1:
                    center = bulImg[i].get_rect()
                    screen.blit(bulImg[i], (bulX[i] - (center[2]/2), bulY[i] - (center[3]/2)))

    # particle effects for bullets
    for i in range(12):
        if -15 <= active[i] < 0:
            screen.blit(bulImg[i], (bulX[i] - 45, bulY[i] - 45))
            active[i] += -1 * timeSlow[0]
        # second frame effect
        if -6.5 <= active[i] < -5.5 and effImg2[i] != "":
            bulImg[i] = effImg2[i]
            active[i] += -1
        elif -6.5 <= active[i] < -5.5:
            active[i] = -16

    # ------------ UI ELEMENTS ------------ #
    # draw walls and stuff
    draw_map(wallCol, wallRandom, wallRandomY)

    # draw enemy HP bars here so that they go above the stuffs
    for i in range(numEnemy):
        if enemyActive[i]:
            # draw HP bars (red inside then black outline)
            pygame.draw.rect(screen, UIHp, (enemyX[i] - 25, enemyY[i] - 40, enemyHP[i] / enemyMaxHP[i] * 50, 10))
            pygame.draw.rect(screen, (0, 0, 0), (enemyX[i] - 25, enemyY[i] - 40, 50, 10), 1)

    # draw crosshair
    dist = math.sqrt((mousePos[0] - posX) ** 2 + (mousePos[1] - posY) ** 2)
    draw_crosshair(mousePos[0], mousePos[1], dist, wpnInAcc[curWpn])

    # draw UI for slow and not slowed time
    if timeSlow[0] != 1 or timeSlow[1] != 1:
        screen.fill(UISlow, [0, 0, 100, disHeight])
    else:
        screen.fill(UICol, [0, 0, 100, disHeight])
    pygame.draw.rect(screen, UIBod, [1, 1, 100, disHeight - 2], 3)

    # hp bars and stuff
    create_UI(health[0], mana[0])
    weapon_UI(parse.wImg[0], wpnAmmo[0], parse.wAmmo[0], 0, curWpn)
    weapon_UI(parse.wImg[1], wpnAmmo[1], parse.wAmmo[1], 1, curWpn)

    # update display!
    pygame.display.update()

    # should make it 60FPS max
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
