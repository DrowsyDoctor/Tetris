import pygame

# Screen dimensions

# Grid dimensions
COLUMNS = 10
ROWS = 20
CELL_SIZE = 35
BORDER_WIDTH = COLUMNS * CELL_SIZE 
BORDER_HEIGHT= ROWS * CELL_SIZE 

#Side bar for pieces and score
SIDE_BAR_WIDTH = 200
PREVIEW_HEIGHT = 0.7
SCORE_HEIGHT = 1 - PREVIEW_HEIGHT

#Window dimensions
PADDING = 20
WINDOW_WIDTH = BORDER_WIDTH + SIDE_BAR_WIDTH + PADDING * 3
WINDOW_HEIGHT = BORDER_HEIGHT + PADDING * 2


#Blocks
OFFSET = pygame.Vector2(COLUMNS // 2 , -1)

#Timer 
UPDATE_START_SPEED = 300  # milliseconds
MOVE_WAIT_TIME = 75
ROTATE_WAIT_TIME = 150

#colors 
RED = (224, 11, 85)
ORANGE = (255, 105, 31)
YELLOW = (255, 253, 147)
GREEN = (0, 233, 136)
LIGHT_BLUE = (153, 247, 255)
DARK_BLUE = (78, 43, 214)
PURPLE = (189, 112, 225)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LINE_COLOR = (52, 52, 52)

TETROMINOS = {
    'I': {"shape": [(0, 1), (-1, 1), (1, 1), (2, 1)], "color": LIGHT_BLUE},     # I piece - horizontal spawn
    'O': {"shape": [(0, 0), (1, 0), (0, 1), (1, 1)], "color": YELLOW},          # O piece - 2x2 square
    'T': {"shape": [(1, 0), (0, 0), (2, 0), (1, -1)], "color": PURPLE},          # T piece - pivot at center
    'Z': {"shape": [(1, 0), (0, 0), (1, 1), (2, 1)], "color": RED},           # S piece - pivot at center
    'S': {"shape": [(1, 0), (2, 0), (1, 1), (0, 1)], "color": GREEN},             # Z piece - pivot at center
    'J': {"shape": [(0, 0), (-1, -1), (-1, 0), (1, 0)], "color": DARK_BLUE},       # J piece - pivot at center
    'L': {"shape": [(0, 0), (-1, 0), (1, 0), (1, -1)], "color": ORANGE}           # L piece - pivot at center
}

SCORE_DATA = {1: 40, 2: 100, 3: 300, 4: 1200}
