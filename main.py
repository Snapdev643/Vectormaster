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

pg.key.set_repeat() #no key repeat, please! (makes weird noises! and an unusable UI!)

def bios():
    if os.path.exists("temp.py"):
        os.remove("temp.py")
        print("leftover temp.py deleted, didya crash? Syntax error? 🤔")
    else:
        print("No temp.py to delete... Safe for now... 😝")
    vector_display.clear()
    vector_display.draw_string(-176, 240, "*****VectorMaster*****", 1)
    vector_display.update()
    time.sleep(1)
    vector_display.clear()
    vector_display.update()
    vector_display.draw_string(-176, 240, "Running self checks", 1)
    vector_display.update()
    time.sleep(0.5)
    vector_display.clear()
    vector_display.update()
    vector_display.draw_string(-176, 240, "Self checks complete", 1)
    vector_display.update()
    audio.play_tone(0, 6, 15, 940, 0.01)
    time.sleep(0.1)
    audio.play_tone(0, 6, 15, 1080, 0.0235)
    time.sleep(0.5)

bios()

if __name__ == "__main__":
    try:
        while True:
            pg.key.set_repeat()
            try:
                parser.parse_keys("FE.vecpyh")
                parser.run()
                print("Running the file explorer...")
            except SystemExit:
                break
            except:
                pass
            parser.reset()
    finally:
        parser.reset()
        pg.quit()