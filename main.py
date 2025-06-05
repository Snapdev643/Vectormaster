import pygame as pg
import time
import os
from display import Display as d
from characters import Characters as c
from cartdrive import VecPyParser
from audio import Audio as a

vector_display = d()
characters_instance = c()
parser = VecPyParser()
audio = a()

#debug_file = "demos/toby_fox.vecpy"
#parser.parse_keys(debug_file)

pg.key.set_repeat()

def get_programs():
    def scan_directory(current_path=""):
        items = []
        full_path = os.path.join("disk", current_path)
        
        # First add all directories
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            relative_path = os.path.join(current_path, item)
            
            if os.path.isdir(item_path):
                # Recursively scan subdirectory
                subitems = scan_directory(relative_path)
                if subitems:  # Only add non-empty directories
                    items.append(("dir", item, relative_path, subitems))
        
        # Then add all .vecpy files
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            relative_path = os.path.join(current_path, item)
            
            if os.path.isfile(item_path) and item.endswith(".vecpy"):
                items.append(("file", item, relative_path, None))
        
        return items
    
    return scan_directory()

def run_program(program_name):
    parser.reset()
    parser.parse_keys(program_name)
    try:
        parser.run()
    except Exception as e:
        print(f"Program error: {e}")
    finally:
        # Ensure we clean up after program execution
        parser.reset()
        # Reset key repeat settings to default (disabled)
        pg.key.set_repeat()

def bios():
    vector_display.clear()
    vector_display.draw_string(-176, 240, "*****VectorMaster*****", 1)
    vector_display.update()
    time.sleep(1)
    vector_display.clear()
    vector_display.update()
    vector_display.draw_string(-176, 240, "Running self checks", 1)
    vector_display.update()
    time.sleep(1)
    vector_display.clear()
    vector_display.update()
    vector_display.draw_string(-176, 240, "Self checks complete", 1)
    vector_display.update()
    audio.play_tone(0, 0, 15, 940, 0.01)
    time.sleep(0.1)
    audio.play_tone(0, 0, 15, 1080, 0.01)
    time.sleep(0.5)

def draw_program_list(items, selected_index, current_path=""):
    vector_display.clear()
    vector_display.draw_string(-176, 240, "*****VectorMaster*****", 1)
    
    # Show current path
    if current_path:
        vector_display.draw_string(-256, 216, f"/{current_path}", 1)
    else:
        vector_display.draw_string(-256, 216, "Select a program:", 1)
    
    y_pos = 192
    for i, (item_type, name, _, _) in enumerate(items):
        cursor = ">" if i == selected_index else " "
        prefix = "[+] " if item_type == "dir" else "    "
        vector_display.draw_string(-256, y_pos, f"{cursor}{prefix}{name}", 1)
        y_pos -= 24
    
    if current_path:
        vector_display.draw_string(-256, -216, "U/D: Sel, Enter: Open, Esc: Back", 1)
    else:
        vector_display.draw_string(-256, -216, "U/D: Sel, Enter: Open, Esc: Exit", 1)
    vector_display.update()

def kernel():
    program_tree = get_programs()
    if not program_tree:
        vector_display.draw_string(-256, 240, "No .vecpy programs found in disk/", 1)
        vector_display.update()
        return
    
    # Stack to keep track of navigation history
    nav_stack = [(program_tree, 0)]  # (items, selected_index)
    program_running = False
    running = True
    
    while running:
        if not program_running:
            current_items, selected_index = nav_stack[-1]
            # Get the path by looking at parent directories in the stack
            current_path = ""
            for items, idx in nav_stack[:-1]:
                _, name, _, _ = items[idx]
                current_path = os.path.join(current_path, name)
            draw_program_list(current_items, selected_index, current_path)
            
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            elif event.type == pg.VIDEORESIZE:
                vector_display.handle_resize(event)
            
            elif event.type == pg.KEYDOWN:
                if not program_running:
                    current_items, selected_index = nav_stack[-1]
                    
                    if event.key == pg.K_ESCAPE:
                        if len(nav_stack) > 1:
                            nav_stack.pop()  # Go back one level
                            audio.play_tone(0, 1, 15, 440, 0.01)
                        else:
                            running = False
                    
                    elif event.key == pg.K_UP:
                        nav_stack[-1] = (current_items, (selected_index - 1) % len(current_items))
                        audio.play_tone(0, 1, 15, 520, 0.01)
                    
                    elif event.key == pg.K_DOWN:
                        nav_stack[-1] = (current_items, (selected_index + 1) % len(current_items))
                        audio.play_tone(0, 1, 15, 440, 0.01)
                    
                    elif event.key == pg.K_RETURN:
                        item_type, _, path, subitems = current_items[selected_index]
                        if item_type == "dir":
                            nav_stack.append((subitems, 0))  # Enter directory
                            audio.play_tone(0, 1, 15, 660, 0.01)
                        else:  # file
                            audio.play_tone(0, 1, 15, 880, 0.01)
                            program_running = True
                            vector_display.clear()
                            run_program(path)
                            program_running = False
                            vector_display.clear()
                
                elif event.key == pg.K_b and pg.key.get_mods() & pg.KMOD_RCTRL:
                    program_running = False
                    parser.reset()
                    vector_display.clear()
                    audio.play_tone(0, 1, 15, 820, 0.01)

    pg.quit()
    parser.reset()

bios()

if __name__ == "__main__":
    pg.key.set_repeat()
    kernel()