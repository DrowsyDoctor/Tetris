from constants import *
from random import choice

from timer import Timer

class Game:
    def __init__(self, get_next_shape, update_score):
        """
        this is the overlay for the game that is put on top of the window
        """
        self.surface = pygame.Surface((BORDER_WIDTH, BORDER_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topleft=(PADDING, PADDING))
        self.sprites = pygame.sprite.Group()

        self.get_next_shape = get_next_shape  # Function to get the next shape
        self.update_score = update_score

        self.line_surface = self.surface.copy()
        self.line_surface.fill((0, 255,0))
        self.line_surface.set_colorkey((0, 255, 0))
        self.line_surface.set_alpha(120)  # Set transparency for grid lines

# Example block at position (0, 0)
        self.field_data = [[0 for x in range(COLUMNS)] for y in range (ROWS)]  # Initialize the field data
        self.tetromino = Tetromino(
            choice(list(TETROMINOS.keys())),
            self.sprites, 
            self.create_tetromino,
            self.field_data)  # Example tetromino, can be changed to any shape


        self.down_speed = UPDATE_START_SPEED
        self.down_speed_increment = self.down_speed * 0.3
        self.down_pressed = False

        self.timers = {
            "vertical move": Timer(UPDATE_START_SPEED, True, self.move_down),
            "horizontal move": Timer(MOVE_WAIT_TIME),
            "rotate": Timer(ROTATE_WAIT_TIME)
        }
        self.timers["vertical move"].activate()

        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0

    def calculate_score(self, num_lines):
        self.current_lines += num_lines
        self.current_score += SCORE_DATA[num_lines] * self.current_level

        if self.current_lines / 10 > self.current_level:
            self.current_level += 1
        self.update_score(self.current_lines, self.current_score, self.current_level)

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def create_tetromino(self):
        self.check_finished_rows()
        self.tetromino = Tetromino(
            self.get_next_shape(),  # Get the next shape from the provided function
            self.sprites, 
            self.create_tetromino,
            self.field_data)

    def move_down(self):
        self.tetromino.move_down()

    def draw_grid(self):
        """
        Draws the grid lines on the game surface. HOWEVER IT STILL HAS A BACKGROUND COLOR
        """
        for col in range(1, COLUMNS):
            x = col * CELL_SIZE
            pygame.draw.line(self.surface, LINE_COLOR, (x, 0), (x, self.surface.get_height()), 1)    
            
        for row in range(1, ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(self.surface, LINE_COLOR, (0, y), (self.surface.get_width(), y), 1)

        self.surface.blit(self.line_surface, (0, 0))

    def input(self):

        keys  = pygame.key.get_pressed()

        if not self.timers["horizontal move"].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_horizontal(-1)
                self.timers["horizontal move"].activate()
            if keys[pygame.K_RIGHT]:
                self.tetromino.move_horizontal(1)
                self.timers['horizontal move'].activate()

        if not self.timers["rotate"].active:
            if keys[pygame.K_UP]:
                # Rotate the tetromino (not implemented in this example)
                self.tetromino.rotate()
                self.timers["rotate"].activate()

        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers["vertical move"].duration = self.down_speed_increment
            
        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers["vertical move"].duration = self.down_speed


    def check_finished_rows(self):
        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)
            
        if delete_rows:
            for delete_row in delete_rows:
                for block in self.field_data[delete_row]:
                    block.kill()  # Remove blocks from the sprite group

                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]  # Reset the field data
            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block  # Update the field data with remaining blocks

            self.calculate_score(len(delete_rows))

    def run(self):

        self.input()
        self.timer_update()
        self.sprites.update()

        self.surface.fill(BLACK)
        self.sprites.draw(self.surface)

        self.draw_grid()
        self.display_surface.blit(self.surface, (PADDING, PADDING))
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)


class Tetromino(pygame.sprite.Sprite):
    def __init__(self, shape, group, create_tetromino, field_data):

        # setup 
        self.shape = shape
        self.block_positions = TETROMINOS[shape]['shape']
        self.color = TETROMINOS[shape]['color']
        self.create_tetromino = create_tetromino
        self.field_data = field_data    
        # create blocks
        self.blocks = [Block(group, pos, self.color) for pos in self.block_positions]

    def collision_horizontal_check(self, blocks, amount):
        collision_list = [block.horizontal_collide(int(block.pos.x + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False
    
    def collision_vertical_check(self, blocks, amount):
        collision_list = [block.vertical_collide(int(block.pos.y + amount), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    def move_down(self):
        if not self.collision_vertical_check(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1
        else:
            for block in self.blocks:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
            self.create_tetromino()


    def move_horizontal(self, amount):
        if not self.collision_horizontal_check(self.blocks, amount):
            for block in self.blocks:
                block.pos.x += amount

    def rotate(self):
        if self.shape != "O":
            pivot_pos = self.blocks[0].pos  # Use the second block as the pivot
            new_positions = [block.rotate(pivot_pos) for block in self.blocks]
            for pos in new_positions:
                if pos.x < 0 or pos.x >= COLUMNS:
                    return 
                
                if pos.y > ROWS:
                    return
                
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return

            for i, block in enumerate(self.blocks):
                block.pos = new_positions[i]


class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color):
        
        # general
        super().__init__(group)
        self.image = pygame.Surface((CELL_SIZE,CELL_SIZE))
        self.image.fill(color)
        
        # position
        self.pos = pygame.Vector2(pos) + OFFSET
        self.rect = self.image.get_rect(topleft = (self.pos *CELL_SIZE))

    def rotate(self, pivot_pos):
        return pivot_pos + (self.pos - pivot_pos).rotate(90)

    def update(self):
        """
        Updates the position of the block based on its pos attribute.
        """
        self.rect.topleft = self.pos* CELL_SIZE

    def horizontal_collide(self, x, field_data):
        if not 0 <= x < COLUMNS:
            return True
        if field_data[int(self.pos.y)][x]:
            return True
    
    def vertical_collide(self, y, field_data):
        if y >= ROWS:
            return True
        if y >= 0 and field_data[y][int(self.pos.x)]:
            return True