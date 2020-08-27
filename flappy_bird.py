import pygame
import neat
import time
import os
import random

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

BIRD_IMAGES = [pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bird1.png"))), pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bird2.png"))), pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "pipe.png")))

BASE_IMG = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "base.png")))

BACKGROUND_IMAGE = pygame.transform.scale2x(
    pygame.image.load(os.path.join("images", "bg.png")))


class Bird:
    IMGS = BIRD_IMAGES
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + 1.5*self.tick_count**2
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if(self.tilt < self.MAX_ROTATION):
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, window):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.image = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.image = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.image = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.image = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.image = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_image.get_rect(
            center=self.image.get_rect(topleft=(self.x, self.y)).center())
        window.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


def draw_window(win, bird):
    win.blit(BACKGROUND_IMAGE, (0, 0))
    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(200, 200)
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    run = True
    while(run):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        draw_window(win, bird)
    pygame.quit()
    quit()
