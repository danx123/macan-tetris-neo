import sys
import json
import random
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QFrame, QPushButton)
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QRect, Property
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QPalette

# Tetromino shapes
SHAPES = {
    'I': [[1,1,1,1]], 'O': [[1,1],[1,1]], 'T': [[0,1,0],[1,1,1]], 
    'S': [[0,1,1],[1,1,0]], 'Z': [[1,1,0],[0,1,1]], 
    'J': [[1,0,0],[1,1,1]], 'L': [[0,0,1],[1,1,1]]
}
COLORS = {
    'I': QColor(0, 255, 255), 'O': QColor(255, 255, 0), 'T': QColor(255, 0, 255),
    'S': QColor(0, 255, 0), 'Z': QColor(255, 0, 0), 'J': QColor(0, 0, 255), 'L': QColor(255, 165, 0)
}

class GlowLabel(QLabel):
    def __init__(self, text, size=16, color='#00ffff'):
        super().__init__(text)
        self.setStyleSheet(f'''
            QLabel {{
                color: {color};
                font-size: {size}px;
                font-family: "Courier New", monospace;
                font-weight: bold;
                text-shadow: 0 0 10px {color}, 0 0 20px {color};
            }}
        ''')

class ArcadeBoard(QFrame):
    def __init__(self):
        super().__init__()
        self.board = [[None for _ in range(10)] for _ in range(20)]
        self.current_piece = None
        self.current_pos = [0, 0]
        self.current_shape = None
        self.fever_mode = False
        self.clearing_lines = []
        self._flash_opacity = 0
        self.setMinimumSize(400, 600)
        self.setStyleSheet('''
            ArcadeBoard {
                background-color: #0a0015;
                border: 3px solid #00ffff;
                border-radius: 10px;
            }
        ''')

    def get_flash_opacity(self):
        return self._flash_opacity

    def set_flash_opacity(self, value):
        self._flash_opacity = value
        self.update()

    flash_opacity = Property(int, get_flash_opacity, set_flash_opacity)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        cell_w, cell_h = w / 10, h / 20
        
        # Draw grid with glow
        pen = QPen(QColor(100, 100, 255, 40))
        pen.setWidth(1)
        painter.setPen(pen)
        for i in range(21):
            y = i * cell_h
            painter.drawLine(0, int(y), w, int(y))
        for i in range(11):
            x = i * cell_w
            painter.drawLine(int(x), 0, int(x), h)
        
        # Draw fever mode glow
        if self.fever_mode:
            gradient = QLinearGradient(0, 0, w, h)
            gradient.setColorAt(0, QColor(255, 0, 255, 30))
            gradient.setColorAt(1, QColor(0, 255, 255, 30))
            painter.fillRect(0, 0, w, h, gradient)
        
        # Draw placed blocks
        for y in range(20):
            for x in range(10):
                if self.board[y][x]:
                    color = self.board[y][x]
                    self.draw_block(painter, x, y, color, cell_w, cell_h)
        
        # Draw current piece
        if self.current_piece and self.current_shape:
            cy, cx = self.current_pos
            for y, row in enumerate(self.current_shape):
                for x, val in enumerate(row):
                    if val:
                        color = COLORS[self.current_piece]
                        self.draw_block(painter, cx + x, cy + y, color, cell_w, cell_h, True)
        
        # Draw flash effect for clearing lines
        if self.clearing_lines and self._flash_opacity > 0:
            painter.setOpacity(self._flash_opacity / 100.0)
            for line_y in self.clearing_lines:
                painter.fillRect(0, int(line_y * cell_h), w, int(cell_h), QColor(255, 255, 255))
            painter.setOpacity(1.0)

    def draw_block(self, painter, x, y, color, cw, ch, glow=False):
        rect = QRect(int(x * cw + 2), int(y * ch + 2), int(cw - 4), int(ch - 4))
        
        # Outer glow
        if glow:
            glow_color = QColor(color)
            glow_color.setAlpha(100)
            painter.setPen(QPen(glow_color, 3))
        else:
            painter.setPen(Qt.NoPen)
        
        painter.setBrush(color)
        painter.drawRect(rect)
        
        # Inner highlight
        highlight = QColor(255, 255, 255, 80)
        painter.fillRect(int(x * cw + 4), int(y * ch + 4), int(cw - 8), int((ch - 8) / 3), highlight)

class NextPieceWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.next_piece = None
        self.next_shape = None
        self.setFixedSize(120, 120)
        self.setStyleSheet('''
            NextPieceWidget {
                background-color: rgba(10, 0, 30, 150);
                border: 2px solid #ff00ff;
                border-radius: 8px;
            }
        ''')

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.next_shape or not self.next_piece:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rows, cols = len(self.next_shape), len(self.next_shape[0])
        cell_size = min(100 / cols, 100 / rows)
        offset_x = (120 - cols * cell_size) / 2
        offset_y = (120 - rows * cell_size) / 2
        
        color = COLORS[self.next_piece]
        for y, row in enumerate(self.next_shape):
            for x, val in enumerate(row):
                if val:
                    rect = QRect(int(offset_x + x * cell_size), int(offset_y + y * cell_size),
                                int(cell_size - 2), int(cell_size - 2))
                    painter.setBrush(color)
                    painter.setPen(Qt.NoPen)
                    painter.drawRect(rect)

class SpeedMeter(QFrame):
    def __init__(self):
        super().__init__()
        self.speed_level = 1
        self.setFixedSize(30, 300)
        self.setStyleSheet('''
            SpeedMeter {
                background-color: rgba(10, 0, 30, 150);
                border: 2px solid #ff0000;
                border-radius: 5px;
            }
        ''')

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        fill_height = int((self.speed_level / 20) * 290)
        gradient = QLinearGradient(0, 290, 0, 0)
        gradient.setColorAt(0, QColor(0, 255, 0))
        gradient.setColorAt(0.5, QColor(255, 255, 0))
        gradient.setColorAt(1, QColor(255, 0, 0))
        
        painter.fillRect(5, 295 - fill_height, 20, fill_height, gradient)

class MacanTetrisNeo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MACAN TETRIS NEO - ARCADE MODE")
        self.setFixedSize(1000, 700)
        
        # Game state
        self.score = 0
        self.level = 1
        self.high_score = 0
        self.combo = 0
        self.lines_cleared = 0
        self.speed = 1000
        self.game_active = False
        self.fever_mode_active = False
        
        # Timers
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.game_tick)
        self.speed_timer = QTimer()
        self.speed_timer.timeout.connect(self.increase_speed)
        self.fever_timer = QTimer()
        self.fever_timer.timeout.connect(self.deactivate_fever)
        
        self.init_ui()
        self.load_state()
        self.new_game()

    def init_ui(self):
        # Dark gradient background
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 700)
        gradient.setColorAt(0, QColor(10, 0, 30))
        gradient.setColorAt(1, QColor(30, 0, 60))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel
        left_panel = QVBoxLayout()
        self.title_label = GlowLabel("MACAN TETRIS NEO", 24, '#ff00ff')
        self.title_label.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(self.title_label)
        
        left_panel.addSpacing(20)
        left_panel.addWidget(GlowLabel("SCORE", 14, '#00ffff'))
        self.score_label = GlowLabel("0", 28, '#ffffff')
        left_panel.addWidget(self.score_label)
        
        left_panel.addSpacing(10)
        left_panel.addWidget(GlowLabel("LEVEL", 14, '#00ffff'))
        self.level_label = GlowLabel("1", 28, '#ffffff')
        left_panel.addWidget(self.level_label)
        
        left_panel.addSpacing(10)
        left_panel.addWidget(GlowLabel("HIGH SCORE", 14, '#ff00ff'))
        self.high_score_label = GlowLabel("0", 20, '#ffff00')
        left_panel.addWidget(self.high_score_label)
        
        left_panel.addSpacing(10)
        left_panel.addWidget(GlowLabel("COMBO", 14, '#00ffff'))
        self.combo_label = GlowLabel("x0", 20, '#ff0000')
        left_panel.addWidget(self.combo_label)
        
        left_panel.addSpacing(20)
        left_panel.addWidget(GlowLabel("NEXT PIECE", 14, '#00ffff'))
        self.next_widget = NextPieceWidget()
        left_panel.addWidget(self.next_widget)
        
        left_panel.addStretch()
        
        # Center - Board
        center_layout = QVBoxLayout()
        self.board_widget = ArcadeBoard()
        center_layout.addWidget(self.board_widget)
        
        # Game over overlay
        self.game_over_label = GlowLabel("GAME OVER", 36, '#ff0000')
        self.game_over_label.setAlignment(Qt.AlignCenter)
        self.game_over_label.hide()
        
        self.restart_btn = QPushButton("RESTART")
        self.restart_btn.setStyleSheet('''
            QPushButton {
                background-color: #ff00ff;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 8px;
                border: 2px solid #00ffff;
            }
            QPushButton:hover {
                background-color: #00ffff;
                color: black;
            }
        ''')
        self.restart_btn.clicked.connect(self.new_game)
        self.restart_btn.hide()
        
        center_layout.addWidget(self.game_over_label)
        center_layout.addWidget(self.restart_btn, alignment=Qt.AlignCenter)
        
        # Right panel
        right_panel = QVBoxLayout()
        right_panel.addWidget(GlowLabel("ARCADE MODE", 16, '#ff00ff'))
        right_panel.addWidget(GlowLabel("HARDCORE", 14, '#ff0000'))
        
        right_panel.addSpacing(20)
        right_panel.addWidget(GlowLabel("SPEED METER", 14, '#00ffff'))
        self.speed_meter = SpeedMeter()
        right_panel.addWidget(self.speed_meter, alignment=Qt.AlignCenter)
        
        right_panel.addSpacing(20)
        self.fever_label = GlowLabel("FEVER MODE!", 18, '#ffff00')
        self.fever_label.setAlignment(Qt.AlignCenter)
        self.fever_label.hide()
        right_panel.addWidget(self.fever_label)
        
        right_panel.addStretch()
        
        # Assemble layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(center_layout, 2)
        main_layout.addLayout(right_panel, 1)
        
        # Footer
        footer = QLabel("© 2025 MACAN ANGKASA")
        footer.setStyleSheet('''
            QLabel {
                color: #666;
                font-size: 10px;
                font-family: "Courier New", monospace;
            }
        ''')
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)

    def new_game(self):
        self.score = 0
        self.level = 1
        self.combo = 0
        self.lines_cleared = 0
        self.speed = 1000
        self.game_active = True
        self.board_widget.board = [[None for _ in range(10)] for _ in range(20)]
        self.board_widget.fever_mode = False
        self.fever_mode_active = False
        
        self.game_over_label.hide()
        self.restart_btn.hide()
        
        self.spawn_piece()
        self.update_ui()
        
        self.game_timer.start(self.speed)
        self.speed_timer.start(30000)  # Speed up every 30s
        
        self.play_move_sound()

    def spawn_piece(self):
        if hasattr(self, 'next_piece_type') and self.next_piece_type:
            piece_type = self.next_piece_type
        else:
            piece_type = random.choice(list(SHAPES.keys()))
        
        self.next_piece_type = random.choice(list(SHAPES.keys()))
        self.next_widget.next_piece = self.next_piece_type
        self.next_widget.next_shape = SHAPES[self.next_piece_type]
        self.next_widget.update()
        
        self.board_widget.current_piece = piece_type
        self.board_widget.current_shape = SHAPES[piece_type]
        self.board_widget.current_pos = [0, 4]
        
        if self.check_collision():
            self.game_over()

    def game_tick(self):
        if not self.game_active:
            return
        self.move_down()

    def move_down(self):
        self.board_widget.current_pos[0] += 1
        if self.check_collision():
            self.board_widget.current_pos[0] -= 1
            self.lock_piece()
            self.clear_lines()
            self.spawn_piece()
        self.board_widget.update()

    def move_left(self):
        self.board_widget.current_pos[1] -= 1
        if self.check_collision():
            self.board_widget.current_pos[1] += 1
        else:
            self.play_move_sound()
        self.board_widget.update()

    def move_right(self):
        self.board_widget.current_pos[1] += 1
        if self.check_collision():
            self.board_widget.current_pos[1] -= 1
        else:
            self.play_move_sound()
        self.board_widget.update()

    def rotate(self):
        shape = self.board_widget.current_shape
        rotated = [[shape[len(shape)-1-j][i] for j in range(len(shape))] 
                   for i in range(len(shape[0]))]
        old_shape = self.board_widget.current_shape
        self.board_widget.current_shape = rotated
        
        if self.check_collision():
            self.board_widget.current_shape = old_shape
        else:
            self.play_move_sound()
        self.board_widget.update()

    def fast_drop(self):
        while not self.check_collision():
            self.board_widget.current_pos[0] += 1
        self.board_widget.current_pos[0] -= 1
        self.lock_piece()
        self.clear_lines()
        self.spawn_piece()
        self.play_move_sound()

    def check_collision(self):
        cy, cx = self.board_widget.current_pos
        for y, row in enumerate(self.board_widget.current_shape):
            for x, val in enumerate(row):
                if val:
                    ny, nx = cy + y, cx + x
                    if ny < 0 or ny >= 20 or nx < 0 or nx >= 10:
                        return True
                    if ny >= 0 and self.board_widget.board[ny][nx]:
                        return True
        return False

    def lock_piece(self):
        cy, cx = self.board_widget.current_pos
        color = COLORS[self.board_widget.current_piece]
        for y, row in enumerate(self.board_widget.current_shape):
            for x, val in enumerate(row):
                if val:
                    ny, nx = cy + y, cx + x
                    if 0 <= ny < 20 and 0 <= nx < 10:
                        self.board_widget.board[ny][nx] = color

    def clear_lines(self):
        lines = [i for i in range(20) if all(self.board_widget.board[i])]
        if not lines:
            self.combo = 0
            self.update_ui()
            return
        
        # Flash animation
        self.board_widget.clearing_lines = lines
        anim = QPropertyAnimation(self.board_widget, b"flash_opacity")
        anim.setDuration(300)
        anim.setStartValue(100)
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        
        QTimer.singleShot(300, lambda: self.complete_clear(lines))

    def complete_clear(self, lines):
        for line in sorted(lines, reverse=True):
            del self.board_widget.board[line]
            self.board_widget.board.insert(0, [None] * 10)
        
        self.board_widget.clearing_lines = []
        self.lines_cleared += len(lines)
        self.combo += 1
        
        points = len(lines) * 100 * self.combo
        self.score += points
        self.level = self.lines_cleared // 10 + 1
        
        if len(lines) == 4:
            self.activate_fever_mode()
        
        self.play_line_clear_sound()
        self.update_ui()
        self.save_state()

    def activate_fever_mode(self):
        self.fever_mode_active = True
        self.board_widget.fever_mode = True
        self.fever_label.show()
        self.fever_timer.start(3000)
        self.play_arcade_fever_sound()

    def deactivate_fever(self):
        self.fever_mode_active = False
        self.board_widget.fever_mode = False
        self.fever_label.hide()
        self.fever_timer.stop()

    def increase_speed(self):
        if self.speed > 100:
            self.speed = max(100, int(self.speed * 0.85))
            self.game_timer.setInterval(self.speed)
            self.speed_meter.speed_level = min(20, self.speed_meter.speed_level + 1)
            self.speed_meter.update()

    def game_over(self):
        self.game_active = False
        self.game_timer.stop()
        self.speed_timer.stop()
        
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_label.setText(str(self.high_score))
        
        self.game_over_label.show()
        self.restart_btn.show()
        self.save_state()

    def update_ui(self):
        self.score_label.setText(str(self.score))
        self.level_label.setText(str(self.level))
        self.high_score_label.setText(str(self.high_score))
        self.combo_label.setText(f"x{self.combo}")

    def keyPressEvent(self, event):
        if not self.game_active:
            return
        
        if event.key() == Qt.Key_Left:
            self.move_left()
        elif event.key() == Qt.Key_Right:
            self.move_right()
        elif event.key() == Qt.Key_Down:
            self.move_down()
        elif event.key() == Qt.Key_Up:
            self.rotate()
        elif event.key() == Qt.Key_Space:
            self.fast_drop()

    def get_save_path(self):
        if sys.platform == 'win32':
            base = Path.home() / 'AppData' / 'Local'
        else:
            base = Path.home() / '.local' / 'share'
        
        save_dir = base / 'MacanTetrisNeoArcade'
        save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir / 'state.json'

    def save_state(self):
        data = {
            'high_score': self.high_score,
            'score': self.score,
            'level': self.level,
            'speed': self.speed,
            'combo': self.combo,
            'lines_cleared': self.lines_cleared,
            'board': [[str(c.name()) if c else None for c in row] 
                     for row in self.board_widget.board]
        }
        try:
            with open(self.get_save_path(), 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Save error: {e}")

    def load_state(self):
        try:
            path = self.get_save_path()
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)
                self.high_score = data.get('high_score', 0)
                self.high_score_label.setText(str(self.high_score))
        except Exception as e:
            print(f"Load error: {e}")

    # Dummy sound functions
    def play_line_clear_sound(self):
        print("[SOUND] Line clear!")

    def play_move_sound(self):
        print("[SOUND] Move piece")

    def play_arcade_fever_sound(self):
        print("[SOUND] FEVER MODE ACTIVATED!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MacanTetrisNeo()
    window.show()
    sys.exit(app.exec())