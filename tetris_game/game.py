# Updated game.py with Super Rotation System (SRS)

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

        self.field_data = [[0 for x in range(COLUMNS)] for y in range (ROWS)]  # Initialize the field data
        self.tetromino = Tetromino(
            get_next_shape(),
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
                self.tetromino.rotate()
                self.timers["rotate"].activate()

        if not self.timers["rotate"].active:#COCK
            if keys[pygame.K_z]:
                self.tetromino.rotate_counter()
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
        # Setup 
        self.shape = shape
        self.block_positions = TETROMINOS[shape]['shape']
        self.color = TETROMINOS[shape]['color']
        self.create_tetromino = create_tetromino
        self.field_data = field_data
        
        # SRS rotation state (0, 1, 2, 3 representing 0°, 90°, 180°, 270°)
        self.rotation_state = 0
        
        # Create blocks
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

    def check_collision_at_positions(self, positions):
        """Check if any of the given positions would cause a collision"""
        for pos in positions:
            # Check boundaries
            if pos.x < 0 or pos.x >= COLUMNS or pos.y >= ROWS:
                return True
            
            # Check collision with existing blocks (only if y >= 0)
            if pos.y >= 0 and self.field_data[int(pos.y)][int(pos.x)]:
                return True
        
        return False

    def check_collision_at_positions(self, positions):
        """Check if any of the given positions would cause a collision"""
        for pos in positions:
            # Check boundaries
            if pos.x < 0 or pos.x >= COLUMNS or pos.y >= ROWS:
                return True
            
            # Check collision with existing blocks (only if y >= 0)
            if pos.y >= 0 and self.field_data[int(pos.y)][int(pos.x)]:
                return True
        
        return False

    def rotate(self):
        """Implement Super Rotation System (SRS) rotation with wall kicks"""
        if self.shape == "O":  # O piece doesn't rotate
            return
            
        # Calculate the pivot point (center of rotation)
        if self.shape == "I":
            # I piece uses a different pivot calculation
            pivot_pos = self.blocks[0].pos
        else:
            # Other pieces use the first block as pivot
            pivot_pos = self.blocks[0].pos
        
        # Calculate new rotation state
        new_rotation_state = (self.rotation_state + 1) % 4
        
        # Get the basic rotated positions
        new_positions = [block.rotate(pivot_pos) for block in self.blocks]
        
        # Get wall kick data for this piece and rotation
        kick_data = self.get_wall_kick_data(self.rotation_state, new_rotation_state)
        
        # Try each wall kick offset
        for kick_offset in kick_data:
            test_positions = [pos + pygame.Vector2(kick_offset) for pos in new_positions]
            
            # If this position is valid, apply the rotation
            if not self.check_collision_at_positions(test_positions):
                for i, block in enumerate(self.blocks):
                    block.pos = test_positions[i]
                self.rotation_state = new_rotation_state
                return
        
        # If no wall kick worked, rotation fails (do nothing)

    def rotate_counter(self):
        """Implement Super Rotation System (SRS) rotation with wall kicks"""
        if self.shape == "O":  # O piece doesn't rotate
            return
            
        # Calculate the pivot point (center of rotation)
        if self.shape == "I":
            # I piece uses a different pivot calculation
            pivot_pos = self.blocks[0].pos
        else:
            # Other pieces use the first block as pivot
            pivot_pos = self.blocks[0].pos
        
        # Calculate new rotation state
        new_rotation_state = (self.rotation_state - 1) % 4
        
        # Get the basic rotated positions
        new_positions = [block.rotate_counter(pivot_pos) for block in self.blocks]
        
        # Get wall kick data for this piece and rotation
        kick_data = self.get_wall_kick_data(self.rotation_state, new_rotation_state)
        
        # Try each wall kick offset
        for kick_offset in kick_data:
            test_positions = [pos + pygame.Vector2(kick_offset) for pos in new_positions]
            
            # If this position is valid, apply the rotation
            if not self.check_collision_at_positions(test_positions):
                for i, block in enumerate(self.blocks):
                    block.pos = test_positions[i]
                self.rotation_state = new_rotation_state
                return
        
        # If no wall kick worked, rotation fails (do nothing)

    def get_wall_kick_data(self, from_state, to_state):
        """Get wall kick offsets for SRS system"""
        
        # I piece has special wall kick data
        if self.shape == "I":
            return self.get_i_piece_wall_kicks(from_state, to_state)
        
        # Standard wall kick data for J, L, S, T, Z pieces
        wall_kick_data = {
            (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 0->R
            (1, 2): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],      # R->2
            (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],     # 2->L
            (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],   # L->0
            (1, 0): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],     # R->0
            (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],   # 2->R
            (3, 2): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],  # L->2
            (0, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)]       # 0->L
        }
        
        return wall_kick_data.get((from_state, to_state), [(0, 0)])

    def get_i_piece_wall_kicks(self, from_state, to_state):
        """Special wall kick data for I piece"""
        i_wall_kick_data = {
            (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],    # 0->R
            (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],    # R->2
            (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],    # 2->L
            (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],    # L->0
            (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],    # R->0
            (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],    # 2->R
            (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],    # L->2
            (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]     # 0->L
        }
        
        return i_wall_kick_data.get((from_state, to_state), [(0, 0)])


class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, color):
        # General
        super().__init__(group)
        self.image = pygame.Surface((CELL_SIZE,CELL_SIZE))
        self.image.fill(color)
        
        # Position
        self.pos = pygame.Vector2(pos) + OFFSET
        self.rect = self.image.get_rect(topleft = (self.pos *CELL_SIZE))

    def rotate(self, pivot_pos):
        """Rotate the block 90 degrees clockwise around the pivot using SRS method"""
        # Calculate relative position from pivot
        relative_pos = self.pos - pivot_pos
        
        # Apply SRS rotation matrix for 90° clockwise: (x, y) -> (y, -x)
        rotated_relative = pygame.Vector2(-relative_pos.y, relative_pos.x)
        
        # Return new absolute position
        return pivot_pos + rotated_relative
    
    def rotate_counter(self, pivot_pos):
        """Rotate the block 90 degrees counterclockwise around the pivot using SRS method"""
        # Calculate relative position from pivot
        relative_pos = self.pos - pivot_pos
        
        # Apply SRS rotation matrix for -90° clockwise: (x, y) -> (y, -x)
        rotated_relative = pygame.Vector2(relative_pos.y, -relative_pos.x)
        
        print("counterclockwise rotation")

        # Return new absolute position
        return pivot_pos + rotated_relative
    

    def update(self):
        """Updates the position of the block based on its pos attribute."""
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