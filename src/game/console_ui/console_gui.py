from game.logic.tetris_handler import TetrisHandler
from pynput import keyboard
import queue
import time
import os


class TetrisConsoleGUI:
    FPS = 20
    FRAME_DELAY = 1 / FPS
    FRAMES_PER_UPDATE = 3

    def __init__(self):
        self.game = TetrisHandler()
        self.key_queue = queue.Queue()
        self.frames_counter = 0
        self.listener = keyboard.Listener(on_release=self.on_release)

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def on_release(self, key):
        if key == keyboard.Key.right:
            self.key_queue.put("move_right")
        elif key == keyboard.Key.left:
            self.key_queue.put("move_left")
        elif key == keyboard.KeyCode.from_char('z'):
            self.key_queue.put('rotate_ccw')
        elif key == keyboard.KeyCode.from_char('x'):
            self.key_queue.put('rotate_cw')

    def handle_input(self):
        while not self.key_queue.empty():
            key = self.key_queue.get()
            if key == "move_right":
                self.game.try_move(is_right=True)
            elif key == "move_left":
                self.game.try_move(is_right=False)
            elif key == 'rotate_ccw':
                self.game.try_rotate(is_clockwise=False)
            elif key == 'rotate_cw':
                self.game.try_rotate(is_clockwise=True)

    def run(self):
        self.listener.start()

        while True:
            self.clear()

            if not self.game.is_game_over():
                self.handle_input()
                print(self.game)

                if self.frames_counter == 0:
                    self.game.update()

                print()
                time.sleep(self.FRAME_DELAY)
                self.frames_counter = (self.frames_counter + 1) % self.FRAMES_PER_UPDATE
            else:
                print("=== GAME OVER ===")
                print(self.game)
                break

        self.listener.stop()

