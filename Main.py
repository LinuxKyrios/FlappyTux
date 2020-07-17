import random  #Necessary for generating random numbers
import sys  #Only for user sys.exit to exit the program
import pygame #Imports pygame library
from pygame.locals import * #Basic imports from pygame

#Definig global variables for the game
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
FPS = 32
RED = (255, 0, 0)
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_MODELS = {} #dictionary for game models
GAME_SOUNDS = {} #dictionary for game sounds
PLAYER = 'models/tux.png'
BACKGROUND = 'models/background.png'
PIPE = 'models/pipe.png'


def welcomeScreen():
    """
    Function shows welcome screen, also sets primary positions of the tux
    """

    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_MODELS['player'].get_height()) / 2)
    messagex = int((SCREENWIDTH - GAME_MODELS['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            #When the user will press cross top  icon or escape button the game will close
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            #Pressing space or up key results in staring game
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_MODELS['background'], (0, 0))
                SCREEN.blit(GAME_MODELS['player'], (playerx, playery))
                SCREEN.blit(GAME_MODELS['message'], (messagex, messagey))
                SCREEN.blit(GAME_MODELS['base'], (basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def mainGame():
    """Main function of the game. The biggest part of mechanics and game working is defined here"""
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENWIDTH / 2)
    basex = 0

    #For creating 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    #A list containing dictionary with upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    #A list containing dictionary with lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8  #Tux speed while flapping
    playerFlapped = False  #It is true only when the tux is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        #This function returns true when the tux is crashed
        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)  
        if crashTest:
            return

        #For display score in terminal
        playerMidPos = playerx + GAME_MODELS['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_MODELS['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"Your score is {score}")
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_MODELS['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        #Moving pipes to the left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        #Adding a new pipe when the first pipe is going to cross the leftmost part of the screen
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        #Remove the pife when it is out of the screen
        if upperPipes[0]['x'] < - GAME_MODELS['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        #For model blitting
        SCREEN.blit(GAME_MODELS['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_MODELS['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_MODELS['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_MODELS['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_MODELS['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_MODELS['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_MODELS['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_MODELS['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

#Function for collision
def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipeHeight = GAME_MODELS['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_MODELS['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_MODELS['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < \
                GAME_MODELS['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False

#Function for generating random pipes through game
def getRandomPipe():
    """
    Generate positions of two pipes(one bottom straight and one rotated to the top) for blitting on the screen
    """
    pipeHeight = GAME_MODELS['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_MODELS['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},  #For upper Pipe
        {'x': pipeX, 'y': y2}  #For lower Pipe
    ]
    return pipe


if __name__ == "__main__":
    #This is going to be the main point from where the game is starting
    pygame.init()  #Initializing all modules from pygame
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Tux')

    #Game models - numbers
    GAME_MODELS['numbers'] = (
        pygame.image.load('models/0.png').convert_alpha(),
        pygame.image.load('models/1.png').convert_alpha(),
        pygame.image.load('models/2.png').convert_alpha(),
        pygame.image.load('models/3.png').convert_alpha(),
        pygame.image.load('models/4.png').convert_alpha(),
        pygame.image.load('models/5.png').convert_alpha(),
        pygame.image.load('models/6.png').convert_alpha(),
        pygame.image.load('models/7.png').convert_alpha(),
        pygame.image.load('models/8.png').convert_alpha(),
        pygame.image.load('models/9.png').convert_alpha(),
    )

    #Game models
    GAME_MODELS['message'] = pygame.image.load('models/message.png').convert_alpha()
    GAME_MODELS['base'] = pygame.image.load('models/base.png').convert_alpha()
    GAME_MODELS['pipe'] = (pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
                            pygame.image.load(PIPE).convert_alpha()
                            )

    #Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('sounds/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('sounds/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('sounds/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('sounds/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('sounds/wing.wav')

    GAME_MODELS['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_MODELS['player'] = pygame.image.load(PLAYER).convert_alpha()

    while True:
        welcomeScreen()  #Shows welcome screen to the user until a buton is pressed
        mainGame()  #This is the main game function