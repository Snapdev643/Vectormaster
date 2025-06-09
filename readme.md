# Welcome to VectorMaster!

VectorMaster is a vector graphics engine that allows you to create and run vector-based programs. I made this with Python and Pygame. In the universe for my Snapverse games, VectorMaster is a desktop computer, and a predecessor to the AntiAuto.

## Features

### Engine Features
- Vector-based graphics rendering system
- Resizable display window
- Built-in audio synthesis capabilities
- Custom VectorPy scripting language (Python-like syntax)
- File browser interface

### Graphics Capabilities
- Vector line drawing
- Dot plotting
- Text rendering with custom vector font
- Screen clearing and updating
- Coordinate system with origin at center (512x512 resolution)

### Audio System
- 2 sound channels (0-1)
- 16 waveform types (17 for noise on channel 1)
- 4-bit volume (0-15)
- Frequency control (20-1600 Hz)

### Demo Programs
- **Starfield**: Starfield with trailing effects
- **Lines**: Cool line patterns
- **Dots**: Random dots
- **Waveform**: Audio waveform editor and visualizer
- **Elite Demo**: 3D wireframe planet renderer with camera controls
- **Notepad**: A simple notepad
- **Toby Fox**: A very buggy Undertale/Deltarune-style battle system demo
- **Music**: A test script for playing music
- **Sorting**: A sorting algorithm demo

### Input Handling
- Keyboard input support
- Event-based input processing
- Window resize handling
- Program exit controls

## Getting Started

1. Run the main program to launch VectorMaster
2. Use the built-in file browser to navigate through available demos
3. Select a demo using the arrow keys and Enter
4. Press Ctrl+B to exit any running program
5. Use Escape to navigate back or exit the file browser

## Dependencies

- Python 3.10+ (I'm using 3.13.1)
- Pygame 2.5.0+ (I'm using 2.6.1)

## Controls

- Arrow keys: Navigate menus and control demos
- Enter: Select/Confirm
- Escape: Back/Exit
- Ctrl+B: Force quit running program
- Space: Reset/Restart (in supported demos)

## Changelog:

- 0.0.1: Initial release (06/04/25)
- 0.0.2: Added import essentials (adds main, screen, audio, and aliases), a sorting demo, a characters demo, separated and updated the file explorer and main program, debug_dots and no_penup added to draw_string and draw_character, improved string wrapping, and updated the bios sounds. (06/06/25)
- 0.0.3: Improved noise generation, added a sprite drawer, removed the silent waveform, updated and made the notepad demo into a system program, added the ability to make hidden files that won't be shown in the file explorer (.vecpyh) and added init_mods & keymod_ for the parser. (06/07/25)