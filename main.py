import pygame
import copy
from field import field
from math import pi as PI

pygame.init()

WIDTH, HEIGHT = 1000, 600
BASE_Y_SIZE = HEIGHT // 32  # Y size of each tile
BASE_X_SIZE = (WIDTH - 350) // 30  # X size of each tile
DIST = 10  # distance between pacman and something

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

# ghost images
blinky_img = pygame.transform.scale(pygame.image.load('red.png'), (24, 24))
pinky_img = pygame.transform.scale(pygame.image.load('pink.png'), (24, 24))
inky_img = pygame.transform.scale(pygame.image.load('blue.png'), (24, 24))
clyde_img = pygame.transform.scale(pygame.image.load('orange.png'), (24, 24))

spooked_img = pygame.transform.scale(pygame.image.load('powerup.png'), (24, 24))
dead_img = pygame.transform.scale(pygame.image.load('dead.png'), (24, 24))

directs = {'right': 0, 'left': 1, 'up': 2, 'down': 3}
direction = directs['up']
animation_ctrl = 0
pac_x, pac_y = 302, 427
pac_center = [pac_x + 12, pac_y + 12]
pac_speed = 2
score = 0
power = False
pow_timer = 0

# valid turns [right, left, up, down]
valid_turns = [False, False, False, False]
eaten_ghost = [False, False, False, False]
wanted_dir = directs['up']


class Ghost:
    def __init__(self, x, y, dirt, img, delay):
        self.x = x
        self.y = y
        self.center = [self.x + 12, self.y + 12]
        self.direction = dirt
        self.img = img
        self.target = pac_center
        self.delay = delay
        self.dead = False
        self.wait = True
        self.in_the_box = True
        self.eaten = False
        self.valid_turns = [False, False, False, False]
        self.speed = 1
        self.draw()

    def draw(self):
        if self.dead:
            screen.blit(dead_img, (self.x, self.y))
        elif power and not self.eaten:
            screen.blit(spooked_img, (self.x, self.y))
        else:
            screen.blit(self.img, (self.x, self.y))

    def check_collisions(self):
        global play

        self.valid_turns = [False, False, False, False]
        if self.dead:
            self.valid_turns = [True, True, True, True]
        self.center = [self.x + 12, self.y + 12]

        if self.center[0] // 30 < 20:
            if level[(self.center[1] - DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] == 9:
                self.valid_turns[directs['up']] = True
            if level[self.center[1] // BASE_Y_SIZE][(self.center[0] - DIST) // BASE_X_SIZE] < 3:
                self.valid_turns[directs['left']] = True
            if level[self.center[1] // BASE_Y_SIZE][(self.center[0] + DIST) // BASE_X_SIZE] < 3:
                self.valid_turns[directs['right']] = True
            if level[(self.center[1] + DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] < 3 or (
                    level[(self.center[1] + DIST) // BASE_Y_SIZE][
                        self.center[0] // BASE_X_SIZE] == 9 and (self.in_the_box or self.dead)):
                self.valid_turns[directs['down']] = True
            if level[(self.center[1] - DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] < 3 or (
                    level[(self.center[1] - DIST) // BASE_Y_SIZE][
                        self.center[0] // BASE_X_SIZE] == 9 and (self.in_the_box or self.dead)):
                self.valid_turns[directs['up']] = True

            if self.direction in (directs['up'], directs['down']):
                if BASE_X_SIZE - 2 <= self.center[0] % BASE_X_SIZE <= BASE_X_SIZE + 2:
                    if level[(self.center[1] + DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] < 3 or (
                            level[(self.center[1] + DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] == 9 and (
                            self.in_the_box or self.dead)):
                        self.valid_turns[directs['down']] = True
                if BASE_X_SIZE - 2 <= self.center[0] % BASE_X_SIZE <= BASE_X_SIZE + 2:
                    if level[(self.center[1] - DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] < 3 or (
                            level[(self.center[1] - DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] == 9 and (
                            self.in_the_box or self.dead)):
                        self.valid_turns[directs['up']] = True
                if BASE_Y_SIZE - 2 <= self.center[1] % BASE_Y_SIZE <= BASE_Y_SIZE + 2:
                    if level[self.center[1] // BASE_Y_SIZE][(self.center[0] - BASE_X_SIZE) // BASE_X_SIZE] < 3 or (
                            level[self.center[1] // BASE_Y_SIZE][
                                (self.center[0] - BASE_X_SIZE) // BASE_X_SIZE] == 9 and (
                                    self.in_the_box or self.dead)):
                        self.valid_turns[directs['down']] = True
                if BASE_X_SIZE - 2 <= self.center[0] % BASE_X_SIZE <= BASE_X_SIZE + 2:
                    if level[self.center[1] // BASE_Y_SIZE][(self.center[0] + BASE_X_SIZE) // BASE_X_SIZE] < 3 or (
                            level[self.center[1] // BASE_Y_SIZE][
                                (self.center[0] + BASE_X_SIZE) // BASE_X_SIZE] == 9 and (
                                    self.in_the_box or self.dead)):
                        self.valid_turns[directs['up']] = True

            if self.direction in (directs['left'], directs['right']):
                if BASE_X_SIZE - 2 <= self.center[0] % BASE_X_SIZE <= BASE_X_SIZE + 2:
                    if level[(self.center[1] + DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] < 3 or (
                            level[(self.center[1] + DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] == 9 and (
                            self.in_the_box or self.dead)):
                        self.valid_turns[directs['down']] = True
                if BASE_X_SIZE - 2 <= self.center[0] % BASE_X_SIZE <= BASE_X_SIZE + 2:
                    if level[(self.center[1] - DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] < 3 or (
                            level[(self.center[1] - DIST) // BASE_Y_SIZE][self.center[0] // BASE_X_SIZE] == 9 and (
                            self.in_the_box or self.dead)):
                        self.valid_turns[directs['up']] = True
                if BASE_Y_SIZE - 2 <= self.center[1] % BASE_Y_SIZE <= BASE_Y_SIZE + 2:
                    if level[self.center[1] // BASE_Y_SIZE][(self.center[0] - DIST) // BASE_X_SIZE] < 3 or (
                            level[self.center[1] // BASE_Y_SIZE][(self.center[0] - DIST) // BASE_X_SIZE] == 9 and (
                            self.in_the_box or self.dead)):
                        self.valid_turns[directs['down']] = True
                if BASE_X_SIZE - 2 <= self.center[0] % BASE_X_SIZE <= BASE_X_SIZE + 2:
                    if level[self.center[1] // BASE_Y_SIZE][(self.center[0] + DIST) // BASE_X_SIZE] < 3 or (
                            level[self.center[1] // BASE_Y_SIZE][(self.center[0] + DIST) // BASE_X_SIZE] == 9 and (
                            self.in_the_box or self.dead)):
                        self.valid_turns[directs['up']] = True
        else:
            self.valid_turns[directs['right']] = True
            self.valid_turns[directs['left']] = True

        if self.x < -50:
            self.x = 635
        elif self.x > 640:
            self.x = -45

        if 232 < self.x < 374 and 237 < self.y < 300:
            self.in_the_box = True
        else:
            self.in_the_box = False

        if ((self.center[0] - pac_center[0]) ** 2 + (self.center[1] - pac_center[1]) ** 2) ** 0.5 <= DIST:
            if power:
                self.dead = True
            else:
                play = False

        if self.dead and self.in_the_box:
            self.dead = False
            self.speed = 1

        if len(list(filter(lambda x: x, self.valid_turns))) == 0:
            self.dead = True
            self.speed = 6

    def move(self):
        global directs

        # calculating
        if self.direction == directs['right']:
            if self.target[0] > self.x and self.valid_turns[directs['right']]:
                self.x += self.speed
            elif not self.valid_turns[directs['right']]:
                if self.target[1] > self.y and self.valid_turns[directs['down']]:
                    self.direction = directs['down']
                    self.y += self.speed
                elif self.target[1] < self.y and self.valid_turns[directs['up']]:
                    self.direction = directs['up']
                    self.y -= self.speed
                elif self.target[0] < self.x and self.valid_turns[directs['left']]:
                    self.direction = directs['left']
                    self.x -= self.speed
                elif self.valid_turns[directs['down']]:
                    self.direction = directs['down']
                    self.y += self.speed
                elif self.valid_turns[directs['up']]:
                    self.direction = directs['up']
                    self.y -= self.speed
                elif self.valid_turns[directs['left']]:
                    self.direction = directs['left']
                    self.x -= self.speed
            elif self.valid_turns[directs['right']]:
                if self.target[1] > self.y and self.valid_turns[directs['down']]:
                    self.direction = directs['down']
                    self.y += self.speed
                if self.target[1] < self.y and self.valid_turns[directs['up']]:
                    self.direction = directs['up']
                    self.y -= self.speed
                else:
                    self.x += self.speed
        elif self.direction == directs['left']:
            if self.target[1] > self.y and self.valid_turns[directs['down']]:
                self.direction = directs['down']
                self.y += self.speed
            elif self.target[0] < self.x and self.valid_turns[directs['left']]:
                self.direction = directs['left']
                self.x -= self.speed
            elif not self.valid_turns[directs['left']]:
                if self.target[1] > self.y and self.valid_turns[directs['down']]:
                    self.direction = directs['down']
                    self.y += self.speed
                elif self.target[1] < self.y and self.valid_turns[directs['up']]:
                    self.direction = directs['up']
                    self.y -= self.speed
                elif self.target[0] > self.x and self.valid_turns[directs['right']]:
                    self.direction = directs['right']
                    self.x += self.speed
                elif self.valid_turns[directs['down']]:
                    self.direction = directs['down']
                    self.y += self.speed
                elif self.valid_turns[directs['up']]:
                    self.direction = directs['up']
                    self.y -= self.speed
                elif self.valid_turns[directs['right']]:
                    self.direction = directs['right']
                    self.x += self.speed
            elif self.valid_turns[directs['left']]:
                if self.target[1] > self.y and self.valid_turns[directs['down']]:
                    self.direction = directs['down']
                    self.y += self.speed
                if self.target[1] < self.y and self.valid_turns[directs['up']]:
                    self.direction = directs['up']
                    self.y -= self.speed
                else:
                    self.x -= self.speed
        elif self.direction == directs['up']:
            if self.target[0] < self.x and self.valid_turns[directs['left']]:
                self.direction = directs['left']
                self.x -= self.speed
            elif self.target[1] < self.y and self.valid_turns[directs['up']]:
                self.direction = directs['up']
                self.y -= self.speed
            elif not self.valid_turns[directs['up']]:
                if self.target[0] > self.x and self.valid_turns[directs['right']]:
                    self.direction = directs['right']
                    self.x += self.speed
                elif self.target[0] < self.x and self.valid_turns[directs['left']]:
                    self.direction = directs['left']
                    self.x -= self.speed
                elif self.target[1] > self.y and self.valid_turns[directs['down']]:
                    self.direction = directs['down']
                    self.y += self.speed
                elif self.valid_turns[directs['left']]:
                    self.direction = directs['left']
                    self.x -= self.speed
                elif self.valid_turns[directs['right']]:
                    self.direction = directs['right']
                    self.x += self.speed
            elif self.valid_turns[directs['up']]:
                if self.target[0] > self.x and self.valid_turns[directs['right']]:
                    self.direction = directs['right']
                    self.x += self.speed
                elif self.target[0] < self.x and self.valid_turns[directs['left']]:
                    self.direction = directs['left']
                    self.x -= self.speed
                else:
                    self.y -= self.speed
        elif self.direction == directs['down']:
            if self.target[1] > self.y and self.valid_turns[directs['down']]:
                self.direction = directs['down']
                self.y += self.speed
            elif not self.valid_turns[directs['down']]:
                if self.target[0] > self.x and self.valid_turns[directs['right']]:
                    self.direction = directs['right']
                    self.x += self.speed
                elif self.target[0] < self.x and self.valid_turns[directs['left']]:
                    self.direction = directs['left']
                    self.x -= self.speed
                elif self.target[1] < self.y and self.valid_turns[directs['up']]:
                    self.direction = directs['up']
                    self.y -= self.speed
                elif self.valid_turns[directs['up']]:
                    self.direction = directs['up']
                    self.y -= self.speed
                elif self.valid_turns[directs['left']]:
                    self.direction = directs['left']
                    self.x -= self.speed
                elif self.valid_turns[directs['right']]:
                    self.direction = directs['right']
                    self.x += self.speed
            elif self.valid_turns[directs['down']]:
                if self.target[0] > self.x and self.valid_turns[directs['right']]:
                    self.direction = directs['right']
                    self.x += self.speed
                elif self.target[0] < self.x and self.valid_turns[directs['left']]:
                    self.direction = directs['left']
                    self.x -= self.speed
                else:
                    self.y += self.speed

            if self.x < -50:
                self.x = 635
            elif self.x > 640:
                self.x = -45

    def make_target(self):
        target = [0, 0]
        if self.wait:
            target = [300, 275]
        elif self.in_the_box and not self.dead:
            target = [300, 260]
        elif self.dead:
            target = [300, 275]
            self.speed = 6
        elif power:
            if pac_x > 300:
                target[0] = 45
            else:
                target[0] = 578
            if pac_y > 300:
                target[1] = 45
            else:
                target[1] = 549
        else:
            target = pac_center
        self.target = target

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
    if pac_center[0] // 30 < 20:

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

            if BASE_Y_SIZE // 2 - 2 <= pac_center[1] % BASE_Y_SIZE <= BASE_Y_SIZE // 2 + 2 and pac_x < 600:
                if level[pac_center[1] // BASE_Y_SIZE][(pac_center[0] - DIST) // BASE_X_SIZE] < 3:
                    valid_turns[1] = True
                if level[pac_center[1] // BASE_Y_SIZE][(pac_center[0] + DIST) // BASE_X_SIZE] < 3:
                    valid_turns[0] = True
    else:
        valid_turns[0] = True
        valid_turns[1] = True


def move_pac():
    global pac_x, pac_y, direction

    if direction == directs['left'] and valid_turns[directs['left']]:
        pac_x -= pac_speed
    if direction == directs['right'] and valid_turns[directs['right']]:
        pac_x += pac_speed
    if direction == directs['up'] and valid_turns[directs['up']]:
        pac_y -= pac_speed
    if direction == directs['down'] and valid_turns[directs['down']]:
        pac_y += pac_speed


def check_collisions():
    global score, power, pow_timer, eaten_ghost

    if 0 < pac_x < 610:
        if level[pac_center[1] // BASE_Y_SIZE][pac_center[0] // BASE_X_SIZE] == 1:
            level[pac_center[1] // BASE_Y_SIZE][pac_center[0] // BASE_X_SIZE] = 0
            score += 10
        if level[pac_center[1] // BASE_Y_SIZE][pac_center[0] // BASE_X_SIZE] == 2:
            level[pac_center[1] // BASE_Y_SIZE][pac_center[0] // BASE_X_SIZE] = 0
            score += 50
            power = True
            pow_timer = 0
            eaten_ghosts = [False, False, False, False]


def draw_ui():
    score_text = font.render(f"Score: {score:>04}", True, 'white')
    screen.blit(score_text, (880, 10))
    if power:
        power_text = font.render(f"POWER!!!", True, 'blue')
        screen.blit(power_text, (879, 35))


blinky = Ghost(290, 270, directs['up'], blinky_img, 150)
pinky = Ghost(280, 280, directs['up'], pinky_img, 100)
inky = Ghost(300, 280, directs['up'], inky_img, 400)
clyde = Ghost(300, 280, directs['down'], clyde_img, 0)
ghosts = [blinky, pinky, inky, clyde]

play = True
while play:
    timer.tick(fps)
    if animation_ctrl < 19:
        animation_ctrl += 1
    else:
        animation_ctrl = 0
    if power:
        if pow_timer < 600:
            pow_timer += 1
        else:
            power = False
            pow_timer = 0
            eaten_ghost = [False, False, False, False]

    screen.fill('black')
    draw_field(level)
    draw_ui()
    draw_pacman()
    pac_center = [pac_x + 12, pac_y + 12]
    check_collisions()

    for ghost in ghosts:
        if ghost.delay > 0:
            ghost.delay -= 1
        else:
            ghost.wait = False
        ghost.draw()
        ghost.make_target()
        ghost.check_collisions()
        ghost.move()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                wanted_dir = directs['right']
            if event.key == pygame.K_LEFT:
                wanted_dir = directs['left']
            if event.key == pygame.K_UP:
                wanted_dir = directs['up']
            if event.key == pygame.K_DOWN:
                wanted_dir = directs['down']

    for some_dir in directs.values():
        if wanted_dir == some_dir and valid_turns[some_dir]:
            direction = some_dir

    if pac_x < -50:
        pac_x = 635
    elif pac_x > 640:
        pac_x = -45
    check_pos()
    move_pac()

    dots = [1 in line or 2 in line for line in level]
    if not any(dots):
        play = False

    pygame.display.flip()
dots = [1 in line or 2 in line for line in level]
if any(dots):
    text = font.render(f"LOSE!", True, 'red')
else:
    text = font.render(f"WIN!", True, 'green')
screen.blit(text, (879, 60))
pygame.display.flip()
pygame.time.wait(3000)
pygame.quit()
