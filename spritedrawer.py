#converts a drawing of lines and dots on a grid into a list of functions to be used in programs
import pygame as pg
import math
import os
from tkinter import filedialog
import tkinter as tk

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
        
        # Reference image properties
        self.reference_image = None
        self.reference_surface = None
        self.show_reference = True
        self.reference_alpha = 128  # 0-255, controls image transparency
        self.ref_x = 0  # Position offset for reference image
        self.ref_y = 0
        self.ref_scale = 1.0  # Scale factor for reference image
        self.dragging_image = False
        self.drag_start = None
        self.initial_ref_pos = None
        
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

    def find_closest_line_or_point(self, mouse_x, mouse_y, threshold=10):
        """Find the closest line or point to the given mouse coordinates"""
        closest_dist = float('inf')
        closest_idx = -1
        is_point = False

        mouse_grid_x, mouse_grid_y = self.screen_to_grid(mouse_x, mouse_y)
        mouse_screen_x, mouse_screen_y = self.grid_to_screen(mouse_grid_x, mouse_grid_y)

        for idx, line in enumerate(self.points):
            if len(line) == 1:  # Single point
                px, py = self.grid_to_screen(*line[0])
                dist = math.sqrt((px - mouse_x)**2 + (py - mouse_y)**2)
                if dist < closest_dist and dist < threshold:
                    closest_dist = dist
                    closest_idx = idx
                    is_point = True
            else:  # Line
                x1, y1 = self.grid_to_screen(*line[0])
                x2, y2 = self.grid_to_screen(*line[1])
                
                # Calculate distance to line segment
                line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                if line_length == 0:
                    continue
                
                # Calculate the distance from point to line segment
                t = max(0, min(1, ((mouse_x - x1) * (x2 - x1) + (mouse_y - y1) * (y2 - y1)) / (line_length * line_length)))
                proj_x = x1 + t * (x2 - x1)
                proj_y = y1 + t * (y2 - y1)
                dist = math.sqrt((mouse_x - proj_x)**2 + (mouse_y - proj_y)**2)
                
                if dist < closest_dist and dist < threshold:
                    closest_dist = dist
                    closest_idx = idx
                    is_point = False

        return closest_idx, is_point if closest_idx != -1 else None

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

    def load_reference_image(self):
        """Open a file dialog to load a reference image"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        file_path = filedialog.askopenfilename(
            title="Select Reference Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        root.destroy()
        
        if file_path:
            try:
                # Load the image and convert it to have an alpha channel
                self.reference_image = pg.image.load(file_path).convert_alpha()
                # Store original size for scaling
                self.original_width = self.reference_image.get_width()
                self.original_height = self.reference_image.get_height()
                # Center the image initially
                self.ref_x = (self.width - self.original_width) // 2
                self.ref_y = (self.height - self.original_height) // 2
                self.ref_scale = 1.0
                self.update_reference_surface()
                return True
            except Exception as e:
                print(f"Error loading image: {e}")
                return False
        return False

    def update_reference_surface(self):
        """Update the reference surface with current alpha value and scale"""
        if self.reference_image:
            # Calculate new dimensions
            new_width = int(self.original_width * self.ref_scale)
            new_height = int(self.original_height * self.ref_scale)
            
            # Scale the image
            scaled_image = pg.transform.scale(self.reference_image, (new_width, new_height))
            
            # Apply transparency
            self.reference_surface = scaled_image.copy()
            self.reference_surface.fill((255, 255, 255, self.reference_alpha), special_flags=pg.BLEND_RGBA_MULT)

    def draw_reference_image(self):
        """Draw the reference image if it exists and is visible"""
        if self.reference_surface and self.show_reference:
            self.screen.blit(self.reference_surface, (self.ref_x, self.ref_y))

    def handle_image_drag(self, mouse_pos, is_start=False, is_end=False):
        """Handle dragging of the reference image"""
        if not self.reference_surface or not self.show_reference:
            return

        if is_start:
            # Check if click is within image bounds
            img_rect = self.reference_surface.get_rect(topleft=(self.ref_x, self.ref_y))
            if img_rect.collidepoint(mouse_pos):
                self.dragging_image = True
                self.drag_start = mouse_pos
                self.initial_ref_pos = (self.ref_x, self.ref_y)
        elif is_end:
            self.dragging_image = False
        elif self.dragging_image:
            # Calculate the difference from drag start
            dx = mouse_pos[0] - self.drag_start[0]
            dy = mouse_pos[1] - self.drag_start[1]
            # Update image position
            self.ref_x = self.initial_ref_pos[0] + dx
            self.ref_y = self.initial_ref_pos[1] + dy

    def run(self):
        running = True
        clock = pg.time.Clock()
        
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if pg.key.get_mods() & pg.KMOD_ALT:  # Alt + Left click for image drag
                            self.handle_image_drag(event.pos, is_start=True)
                        else:  # Normal drawing
                            mouse_x, mouse_y = pg.mouse.get_pos()
                            grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                            if not self.start_point:
                                self.start_point = (grid_x, grid_y)
                            else:
                                self.points.append([self.start_point, (grid_x, grid_y)])
                                self.start_point = None
                                self.preview_end = None
                    elif event.button == 2:  # Middle click - delete line/point
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        closest_idx, is_point = self.find_closest_line_or_point(mouse_x, mouse_y)
                        if closest_idx != -1:
                            self.points.pop(closest_idx)
                    elif event.button == 3:  # Right click - place single dot
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
                        self.points.append([(grid_x, grid_y)])
                    elif event.button == 4:  # Mouse wheel up - scale up reference image
                        if pg.key.get_mods() & pg.KMOD_ALT:
                            self.ref_scale = min(5.0, self.ref_scale * 1.1)
                            self.update_reference_surface()
                    elif event.button == 5:  # Mouse wheel down - scale down reference image
                        if pg.key.get_mods() & pg.KMOD_ALT:
                            self.ref_scale = max(0.1, self.ref_scale / 1.1)
                            self.update_reference_surface()
                            
                elif event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.handle_image_drag(event.pos, is_end=True)
                            
                elif event.type == pg.MOUSEMOTION:
                    self.handle_image_drag(event.pos)
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
                        if name.isidentifier():
                            self.sprite_name = name
                        else:
                            print("Invalid name! Using default name 'sprite'")
                    elif event.key == pg.K_z and (pg.key.get_mods() & pg.KMOD_CTRL):  # Undo
                        if self.points:
                            self.points.pop()
                    elif event.key == pg.K_ESCAPE:  # Cancel current line
                        self.start_point = None
                        self.preview_end = None
                    elif event.key == pg.K_EQUALS:
                        old_grid_size = self.grid_size
                        self.grid_size += 4
                        # Adjust center to maintain grid alignment
                        self.center_x = self.width // (2 * self.grid_size) * self.grid_size
                        self.center_y = self.height // (2 * self.grid_size) * self.grid_size
                    elif event.key == pg.K_MINUS:
                        if self.grid_size > 4:  # Prevent grid from becoming too small
                            old_grid_size = self.grid_size
                            self.grid_size -= 4
                            # Adjust center to maintain grid alignment
                            self.center_x = self.width // (2 * self.grid_size) * self.grid_size
                            self.center_y = self.height // (2 * self.grid_size) * self.grid_size
                    elif event.key == pg.K_i:  # Import reference image
                        self.load_reference_image()
                    elif event.key == pg.K_r:  # Toggle reference image
                        self.show_reference = not self.show_reference
                    elif event.key == pg.K_UP:  # Increase reference image opacity
                        self.reference_alpha = min(255, self.reference_alpha + 16)
                        self.update_reference_surface()
                    elif event.key == pg.K_DOWN:  # Decrease reference image opacity
                        self.reference_alpha = max(0, self.reference_alpha - 16)
                        self.update_reference_surface()
                        
                elif event.type == pg.VIDEORESIZE:
                    old_width = self.width
                    old_height = self.height
                    self.width = event.w
                    self.height = event.h
                    # Adjust center to maintain grid alignment
                    self.center_x = self.width // (2 * self.grid_size) * self.grid_size
                    self.center_y = self.height // (2 * self.grid_size) * self.grid_size
                    self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
            
            # Draw everything
            self.screen.fill(self.BLACK)
            self.draw_reference_image()  # Draw reference image first
            self.draw_grid()
            self.draw_points()
            pg.display.flip()
            
            clock.tick(60)

if __name__ == '__main__':
    drawer = SpriteDrawer()
    drawer.run()

