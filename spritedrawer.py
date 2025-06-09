#converts a drawing of lines and dots on a grid into a list of functions to be used in programs
import pygame as pg
import math

class SpriteDrawer:
    def __init__(self, width=512, height=512):
        self.width = width
        self.height = height
        self.grid_size = 16  # Each grid cell is 8x8 pixels
        self.screen = pg.display.set_mode((width, height), pg.RESIZABLE)
        pg.display.set_caption("Sprite Drawer")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        
        # Drawing state
        self.points = []  # List of points in order of drawing
        self.start_point = None  # First point of current line
        self.preview_end = None  # Preview end point for current line
        self.show_grid = True
        self.sprite_name = "sprite"  # Default name
        
        # Center offset (in grid units)
        self.center_x = width // (2 * self.grid_size) * self.grid_size
        self.center_y = height // (2 * self.grid_size) * self.grid_size
        
    def screen_to_grid(self, screen_x, screen_y):
        """Convert screen coordinates to grid coordinates"""
        grid_x = round((screen_x - self.center_x) / self.grid_size)
        grid_y = round(-(screen_y - self.center_y) / self.grid_size)  # Flip Y axis
        return grid_x, grid_y
        
    def grid_to_screen(self, grid_x, grid_y):
        """Convert grid coordinates to screen coordinates"""
        screen_x = self.center_x + grid_x * self.grid_size
        screen_y = self.center_y - grid_y * self.grid_size  # Flip Y axis
        return screen_x, screen_y

    def draw_grid(self):
        """Draw the grid lines"""
        if not self.show_grid:
            return
            
        # Calculate grid boundaries
        left = -self.center_x
        right = self.width - self.center_x
        top = -self.center_y
        bottom = self.height - self.center_y
        
        # Draw horizontal lines
        for y in range(0, self.height + self.grid_size, self.grid_size):
            alpha = 255 if y == self.center_y else 128
            color = (*self.GRAY[:3], alpha)
            pg.draw.line(self.screen, color, (0, y), (self.width, y))
            
        # Draw vertical lines
        for x in range(0, self.width + self.grid_size, self.grid_size):
            alpha = 255 if x == self.center_x else 128
            color = (*self.GRAY[:3], alpha)
            pg.draw.line(self.screen, color, (x, 0), (x, self.height))

    def draw_points(self):
        """Draw all points and lines"""
        # Draw completed lines
        for line in self.points:
            if len(line) > 1:  # If it's a line
                start = self.grid_to_screen(*line[0])
                end = self.grid_to_screen(*line[1])
                pg.draw.line(self.screen, self.WHITE, start, end, 2)
                # Draw endpoints
                pg.draw.circle(self.screen, self.RED, (int(start[0]), int(start[1])), 3)
                pg.draw.circle(self.screen, self.RED, (int(end[0]), int(end[1])), 3)
            elif len(line) == 1:  # If it's a single point
                x, y = self.grid_to_screen(*line[0])
                pg.draw.circle(self.screen, self.WHITE, (int(x), int(y)), 2)
        
        # Draw current line preview
        if self.start_point:
            start = self.grid_to_screen(*self.start_point)
            pg.draw.circle(self.screen, self.YELLOW, (int(start[0]), int(start[1])), 4)
            
            if self.preview_end:
                end = self.grid_to_screen(*self.preview_end)
                pg.draw.line(self.screen, self.YELLOW, start, end, 2)
                pg.draw.circle(self.screen, self.YELLOW, (int(end[0]), int(end[1])), 4)

    def convert_to_function(self):
        """Convert the points into a VecPy function definition"""
        if not self.points:
            return ''
            
        # Start the function definition
        lines = [f"def {self.sprite_name}(x, y, scale=1):"]
        
        # Convert each line/point into draw commands
        for line in self.points:
            if len(line) > 1:  # If it's a line
                start = line[0]
                end = line[1]
                x1, y1 = start[0] * 8, start[1] * 8
                x2, y2 = end[0] * 8, end[1] * 8
                lines.append(f"    screen.draw_line(x + {x1} * scale, y + {y1} * scale, x + {x2} * scale, y + {y2} * scale)")
            elif len(line) == 1:  # If it's a single point
                x, y = line[0][0] * 8, line[0][1] * 8
                lines.append(f"    screen.draw_dot(x + {x} * scale, y + {y} * scale)")
        
        return '\n'.join(lines)

    def run(self):
        running = True
        clock = pg.time.Clock()
        
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                        
                        if not self.start_point:  # First point of line
                            self.start_point = (grid_x, grid_y)
                        else:  # Second point of line
                            # Add the completed line
                            self.points.append([self.start_point, (grid_x, grid_y)])
                            self.start_point = None
                            self.preview_end = None
                            
                    elif event.button == 3:  # Right click - place single dot
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                        self.points.append([(grid_x, grid_y)])  # Add as single-point line
                            
                elif event.type == pg.MOUSEMOTION:
                    if self.start_point:  # Update preview end point
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                        self.preview_end = (grid_x, grid_y)
                        
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_g:  # Toggle grid
                        self.show_grid = not self.show_grid
                    elif event.key == pg.K_c:  # Clear drawing
                        self.points = []
                        self.start_point = None
                        self.preview_end = None
                    elif event.key == pg.K_e:  # Export function
                        print("\nGenerated VecPy function:")
                        print(self.convert_to_function())
                        print("\nUse this function in your VecPy program!")
                    elif event.key == pg.K_n:  # Change sprite name
                        name = input("Enter sprite name: ")
                        if name.isidentifier():  # Check if it's a valid Python identifier
                            self.sprite_name = name
                        else:
                            print("Invalid name! Using default name 'sprite'")
                    elif event.key == pg.K_z and (pg.key.get_mods() & pg.KMOD_CTRL):  # Undo
                        if self.points:
                            self.points.pop()
                    elif event.key == pg.K_ESCAPE:  # Cancel current line
                        self.start_point = None
                        self.preview_end = None
                        
                elif event.type == pg.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                    # Keep center in grid units to prevent offset
                    self.center_x = self.width // (2 * self.grid_size) * self.grid_size
                    self.center_y = self.height // (2 * self.grid_size) * self.grid_size
                    self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
            
            # Draw everything
            self.screen.fill(self.BLACK)
            self.draw_grid()
            self.draw_points()
            pg.display.flip()
            
            clock.tick(60)

if __name__ == '__main__':
    drawer = SpriteDrawer()
    drawer.run()

