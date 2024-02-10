import pygame
import copy
from field import field
from math import pi as PI

pygame.init()

WIDTH, HEIGHT = 1000, 600
BASE_Y_SIZE = HEIGHT // 32  # Y size of each tile
BASE_X_SIZE = (WIDTH - 350) // 30  # X size of each tile
DIST = 12  # distance between pacman and something

screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)

level = copy.deepcopy(field)
# 0 = empty black rectangle,
# 1 = dot, 2 = big dot,
# 3 = vertical line,
# 4 = horizontal line,
# 5 = top right, 6 = top left, 7 = bot left, 8 = bot right
# 9 = gate

color = "blue"

pac_images = [pygame.transform.scale(pygame.image.load("pac_1.png"), (24, 24)),
              pygame.transform.scale(pygame.image.load("pac_2.png"), (24, 24))]

directs = {'right': 0, 'left': 1, 'up': 2, 'down': 3}
direction = directs['right']
animation_ctrl = 0
pac_x, pac_y = 300, 427
pac_speed = 2

# valid turns [right, left, up, down]
valid_turns = [True, False, False, False]


def draw_field(layout):
    for y in range(len(layout)):
        for x in range(len(layout[y])):
            if level[y][x] == 1:
                pygame.draw.circle(screen, 'white',
                                   (x * BASE_X_SIZE + (0.5 * BASE_X_SIZE), y * BASE_Y_SIZE + (0.5 * BASE_Y_SIZE)), 2.7)
            if level[y][x] == 2:
                pygame.draw.circle(screen, 'white',
                                   (x * BASE_X_SIZE + (0.5 * BASE_X_SIZE), y * BASE_Y_SIZE + (0.5 * BASE_Y_SIZE)), 7)
            if level[y][x] == 3:
                pygame.draw.line(screen, color, (x * BASE_X_SIZE + (0.5 * BASE_X_SIZE), y * BASE_Y_SIZE),
                                 (x * BASE_X_SIZE + (0.5 * BASE_X_SIZE), y * BASE_Y_SIZE + BASE_Y_SIZE), 1)
            if level[y][x] == 4:
                pygame.draw.line(screen, color, (x * BASE_X_SIZE, y * BASE_Y_SIZE + (0.5 * BASE_Y_SIZE)),
                                 (x * BASE_X_SIZE + BASE_X_SIZE, y * BASE_Y_SIZE + (0.5 * BASE_Y_SIZE)), 1)
            if level[y][x] == 5:
                pygame.draw.arc(screen, color,
                                [(x * BASE_X_SIZE - (BASE_X_SIZE * 0.4)) - 2, (y * BASE_Y_SIZE + (0.5 * BASE_Y_SIZE)),
                                 BASE_X_SIZE,
                                 BASE_Y_SIZE],
                                0, PI / 2, 1)
            if level[y][x] == 6:
                pygame.draw.arc(screen, color,
                                [(x * BASE_X_SIZE + (BASE_X_SIZE * 0.5)), (y * BASE_Y_SIZE + (0.5 * BASE_Y_SIZE)),
                                 BASE_X_SIZE, BASE_Y_SIZE],
                                PI / 2, PI, 1)
            if level[y][x] == 7:
                pygame.draw.arc(screen, color,
                                [(x * BASE_X_SIZE + (BASE_X_SIZE * 0.5)), (y * BASE_Y_SIZE - (0.4 * BASE_Y_SIZE)),
                                 BASE_X_SIZE, BASE_Y_SIZE],
                                PI,
                                3 * PI / 2, 1)
            if level[y][x] == 8:
                pygame.draw.arc(screen, color,
                                [(x * BASE_X_SIZE - (BASE_X_SIZE * 0.4)) - 2, (y * BASE_Y_SIZE - (0.4 * BASE_Y_SIZE)),
                                 BASE_X_SIZE,
                                 BASE_Y_SIZE], 3 * PI / 2,
                                2 * PI, 1)
            if level[y][x] == 9:
                pygame.draw.line(screen, 'white', (x * BASE_X_SIZE, y * BASE_Y_SIZE + (0.5 * BASE_Y_SIZE)),
                                 (x * BASE_X_SIZE + BASE_X_SIZE, y * BASE_Y_SIZE + (0.5 * BASE_Y_SIZE)), 3)


def draw_pacman():
    if direction == directs['right']:
        screen.blit(pac_images[animation_ctrl // 10], (pac_x, pac_y))
    elif direction == directs['left']:
        screen.blit(pygame.transform.flip(pac_images[animation_ctrl // 10], True, False), (pac_x, pac_y))
    elif direction == directs['up']:
        screen.blit(pygame.transform.rotate(pac_images[animation_ctrl // 10], 90), (pac_x, pac_y))
    elif direction == directs['down']:
        screen.blit(pygame.transform.rotate(pac_images[animation_ctrl // 10], 270), (pac_x, pac_y))


def check_pos():
    global valid_turns
    valid_turns = [False, False, False, False]
    if pac_center[0] // 30 < 29:

        # you always should be able to turn backwards
        if direction == directs['left']:
            if level[pac_center[1] // BASE_Y_SIZE][(pac_center[0] - DIST) // BASE_X_SIZE] < 3:
                valid_turns[1] = True
        if direction == directs['right']:
            if level[pac_center[1] // BASE_Y_SIZE][(pac_center[0] + DIST) // BASE_X_SIZE] < 3:
                valid_turns[0] = True
        if direction == directs['up']:
            if level[(pac_center[1] + DIST) // BASE_Y_SIZE][(pac_center[0]) // BASE_X_SIZE] < 3:
                valid_turns[3] = True
        if direction == directs['down']:
            if level[(pac_center[1] - DIST) // BASE_Y_SIZE][(pac_center[0]) // BASE_X_SIZE] < 3:
                valid_turns[2] = True

        # checking if you are able to turn by 90 degrees
        if direction in (directs['up'], directs['down']):
            if BASE_X_SIZE // 2 - 2 <= pac_center[0] % BASE_X_SIZE <= BASE_X_SIZE // 2 + 2:
                if level[(pac_center[1] + DIST) // BASE_Y_SIZE][pac_center[0] // BASE_X_SIZE] < 3:
                    valid_turns[3] = True
                if level[(pac_center[1] - DIST) // BASE_Y_SIZE][pac_center[0] // BASE_X_SIZE] < 3:
                    valid_turns[2] = True

            if BASE_Y_SIZE // 2 - 2 <= pac_center[1] % BASE_Y_SIZE <= BASE_Y_SIZE // 2 + 2:
                if level[pac_center[1] // BASE_Y_SIZE][(pac_center[0] - BASE_X_SIZE) // BASE_X_SIZE] < 3:
                    valid_turns[1] = True
                if level[pac_center[1] // BASE_Y_SIZE][(pac_center[0] + BASE_X_SIZE) // BASE_X_SIZE] < 3:
                    valid_turns[0] = True

        if direction in (directs['left'], directs['right']):
            if BASE_X_SIZE // 2 - 2 <= pac_center[0] % BASE_X_SIZE <= BASE_X_SIZE // 2 + 2:
                if level[(pac_center[1] + BASE_Y_SIZE) // BASE_Y_SIZE][pac_center[0] // BASE_X_SIZE] < 3:
                    valid_turns[3] = True
                if level[(pac_center[1] - BASE_Y_SIZE) // BASE_Y_SIZE][pac_center[0] // BASE_X_SIZE] < 3:
                    valid_turns[2] = True

            if BASE_Y_SIZE // 2 - 2 <= pac_center[1] % BASE_Y_SIZE <= BASE_Y_SIZE // 2 + 2:
                if level[pac_center[1] // BASE_Y_SIZE][(pac_center[0] - DIST) // BASE_X_SIZE] < 3:
                    valid_turns[1] = True
                if level[pac_center[1] // BASE_Y_SIZE][(pac_center[0] + DIST) // BASE_X_SIZE] < 3:
                    valid_turns[0] = True
    else:
        valid_turns[0] = True
        valid_turns[1] = True


def move_pac():
    global pac_x, pac_y

    if direction == directs['left'] and valid_turns[directs['left']]:
        pac_x -= pac_speed
    if direction == directs['right'] and valid_turns[directs['right']]:
        pac_x += pac_speed
    if direction == directs['up'] and valid_turns[directs['up']]:
        pac_y -= pac_speed
    if direction == directs['down'] and valid_turns[directs['down']]:
        pac_y += pac_speed


play = True
while play:
    timer.tick(fps)
    if animation_ctrl < 19:
        animation_ctrl += 1
    else:
        animation_ctrl = 0

    screen.fill('black')
    draw_field(level)
    draw_pacman()
    pac_center = [pac_x + 12, pac_y + 12]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction = directs['right']
            if event.key == pygame.K_LEFT:
                direction = directs['left']
            if event.key == pygame.K_UP:
                direction = directs['up']
            if event.key == pygame.K_DOWN:
                direction = directs['down']
    check_pos()
    move_pac()

    pygame.display.flip()
pygame.quit()
