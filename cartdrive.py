#parses the vector to a temporary file to be used by the main program
#It gets messy sometimes, y'know? Code generating code.


import runpy
import os

diskpath = 'disk/'

class VecPyParser:
    def __init__(self):
        self.key = {
            'type': 'draw_string',
            'stop()': 'running = False',
            'if break': 'if event.key == pg.K_LCTRL and event.key == pg.K_b: running = False',
            'import main': 'import pygame as pg',
            'import screen': 'from display import Display as d\n\nvector_display = d()',
            'import aliases': 'screen = vector_display',
            'import audio': 'from audio import Audio as a\n\naudio = a()',
            'tone': 'audio.play_tone',
            'key_delay': 'pg.key.set_repeat',
            'get_events': 'event in pg.event.get()',
            'quit_event': 'event.type == pg.QUIT',
            'resize_event': 'event.type == pg.VIDEORESIZE',
            'key_down_event': 'event.type == pg.KEYDOWN',
            'key_': 'event.key == pg.K_',
            'special_key': 'event.key == pg.K_b and pg.key.get_mods() & pg.KMOD_CTRL'
        }
    def parse_keys(self, filename): #take all the lines, parse them, remove comments, and put them into a temporary file
        file_path = os.path.join(diskpath, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Program file not found: {file_path}")
            
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        processed_lines = []
        for line in lines:
            # Preserve the indentation by counting leading spaces
            indentation = len(line) - len(line.lstrip())
            spaces = ' ' * indentation
            
            # Process the actual content
            processed_line = line.lstrip()
            for k, v in self.key.items():
                processed_line = processed_line.replace(k, v)
            
            # Remove comments only if # is at the start of the line (after whitespace)
            if processed_line.lstrip().startswith('#'):
                processed_line = ''
            
            # Strip trailing whitespace
            processed_line = processed_line.rstrip()
            
            # Only write non-empty lines with proper indentation
            if processed_line:
                processed_lines.append(spaces + processed_line + '\n')
        
        # Write all processed lines to temp.py
        with open('temp.py', 'w') as file:  # Changed to 'w' mode to overwrite
            file.writelines(processed_lines)
    def reset(self):
        if os.path.exists('temp.py'):
            os.remove('temp.py')
    def run(self):
        if os.path.exists('temp.py'):
            try:
                runpy.run_path('temp.py')
            except Exception as e:
                print(f"#!#!#!#!# Program error: {e} #!#!#!#!#")
        else:
            print('No file to run or the temp file was not found at ' + diskpath + 'temp.py for some reason. (How???)')
