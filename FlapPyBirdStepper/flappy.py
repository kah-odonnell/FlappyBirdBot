from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *

class GameClient:
    def __init__(self):
        pass

    def init(self):
        self.FPS = 30
        self.SCREENWIDTH  = 288
        self.SCREENHEIGHT = 512
        # amount by which base can maximum shift to left
        self.PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
        self.BASEY        = self.SCREENHEIGHT * 0.79
        # image, sound and hitmask  dicts
        self.IMAGES, self.SOUNDS, self.HITMASKS = {}, {}, {}

        # list of all possible players (tuple of 3 positions of flap)
        self.PLAYERS_LIST = (
            # red bird
            (
                'FlapPyBirdStepper/assets/sprites/redbird-upflap.png',
                'FlapPyBirdStepper/assets/sprites/redbird-midflap.png',
                'FlapPyBirdStepper/assets/sprites/redbird-downflap.png',
            ),
            # blue bird
            (
                # amount by which base can maximum shift to left
                'FlapPyBirdStepper/assets/sprites/bluebird-upflap.png',
                'FlapPyBirdStepper/assets/sprites/bluebird-midflap.png',
                'FlapPyBirdStepper/assets/sprites/bluebird-downflap.png',
            ),
            # yellow bird
            (
                'FlapPyBirdStepper/assets/sprites/yellowbird-upflap.png',
                'FlapPyBirdStepper/assets/sprites/yellowbird-midflap.png',
                'FlapPyBirdStepper/assets/sprites/yellowbird-downflap.png',
            ),
        )

        # list of backgrounds
        self.BACKGROUNDS_LIST = (
            'FlapPyBirdStepper/assets/sprites/background-day.png',
            'FlapPyBirdStepper/assets/sprites/background-night.png',
        )

        # list of pipes
        self.PIPES_LIST = (
            'FlapPyBirdStepper/assets/sprites/pipe-green.png',
            'FlapPyBirdStepper/assets/sprites/pipe-red.png',
        )

        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()
        self.SCREEN = pygame.display.set_mode((self.SCREENWIDTH, self.SCREENHEIGHT))
        pygame.display.set_caption('Flappy Bird')

        # numbers sprites for score display
        self.IMAGES['numbers'] = (
            pygame.image.load('FlapPyBirdStepper/assets/sprites/0.png').convert_alpha(),
            pygame.image.load('FlapPyBirdStepper/assets/sprites/1.png').convert_alpha(),
            pygame.image.load('FlapPyBirdStepper/assets/sprites/2.png').convert_alpha(),
            pygame.image.load('FlapPyBirdStepper/assets/sprites/3.png').convert_alpha(),
            pygame.image.load('FlapPyBirdStepper/assets/sprites/4.png').convert_alpha(),
            pygame.image.load('FlapPyBirdStepper/assets/sprites/5.png').convert_alpha(),
            pygame.image.load('FlapPyBirdStepper/assets/sprites/6.png').convert_alpha(),
            pygame.image.load('FlapPyBirdStepper/assets/sprites/7.png').convert_alpha(),
            pygame.image.load('FlapPyBirdStepper/assets/sprites/8.png').convert_alpha(),
            pygame.image.load('FlapPyBirdStepper/assets/sprites/9.png').convert_alpha()
        )

        # game over sprite
        self.IMAGES['gameover'] = pygame.image.load('FlapPyBirdStepper/assets/sprites/gameover.png').convert_alpha()
        # message sprite for welcome screen
        self.IMAGES['message'] = pygame.image.load('FlapPyBirdStepper/assets/sprites/message.png').convert_alpha()
        # base (ground) sprite
        self.IMAGES['base'] = pygame.image.load('FlapPyBirdStepper/assets/sprites/base.png').convert_alpha()

        # sounds
        if 'win' in sys.platform:
            soundExt = '.wav'
        else:
            soundExt = '.ogg'

        self.SOUNDS['die']    = pygame.mixer.Sound('FlapPyBirdStepper/assets/audio/die' + soundExt)
        self.SOUNDS['hit']    = pygame.mixer.Sound('FlapPyBirdStepper/assets/audio/hit' + soundExt)
        self.SOUNDS['point']  = pygame.mixer.Sound('FlapPyBirdStepper/assets/audio/point' + soundExt)
        self.SOUNDS['swoosh'] = pygame.mixer.Sound('FlapPyBirdStepper/assets/audio/swoosh' + soundExt)
        self.SOUNDS['wing']   = pygame.mixer.Sound('FlapPyBirdStepper/assets/audio/wing' + soundExt)

        # select random background sprites
        randBg = random.randint(0, len(self.BACKGROUNDS_LIST) - 1)
        self.IMAGES['background'] = pygame.image.load(self.BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(self.PLAYERS_LIST) - 1)
        self.IMAGES['player'] = (
            pygame.image.load(self.PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(self.PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(self.PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(self.PIPES_LIST) - 1)
        self.IMAGES['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(self.PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        self.HITMASKS['pipe'] = (
            self.getHitmask(self.IMAGES['pipe'][0]),
            self.getHitmask(self.IMAGES['pipe'][1]),
        )

        # hitmask for player
        self.HITMASKS['player'] = (
            self.getHitmask(self.IMAGES['player'][0]),
            self.getHitmask(self.IMAGES['player'][1]),
            self.getHitmask(self.IMAGES['player'][2]),
        )

        movementInfo = self.showWelcomeAnimation()
        return movementInfo


    def showWelcomeAnimation(self):
        """Shows welcome screen animation of flappy bird"""
        # index of player to blit on screen
        playerIndex = 0
        playerIndexGen = cycle([0, 1, 2, 1])
        # iterator used to change playerIndex after every 5th iteration
        loopIter = 0

        playerx = int(self.SCREENWIDTH * 0.2)
        playery = int((self.SCREENHEIGHT - self.IMAGES['player'][0].get_height()) / 2)

        messagex = int((self.SCREENWIDTH - self.IMAGES['message'].get_width()) / 2)
        messagey = int(self.SCREENHEIGHT * 0.12)

        basex = 0
        # amount by which base can maximum shift to left
        baseShift = self.IMAGES['base'].get_width() - self.IMAGES['background'].get_width()

        # player shm for up-down motion on welcome screen
        playerShmVals = {'val': 0, 'dir': 1}

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        self.playerShm(playerShmVals)

        # draw sprites
        self.SCREEN.blit(self.IMAGES['background'], (0,0))
        self.SCREEN.blit(self.IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        self.SCREEN.blit(self.IMAGES['message'], (messagex, messagey))
        self.SCREEN.blit(self.IMAGES['base'], (basex, self.BASEY))

        pygame.display.update()
        self.FPSCLOCK.tick(self.FPS)

        return {
            'playery': playery + playerShmVals['val'],
            'basex': basex,
            'playerIndexGen': playerIndexGen,
        }
        #
        # while True:
        #     for event in pygame.event.get():
        #         if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
        #             pygame.quit()
        #             sys.exit()
        #         if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
        #             # make first flap sound and return values for mainGame
        #             SOUNDS['wing'].play()
        #             return {
        #                 'playery': playery + playerShmVals['val'],
        #                 'basex': basex,
        #                 'playerIndexGen': playerIndexGen,
        #             }
        #



    def setupGame(self, movementInfo):
        self.score = self.playerIndex = self.loopIter = 0
        self.playerIndexGen = movementInfo['playerIndexGen']
        self.playerx, self.playery = int(self.SCREENWIDTH * 0.2), movementInfo['playery']

        self.basex = movementInfo['basex']
        self.baseShift = self.IMAGES['base'].get_width() - self.IMAGES['background'].get_width()

        # get 2 new pipes to add to upperPipes lowerPipes list
        newPipe1 = self.getRandomPipe()
        newPipe2 = self.getRandomPipe()

        # list of upper pipes
        self.upperPipes = [
            {'x': self.SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
            {'x': self.SCREENWIDTH + 200 + (self.SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
        ]

        # list of lowerpipe
        self.lowerPipes = [
            {'x': self.SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
            {'x': self.SCREENWIDTH + 200 + (self.SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
        ]

        self.pipeVelX = -4

        # player velocity, max velocity, downward accleration, accleration on flap
        self.playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
        self.playerMaxVelY =  10   # max vel along Y, max descend speed
        self.playerMinVelY =  -8   # min vel along Y, max ascend speed
        self.playerAccY    =   1   # players downward accleration
        self.playerRot     =  45   # player's rotation
        self.playerVelRot  =   3   # angular speed
        self.playerRotThr  =  20   # rotation threshold
        self.playerFlapAcc =  -9   # players speed on flapping
        self.playerFlapped = False # True when player flaps


    def stepGame(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if self.playery > -2 * self.IMAGES['player'][0].get_height():
                    self.playerVelY = self.playerFlapAcc
                    self.playerFlapped = True
                    self.SOUNDS['wing'].play()

        # check for crash here
        crashTest = self.checkCrash({'x': self.playerx, 'y': self.playery, 'index': self.playerIndex},
                                    self.upperPipes, self.lowerPipes)
        if crashTest[0]:
            return {
                'didCrash': True,
                'y': self.playery,
                'groundCrash': crashTest[1],
                'basex': self.basex,
                'upperPipes': self.upperPipes,
                'lowerPipes': self.lowerPipes,
                'score': self.score,
                'playerVelY': self.playerVelY,
                'playerRot': self.playerRot
            }

        # check for score
        playerMidPos = self.playerx + self.IMAGES['player'][0].get_width() / 2
        for pipe in self.upperPipes:
            pipeMidPos = pipe['x'] + self.IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                self.score += 1
                self.SOUNDS['point'].play()

        # playerIndex basex change
        if (self.loopIter + 1) % 3 == 0:
            self.playerIndex = next(self.playerIndexGen)
        self.loopIter = (self.loopIter + 1) % 30
        self.basex = -((-self.basex + 100) % self.baseShift)

        # rotate the player
        if self.playerRot > -90:
            self.playerRot -= self.playerVelRot

        # player's movement
        if self.playerVelY < self.playerMaxVelY and not self.playerFlapped:
            self.playerVelY += self.playerAccY
        if self.playerFlapped:
            self.playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            self.playerRot = 45

        playerHeight = self.IMAGES['player'][self.playerIndex].get_height()
        self.playery += min(self.playerVelY, self.BASEY - self.playery - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            uPipe['x'] += self.pipeVelX
            lPipe['x'] += self.pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < self.upperPipes[0]['x'] < 5:
            newPipe = self.getRandomPipe()
            self.upperPipes.append(newPipe[0])
            self.lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if self.upperPipes[0]['x'] < -self.IMAGES['pipe'][0].get_width():
            self.upperPipes.pop(0)
            self.lowerPipes.pop(0)

        # draw sprites
        self.SCREEN.blit(self.IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            self.SCREEN.blit(self.IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            self.SCREEN.blit(self.IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        self.SCREEN.blit(self.IMAGES['base'], (self.basex, self.BASEY))
        # print score so player overlaps the score
        self.showScore(self.score)

        # Player rotation has a threshold
        self.visibleRot = self.playerRotThr
        if self.playerRot <= self.playerRotThr:
            self.visibleRot = self.playerRot

        self.playerSurface = pygame.transform.rotate(self.IMAGES['player'][self.playerIndex], self.visibleRot)
        self.SCREEN.blit(self.playerSurface, (self.playerx, self.playery))

        pygame.display.update()
        self.FPSCLOCK.tick(self.FPS)

        return {
            'didCrash': False
        }


    def showGameOverScreen(self, crashInfo):
        """crashes the player down ans shows gameover image"""
        score = crashInfo['score']
        playerx = self.SCREENWIDTH * 0.2
        playery = crashInfo['y']
        playerHeight = self.IMAGES['player'][0].get_height()
        playerVelY = crashInfo['playerVelY']
        playerAccY = 2
        playerRot = crashInfo['playerRot']
        playerVelRot = 7

        basex = crashInfo['basex']

        upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

        # play hit and die sounds
        self.SOUNDS['hit'].play()
        if not crashInfo['groundCrash']:
            self.SOUNDS['die'].play()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if playery + playerHeight >= self.BASEY - 1:
                        return

            # player y shift
            if playery + playerHeight < self.BASEY - 1:
                playery += min(playerVelY, self.BASEY - playery - playerHeight)

            # player velocity change
            if playerVelY < 15:
                playerVelY += playerAccY

            # rotate only when it's a pipe crash
            if not crashInfo['groundCrash']:
                if playerRot > -90:
                    playerRot -= playerVelRot

            # draw sprites
            self.SCREEN.blit(self.IMAGES['background'], (0,0))

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                self.SCREEN.blit(self.IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                self.SCREEN.blit(self.IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

            self.SCREEN.blit(self.IMAGES['base'], (basex, self.BASEY))
            self.showScore(score)

            playerSurface = pygame.transform.rotate(self.IMAGES['player'][1], playerRot)
            self.SCREEN.blit(playerSurface, (playerx,playery))

            self.FPSCLOCK.tick(self.FPS)
            pygame.display.update()


    def playerShm(self, playerShm):
        """oscillates the value of playerShm['val'] between 8 and -8"""
        if abs(playerShm['val']) == 8:
            playerShm['dir'] *= -1

        if playerShm['dir'] == 1:
             playerShm['val'] += 1
        else:
            playerShm['val'] -= 1


    def getRandomPipe(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gapY = random.randrange(0, int(self.BASEY * 0.6 - self.PIPEGAPSIZE))
        gapY += int(self.BASEY * 0.2)
        pipeHeight = self.IMAGES['pipe'][0].get_height()
        pipeX = self.SCREENWIDTH + 10

        return [
            {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
            {'x': pipeX, 'y': gapY + self.PIPEGAPSIZE}, # lower pipe
        ]


    def showScore(self, score):
        """displays score in center of screen"""
        scoreDigits = [int(x) for x in list(str(score))]
        totalWidth = 0 # total width of all numbers to be printed

        for digit in scoreDigits:
            totalWidth += self.IMAGES['numbers'][digit].get_width()

        Xoffset = (self.SCREENWIDTH - totalWidth) / 2

        for digit in scoreDigits:
            self.SCREEN.blit(self.IMAGES['numbers'][digit], (Xoffset, self.SCREENHEIGHT * 0.1))
            Xoffset += self.IMAGES['numbers'][digit].get_width()


    def checkCrash(self, player, upperPipes, lowerPipes):
        """returns True if player collders with base or pipes."""
        pi = player['index']
        player['w'] = self.IMAGES['player'][0].get_width()
        player['h'] = self.IMAGES['player'][0].get_height()

        # if player crashes into ground
        if player['y'] + player['h'] >= self.BASEY - 1:
            return [True, True]
        else:

            playerRect = pygame.Rect(player['x'], player['y'],
                          player['w'], player['h'])
            pipeW = self.IMAGES['pipe'][0].get_width()
            pipeH = self.IMAGES['pipe'][0].get_height()

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                # upper and lower pipe rects
                uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
                lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

                # player and upper/lower pipe hitmasks
                pHitMask = self.HITMASKS['player'][pi]
                uHitmask = self.HITMASKS['pipe'][0]
                lHitmask = self.HITMASKS['pipe'][1]

                # if bird collided with upipe or lpipe
                uCollide = self.pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
                lCollide = self.pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

                if uCollide or lCollide:
                    return [True, False]

        return [False, False]

    def pixelCollision(self, rect1, rect2, hitmask1, hitmask2):
        """Checks if two objects collide and not just their rects"""
        rect = rect1.clip(rect2)

        if rect.width == 0 or rect.height == 0:
            return False

        x1, y1 = rect.x - rect1.x, rect.y - rect1.y
        x2, y2 = rect.x - rect2.x, rect.y - rect2.y

        for x in range(rect.width):
            for y in range(rect.height):
                if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                    return True
        return False

    def getHitmask(self, image):
        """returns a hitmask using an image's alpha."""
        mask = []
        for x in range(image.get_width()):
            mask.append([])
            for y in range(image.get_height()):
                mask[x].append(bool(image.get_at((x,y))[3]))
        return mask


    if __name__ == '__main__':
        pass
        #main()
