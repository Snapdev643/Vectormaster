#Vector engine by Antiblue

import pygame as pg
from characters import Characters as c

characters_instance = c()
icon = pg.image.load('resources/icon.ico')
pg.display.set_icon(icon)

class Display:
    def __init__(self, width=512, height=512):
        pg.init()
        self.BASE_WIDTH = width
        self.BASE_HEIGHT = height
        self.centerX = self.BASE_WIDTH // 2
        self.centerY = self.BASE_HEIGHT // 2
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        
        self.screen = pg.display.set_mode((self.BASE_WIDTH, self.BASE_HEIGHT), pg.RESIZABLE)
        pg.display.set_caption("VECTORMASTER")
        
        self.drawing_surface = pg.Surface((self.BASE_WIDTH, self.BASE_HEIGHT))
        self.drawing_surface.fill(self.BLACK)
        self.last_pos = None

    def calculate_scaled_surface(self, window_size):
        window_width, window_height = window_size
        scale = min(window_width / self.BASE_WIDTH, window_height / self.BASE_HEIGHT)
        scaled_width = int(self.BASE_WIDTH * scale)
        scaled_height = int(self.BASE_HEIGHT * scale)
        return scaled_width, scaled_height

    def draw_dot(self, x, y):
        # Convert to screen coordinates first
        screen_x = x + self.BASE_WIDTH // 2
        screen_y = self.BASE_HEIGHT // 2 - y
        # Then snap to grid
        screen_x = round(screen_x / 8) * 8
        screen_y = round(screen_y / 8) * 8
        pg.draw.circle(self.drawing_surface, self.WHITE, (int(screen_x), int(screen_y)), 1)

    def draw_line(self, x1, y1, x2, y2):
        # Convert to screen coordinates first
        screen_x1 = x1 + self.BASE_WIDTH // 2
        screen_y1 = self.BASE_HEIGHT // 2 - y1
        screen_x2 = x2 + self.BASE_WIDTH // 2
        screen_y2 = self.BASE_HEIGHT // 2 - y2
        # Then snap to grid
        screen_x1 = round(screen_x1 / 8) * 8
        screen_y1 = round(screen_y1 / 8) * 8
        screen_x2 = round(screen_x2 / 8) * 8
        screen_y2 = round(screen_y2 / 8) * 8
        pg.draw.line(self.drawing_surface, self.WHITE, 
                    (int(screen_x1), int(screen_y1)), 
                    (int(screen_x2), int(screen_y2)), 2)

    def wrap_character_position(self, x, y, scale):
        # Wrap x coordinate
        screen_x = x * scale
        if screen_x > self.BASE_WIDTH / 2:
            x = -self.BASE_WIDTH / (2 * scale)
        elif screen_x < -self.BASE_WIDTH / 2:
            x = self.BASE_WIDTH / (2 * scale)
            
        # Wrap y coordinate
        screen_y = y * scale
        if screen_y > self.BASE_HEIGHT / 2:
            y = -self.BASE_HEIGHT / (2 * scale)
        elif screen_y < -self.BASE_HEIGHT / 2:
            y = self.BASE_HEIGHT / (2 * scale)
            
        return x, y

    def draw_character(self, x, y, character, scale=1, debug_dots=False, no_penup=False):
        if character not in characters_instance.char_dict:
            return '?'
        
        character = character.lower()
        instructions = characters_instance.char_dict[character]
        current_x, current_y = self.wrap_character_position(x, y, scale)
        drawing = False
        
        if debug_dots:
            self.draw_dot(current_x * scale, current_y * scale)

        for instruction in instructions:
            next_x, next_y = current_x, current_y
            
            if instruction == 'u':
                next_y += 8
            elif instruction == 'd':
                next_y -= 8
            elif instruction == 'l':
                next_x -= 8
            elif instruction == 'r':
                next_x += 8
            elif instruction == 'b':
                drawing = True
            elif instruction == 'e':
                if not no_penup:
                    drawing = False
            elif instruction == '/':
                next_x += 8
                next_y += 8
            elif instruction == '\\':
                next_x += 8
                next_y -= 8
            elif instruction == '.':
                self.draw_dot(current_x * scale, current_y * scale)
            elif instruction == 's':
                break
                
            if drawing:
                self.draw_line(current_x * scale, current_y * scale, next_x * scale, next_y * scale)
            
            current_x, current_y = next_x, next_y

    def draw_string(self, x, y, string, scale=1, debug_dots=False, no_penup=False):
        space = 16
        for char in string.lower():
            if char == 'm' or char == 'w':
                space = 24
            else:
                space = 16
            
            # Draw the character at wrapped position
            wrapped_x, wrapped_y = self.wrap_character_position(x, y, scale)
            self.draw_character(wrapped_x, wrapped_y, char, scale, debug_dots, no_penup)
            
            # Move to next character position
            x += space / scale
            
            # Check if the next character would be past the right edge
            if x * scale > self.BASE_WIDTH / 2 - space:
                x = -self.BASE_WIDTH / (2 * scale)
                y -= 24  # Move down one line
            
            # Also check if somehow we're past the left edge
            if x * scale < -self.BASE_WIDTH / 2:
                x = -self.BASE_WIDTH / (2 * scale)

    def handle_resize(self, event):
        self.screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)

    def clear(self):
        pg.draw.rect(self.drawing_surface, self.BLACK, (0, 0, self.BASE_WIDTH, self.BASE_HEIGHT))


    def update(self):
        window_size = self.screen.get_size()
        scaled_size = self.calculate_scaled_surface(window_size)
        
        scaled_surface = pg.transform.scale(self.drawing_surface, scaled_size)
        self.screen.blit(scaled_surface, 
                        ((window_size[0] - scaled_size[0]) // 2,
                         (window_size[1] - scaled_size[1]) // 2))
        pg.display.flip()