from constants import *
from sys import exit
from game import Game
from score import Score
from preview import Preview

from random import choice

class Main:
    def __init__(self):
        """
        has all general stuff for the game
        such as the window, clock, and display surface
        """
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Tetris")
        
        self.next_shapes = []
        self.current_bag = list(TETROMINOS.keys())

        for _ in range(3):  # Pre-fill the next shapes with 3 random tetrominos
            x  = choice(self.current_bag)  # Randomly select a shape from the bag
            self.next_shapes.append(x)
            self.current_bag.remove(x)

        self.game = Game(self.get_next_shape, self.update_score )  # Initialize the game overlay
        self.score = Score() # Initialize the score display
        self.preview = Preview() # Initialize the preview display

        
        

    def update_score(self, lines, score, level):
            self.score.lines = lines
            self.score.score = score
            self.score.level = level

    def get_next_shape(self):
        if not self.current_bag:
            self.current_bag = list(TETROMINOS.keys())  # Reset the bag if empty
        
        next_shape = self.next_shapes.pop(0)  # Get the next shape 
        x  = choice(self.current_bag)  # Randomly select a shape from the bag
        self.next_shapes.append(x)
        self.current_bag.remove(x)  # Remove the selected shape from the bag
        return next_shape
        
    def run(self):
        """
        Runs the main loop of the game.
        This loop will keep the game running until the user closes the window.
        """
        #runs perpetual while loop until false or exited 
        while True:
            #takes in user inputs
            for event in pygame.event.get(): 
                #quits the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            #background color
            self.display_surface.fill((GRAY))
            self.game.run()
            self.score.run()
            self.preview.run(self.next_shapes)
            #updates the display surface
            pygame.display.update()
            #updates the clock
            self.clock.tick(100) #100 FPS
            

if __name__ == "__main__":
    main = Main()
    main.run()