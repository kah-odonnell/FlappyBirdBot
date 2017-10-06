import pygame
from pygame.locals import *


def play(game):
    movementInfo = game.init()
    game.setupGame(movementInfo)
    crashInfo = game.stepGame()
    while (crashInfo['didCrash'] is False):
        crashInfo = game.stepGame()
    game.showGameOverScreen(crashInfo)


def pressUp():
    event = pygame.event.Event(pygame.KEYDOWN, {"key": K_UP})
    pygame.event.post(event)


def learn(score):
    pass


def run(upperPipes, lowerPipes, playerInfo):
    event = pygame.event.Event(pygame.KEYDOWN, {"key": K_UP})
    pygame.event.post(event)

def main():
    pass

