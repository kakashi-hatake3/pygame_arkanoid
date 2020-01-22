import pygame
import sys
import os
pygame.init()
WIDTH = 400
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 250
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
over = False
BLOCK_W = 100
BLOCK_H = 30
SPACE = 30
RADIUS = 10
PLANK_W = 100
PLANK_H = 30
FLAG_LOSE = False


def load_image(name, colorkey=None):
    fullname = os.path.join("data", name)
    image = pygame.image.load(fullname).convert()
    return image


class Ball(pygame.sprite.Sprite):
    image = load_image('ball.png')
    image.set_colorkey((255, 255, 255))

    def __init__(self, sprites, x, y):
        super().__init__(sprites)

        self.image = Ball.image

        self.rect = self.image.get_rect()

        self.dx = 0
        self.dy = 0

        self.sprites = sprites

        self.x = x
        self.y = y

        self.rect.x = x
        self.rect.y = y

    def update(self, *args):

        self.rect.x += self.dx

        self.rect.y += self.dy

        if self.rect.x < 0 or self.rect.x + RADIUS > WIDTH:

            self.dx = -self.dx

        elif self.rect.y < 0:

            self.dy = -self.dy

        elif self.rect.y + RADIUS > HEIGHT:

            lose()

        for i in self.sprites.sprites():
            if type(i).__name__ == 'Block' or type(i).__name__ == 'Plank':
                if (i.rect.collidepoint((self.rect.x, self.rect.y)) and
                    i.rect.collidepoint((self.rect.x + RADIUS, self.rect.y))) or \
                        (i.rect.collidepoint((self.rect.x + RADIUS, self.rect.y + RADIUS)) and
                         i.rect.collidepoint((self.rect.x, self.rect.y + RADIUS))):
                    self.dy = -self.dy
                    i.click()
                elif (i.rect.collidepoint((self.rect.x, self.rect.y)) and
                    i.rect.collidepoint((self.rect.x, self.rect.y + RADIUS))) or \
                        (i.rect.collidepoint((self.rect.x + RADIUS, self.rect.y)) and
                         i.rect.collidepoint((self.rect.x + RADIUS, self.rect.y + RADIUS))):
                    self.dx = -self.dx
                    i.click()
                elif i.rect.collidepoint((self.rect.x, self.rect.y)) or \
                    i.rect.collidepoint((self.rect.x + RADIUS, self.rect.y)) or \
                        i.rect.collidepoint((self.rect.x + RADIUS, self.rect.y + RADIUS)) or \
                         i.rect.collidepoint((self.rect.x, self.rect.y + RADIUS)):
                    r = i.rect.clip(self.rect)
                    if r.width == 0 and r.height == 0:
                        continue
                    elif r.width > r.height:
                        self.dy = -self.dy
                    elif r.width < r.height:
                        self.dx = -self.dx
                    else:
                        self.dx, self.dy = -self.dx, -self.dy
                    i.click()

    def back(self, x):
        self.rect.x = x
        self.rect.y = self.y

        self.dx = 0
        self.dy = 0


class Block(pygame.sprite.Sprite):
    def __init__(self, sprites, x, y, name, lifes):
        super().__init__(sprites)
        self.image = block_images[name]
        self.rect = self.image.get_rect()

        self.name = name

        self.rect.x = x
        self.rect.y = y

        self.lifes = lifes

        self.sprites = sprites

    def click(self):
        self.lifes -= 1
        if self.lifes == 0:
            self.sprites.remove(self)
        if len(self.sprites) == 2:
            win()


class Plank(pygame.sprite.Sprite):
    image = load_image("plank.png")
    image.set_colorkey((255, 255, 255))

    def __init__(self, sprites, x, y):
        super().__init__(sprites)
        self.x = x
        self.y = y

        self.image = Plank.image

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEMOTION:
            if args[0].pos[0] + PLANK_W <= WIDTH:
                self.rect.x = args[0].pos[0]
            else:
                self.rect.x = WIDTH - PLANK_W

    def click(self):
        pass


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["НАЖМИТЕ ЛЮБУЮ КНОПКУ", "ДЛЯ НАЧАЛА ИГРЫ"]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))

    screen.blit(fon, (0, 0))

    font = pygame.font.Font(None, 30)

    text_coord = 50

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))

        intro_rect = string_rendered.get_rect()
        text_coord += 10

        intro_rect.top = text_coord
        intro_rect.x = 10

        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()

        clock.tick(FPS)


def start_game(level_numb):

    pygame.mixer.music.load('data/test.mp3')
    pygame.mixer.music.play(-1)

    map = load_level(level_numb)

    generate_level(map)

    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                terminate()

            elif over:

                return
            if bal.dx == 0 and bal.dy == 0 and event.type == pygame.MOUSEBUTTONDOWN:
                bal.dx = 1
                bal.dy = -1

            if bal.dx == 0 and bal.dy == 0 and event.type == pygame.MOUSEMOTION:
                bal.rect.x = plank.rect.x + PLANK_W // 2

            plank.update(event)

        all_sprites.update()

        all_sprites.draw(screen)

        pygame.display.flip()

        screen.fill((0, 0, 255))

        clock.tick(FPS)


def load_level(level_numb):
    filename = f"data/map_{level_numb}.txt"

    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    global over

    over = False

    x, y = (WIDTH - len(level[0]) * (BLOCK_W + SPACE) + SPACE) // 2,\
           (HEIGHT - len(level) * (BLOCK_H + SPACE) + SPACE) // 2
    for i in range(len(level)):

        for j in range(len(level[i])):

            if level[i][j] in ['1', '2', '3']:

                Block(all_sprites, x + j * (BLOCK_W + SPACE),
                      y + i * (BLOCK_H + SPACE), 'block_' + level[i][j], int(level[i][j]))


def end_screen():
    global level_numb

    intro_text = ["ВЫ ВЫИГРАЛИ!", 'ЧТОБЫ НАЧАТЬ ЗАНОВО', "НАЖМИТЕ ЛЮБУЮ КНОПКУ"]
    fon = pygame.transform.scale(load_image('end_fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))

        intro_rect = string_rendered.get_rect()
        text_coord += 10

        intro_rect.top = text_coord

        intro_rect.x = 10
        text_coord += intro_rect.height

        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                terminate()

            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:

                level_numb = 0

                return

        pygame.display.flip()

        clock.tick(FPS)


def lose():
    global level_numb

    global over

    global bal

    over = True

    bal.back(plank.rect.x + PLANK_W // 2)

    intro_text = ["ВЫ ПРОИГРАЛИ!", 'ЧТОБЫ НАЧАТЬ ЗАНОВО', "НАЖМИТЕ ЛЮБУЮ КНОПКУ"]

    fon = pygame.transform.scale(load_image('end_fon.png'), (WIDTH, HEIGHT))

    screen.blit(fon, (0, 0))

    font = pygame.font.Font(None, 30)

    text_coord = 50

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('red'))

        intro_rect = string_rendered.get_rect()
        text_coord += 10

        intro_rect.top = text_coord

        intro_rect.x = 10
        text_coord += intro_rect.height

        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                terminate()

            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:

                level_numb = 0

                return

        pygame.display.flip()

        clock.tick(FPS)


def win():
    global over

    global level_numb

    global bal

    over = True

    bal.back(plank.rect.x + PLANK_W // 2)

    if level_numb == 4:
        end_screen()


bal = Ball(all_sprites, WIDTH // 2 - RADIUS // 2, HEIGHT - PLANK_H - RADIUS)

plank = Plank(all_sprites, WIDTH // 2 - PLANK_W // 2, HEIGHT - PLANK_H)

bal.back(plank.rect.x + PLANK_W // 2)

block_images = {'block_1': load_image('block_1.png'), 'block_2': load_image('block_2.png'),
                'block_3': load_image('block_3.png')}
start_screen()

level_numb = 0

while level_numb < 5:

    level_numb += 1

    start_game(level_numb)


if level_numb == 5:
    win()


over = True
