# 🎮 MACAN TETRIS NEO - ARCADE MODE (HARDCORE EDITION)

A futuristic, neon-infused Tetris game with brutal arcade-style gameplay, featuring cyberpunk aesthetics, smooth animations, and a hardcore speed progression system.

![Version](https://img.shields.io/badge/version-2.0-ff00ff)
![Python](https://img.shields.io/badge/python-3.8+-00ffff)
![License](https://img.shields.io/badge/license-MIT-00ff00)

## 🌟 Features

### Arcade Mode Enhancements
- **Speed Progression**: Automatic speed increase every 30 seconds
- **Combo System**: Chain line clears for massive score multipliers
- **Fever Mode**: Clear 4 lines at once to trigger a 3-second fever state with glowing effects
- **Persistent High Score**: Your best scores are saved locally
- **Flash Effects**: Smooth opacity animations when clearing lines
- **Speed Meter**: Visual representation of current game speed

### Futuristic UI Design
- **Neon Color Palette**: Cyan, magenta, and red glowing elements
- **Holographic Panels**: Left and right side panels with translucent effects
- **Glowing Grid**: Arcade-style illuminated game board
- **Cyberpunk Background**: Dark gradient with purple-blue tones
- **Digital Font**: Monospace "Courier New" with text-shadow glow effects
- **Smooth Animations**: Fluid piece movements and line clear effects

### Core Gameplay
- Standard Tetris mechanics (rotation, movement, fast drop)
- 10x20 game board
- 7 classic Tetromino shapes (I, O, T, S, Z, J, L)
- Collision detection and line clearing
- Game over detection
- Auto-drop with increasing speed

## 🎯 Gameplay Rules

### Controls
- **Arrow Left/Right**: Move piece horizontally
- **Arrow Down**: Soft drop (move piece down faster)
- **Arrow Up**: Rotate piece clockwise
- **Space**: Hard drop (instant placement)

### Scoring System
- **Single Line**: 100 points × combo multiplier
- **Multiple Lines**: 100 × lines × combo multiplier
- **Combo System**: Consecutive line clears increase multiplier
- **Fever Mode Bonus**: Triggered by clearing 4 lines (Tetris)

### Speed Progression
- Speed increases automatically every 30 seconds
- Each speed increase makes the game 15% faster
- Minimum interval: 100ms (maximum difficulty)
- Visual speed meter shows current intensity

### Fever Mode
- Activated when clearing 4 lines at once
- Lasts for 3 seconds
- Board glows with cyan-magenta gradient
- Provides a visual celebration of skill

## 📸 Screenshot
<img width="1000" height="733" alt="Screenshot 2025-12-10 193904" src="https://github.com/user-attachments/assets/0237dad4-5767-42b4-a1dc-5583b30833c6" />


## 🚀 Installation & Running

### Requirements
```bash
Python 3.8 or higher
PySide6
```

### Install Dependencies
```bash
pip install PySide6
```

### Run the Game
```bash
python main.py
```

## 📦 Building to Executable

### Using PyInstaller

1. **Install PyInstaller**
```bash
pip install pyinstaller
```

2. **Build for Windows**
```bash
pyinstaller --onefile --windowed --name "MacanTetrisNeo" main.py
```

3. **Build for Linux/Mac**
```bash
pyinstaller --onefile --windowed --name "MacanTetrisNeo" main.py
```

The executable will be in the `dist/` folder.

### Alternative: Using Nuitka (Better Performance)
```bash
pip install nuitka
python -m nuitka --standalone --onefile --enable-plugin=pyside6 main.py
```

## 💾 Save System

Game state is automatically saved to:

- **Windows**: `%LOCALAPPDATA%/MacanTetrisNeoArcade/state.json`
- **Linux**: `~/.local/share/MacanTetrisNeoArcade/state.json`
- **macOS**: `~/.local/share/MacanTetrisNeoArcade/state.json`

### Saved Data
- High score
- Current score (on game over)
- Level
- Speed
- Combo state
- Board state
- Lines cleared

## 🎨 UI Architecture

### Layout Structure
```
┌─────────────────────────────────────────────────────┐
│                  MACAN TETRIS NEO                   │
├──────────┬────────────────────────┬─────────────────┤
│  LEFT    │       CENTER           │     RIGHT       │
│  PANEL   │       BOARD            │     PANEL       │
│          │                        │                 │
│ Score    │   10x20 Game Grid      │  Arcade Mode    │
│ Level    │   Neon Glow Effect     │  Hardcore       │
│ High     │   Fever Mode Flash     │                 │
│ Combo    │                        │  Speed Meter    │
│          │                        │  [Visual Bar]   │
│ Next     │                        │                 │
│ Piece    │                        │  Fever Label    │
│ Widget   │                        │                 │
│          │                        │                 │
└──────────┴────────────────────────┴─────────────────┘
                © 2025 MACAN ANGKASA
```

### Color Scheme
- **Primary**: Cyan (#00ffff) - Grid, labels
- **Secondary**: Magenta (#ff00ff) - Title, borders
- **Accent**: Red (#ff0000) - Fever, warnings
- **Background**: Dark Purple gradient (#0a0015 → #1e003c)
- **Highlight**: Yellow (#ffff00) - High score, fever text

### Visual Effects
1. **Text Glow**: CSS text-shadow with dual-layer glow
2. **Board Glow**: Semi-transparent grid lines with neon effect
3. **Fever Mode**: Linear gradient overlay with animation
4. **Flash Animation**: QPropertyAnimation for line clears
5. **Block Rendering**: Inner highlight + outer glow

## 🔊 Audio System (Hooks Ready)

The game includes placeholder audio hooks for future sound implementation:

```python
play_line_clear_sound()    # Triggered on line clear
play_move_sound()          # Triggered on piece movement
play_arcade_fever_sound()  # Triggered on fever mode activation
```

To add sounds, integrate libraries like:
- `pygame.mixer` (simple)
- `QSoundEffect` (PySide6 native)
- `python-sounddevice` (advanced)

## 📁 File Structure

```
MacanTetrisNeoArcade/
├── main.py              # Main game file (all-in-one)
├── README.md            # This file
└── state.json          # Auto-generated save file
```

### Code Organization (main.py)

- **GlowLabel**: Custom QLabel with neon glow effect
- **ArcadeBoard**: Game board widget with rendering logic
- **NextPieceWidget**: Preview widget for upcoming piece
- **SpeedMeter**: Visual speed indicator
- **MacanTetrisNeo**: Main game window and logic controller

## 🎓 Technical Highlights

### OOP Design
- Clean separation of UI widgets and game logic
- Each widget handles its own rendering
- Event-driven architecture with Qt signals/timers
- Modular component design

### Performance Optimizations
- Efficient collision detection (early exit on invalid positions)
- Double-buffered rendering via Qt
- Minimal repaints (update() only when needed)
- Optimized animation timers

### Modern Qt Features
- QPropertyAnimation for smooth effects
- QLinearGradient for cyberpunk aesthetics
- QPainter with antialiasing for crisp graphics
- QTimer for precise game timing

## 🐛 Known Issues & Future Enhancements

### Potential Improvements
- [ ] Add background music loop
- [ ] Implement particle effects on line clear
- [ ] Add leaderboard with online sync
- [ ] Create multiple difficulty presets
- [ ] Add ghost piece (piece preview)
- [ ] Implement hold piece feature
- [ ] Add screen shake on Tetris clear
- [ ] Create attract mode for idle state

## 📜 Copyright & License

**© 2025 MACAN ANGKASA**

This project is released under the MIT License.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Share your high scores

## 🏆 Credits

**Game Design**: Macan Angkasa Team  
**UI/UX**: Cyberpunk Arcade Aesthetic  
**Framework**: PySide6 (Qt for Python)  
**Inspiration**: Classic arcade Tetris + modern neon aesthetics

---

**Enjoy the neon-soaked, hardcore arcade experience! 🎮✨**

*For support or feedback, create an issue in the repository.*
