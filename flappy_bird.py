import pygame
import neat
import time
import os
import random
import pickle
pygame.font.init()


BIRD_IMGS = [pygame.image.load(os.path.join("images", "bird1.png")),
             pygame.image.load(os.path.join("images", "bird2.png")),
             pygame.image.load(os.path.join("images", "bird3.png"))]

PIPE_IMG = pygame.image.load(os.path.join("images", "pipe.png"))

BASE_IMG = pygame.image.load(os.path.join("images", "base.png"))

BG_IMG = pygame.image.load(os.path.join("images", "bg.png"))

WIN_WIDTH = BG_IMG.get_width()
WIN_HEIGHT = BG_IMG.get_height()

VEL = 3

STAT_FONT = pygame.font.SysFont("comicsans", 30)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x + 20
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -2
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + 0.3*self.tick_count**2
        if d >= 8:
            d = 8

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = round(WIN_HEIGHT/5)

    def __init__(self, x):
        self.x = x + 30
        self.height = 0
        self.gap = 100
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, WIN_HEIGHT-180)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False


class Base:
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= VEL
        self.x2 -= VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(round(WIN_WIDTH/2)-50, round(WIN_HEIGHT/2))
    base = Base(WIN_HEIGHT - 70)
    pipes = [Pipe(WIN_WIDTH)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYUP:
                bird.jump()
        bird.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            if pipe.collide(bird):
                print("LOSE")
                run = False

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= WIN_HEIGHT - 70:
            pass

        base.move()
        draw_window(win, [bird], pipes, base, score)
    pygame.quit()
    quit()


def eval_genomes(genomes, config, training=True):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(round(WIN_WIDTH/2)-50, round(WIN_HEIGHT/2)))
        g.fitness = 0
        ge.append(g)

    base = Base(WIN_HEIGHT - 70)
    pipes = [Pipe(WIN_WIDTH)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate(
                (bird.y, abs(bird.y-pipes[pipe_ind].height), abs(bird.y-pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= WIN_HEIGHT - 70 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score)

        if score > 20 and training:
            break


def replay_genome(config_path, genome_path="winner.pkl"):
    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    eval_genomes(genomes, config, False)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(eval_genomes, 50)
    with open("winner.pkl", "wb") as output:
        pickle.dump(winner, output)


def menu(config_path):
    run = True
    BUTTON_HEIGHT = 50
    BUTTON_WIDTH = 100
    clock = pygame.time.Clock()
    while run:
        win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        win.blit(BG_IMG, (0, 0))
        #text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if WIN_WIDTH/2 + BUTTON_WIDTH/2 > mouse[0] > WIN_WIDTH/2 - BUTTON_WIDTH/2 and WIN_HEIGHT/2 + BUTTON_HEIGHT/2 > mouse[1] > WIN_HEIGHT/2 - BUTTON_HEIGHT/2:
            pygame.draw.rect(win, (0, 0, 255),
                             (WIN_WIDTH/2 - BUTTON_WIDTH/2, WIN_HEIGHT/2 - BUTTON_HEIGHT/2, BUTTON_WIDTH, BUTTON_HEIGHT))
            if click[0] == 1:
                main()
        else:
            pygame.draw.rect(win, (0, 255, 0),
                             (WIN_WIDTH/2 - BUTTON_WIDTH/2, WIN_HEIGHT/2 - BUTTON_HEIGHT/2, BUTTON_WIDTH, BUTTON_HEIGHT))

        if WIN_WIDTH/2 + BUTTON_WIDTH/2 > mouse[0] > WIN_WIDTH/2 - BUTTON_WIDTH/2 and WIN_HEIGHT/2 + BUTTON_HEIGHT/2 + 100 > mouse[1] > WIN_HEIGHT/2 - BUTTON_HEIGHT/2 + 100:
            pygame.draw.rect(win, (0, 0, 255), (WIN_WIDTH/2 - BUTTON_WIDTH/2,
                                                WIN_HEIGHT/2 - BUTTON_HEIGHT/2 + 100, BUTTON_WIDTH, BUTTON_HEIGHT))
            if click[0] == 1:
                replay_genome(config_path)
        else:
            pygame.draw.rect(win, (255, 0, 0), (WIN_WIDTH/2 - BUTTON_WIDTH/2,
                                                WIN_HEIGHT/2 - BUTTON_HEIGHT/2 + 100, BUTTON_WIDTH, BUTTON_HEIGHT))

        text = STAT_FONT.render("Play", 1, (255, 255, 255))
        win.blit(text, (WIN_WIDTH/2 - text.get_width() /
                        2, WIN_HEIGHT/2 - text.get_height()/2))

        text = STAT_FONT.render("AI", 1, (255, 255, 255))
        win.blit(text, (WIN_WIDTH/2 - text.get_width() /
                        2, WIN_HEIGHT/2 - text.get_height()/2 + 100))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        clock.tick(15)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    # replay_genome(config_path)
    # main()
    menu(config_path)
