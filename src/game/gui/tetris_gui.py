import pygame
from game.logic.vec2 import Vec2


class TetrisGUI:
    COLORS = {
        0: (20, 20, 20),  # Tło (ciemnoszary)
        1: (45, 45, 45),  # Niska 1: Prawie tło
        2: (40, 60, 80),  # Niska 2: Ciemny niebieski
        3: (30, 80, 80),  # Niska 3: Morski
        4: (30, 100, 40),  # Średnia 4: Ciemny zielony
        5: (100, 100, 30),  # Średnia 5: Ciemny żółty
        6: (130, 80, 20),  # Średnia 6: Mętny pomarańcz
        7: (200, 100, 20),  # Wysoka 7: Jasny pomarańcz
        8: (210, 30, 30),  # Wysoka 8: Czerwony
        9: (255, 215, 0),  # MAKSYMALNA 9: ZŁOTY/ŻÓŁTY
        "grid": (55, 55, 55),
        "ghost": (60, 60, 60)
    }

    @staticmethod
    def get_text_color(bg_color):
        """Zwraca czarny lub biały tekst w zależności od jasności tła."""
        # Wzór na luminancję W3C
        luminance = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]) / 255
        return (0, 0, 0) if luminance > 0.5 else (255, 255, 255)

    def __init__(self, grid, handler, cell_size: int = 35):
        self.grid = grid
        self.handler = handler
        self.cell_size = cell_size

        # UI Layout: Main Grid + Side Panel
        self.game_width = grid.get_shape().get_x() * cell_size
        self.ui_width = 200
        self.height = grid.get_shape().get_y() * cell_size

        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = None
        self.small_font = None

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.game_width + self.ui_width, self.height))
        pygame.display.set_caption("Tetris DQL")
        self.font = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.small_font = pygame.font.SysFont("Segoe UI", 18)

    def draw_cell(self, x, y, value, is_ghost=False):
        """Rysuje komórkę z wartością punktową w środku."""
        rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)

        if is_ghost:
            pygame.draw.rect(self.screen, self.COLORS["ghost"], rect, 2)
        else:
            abs_val = abs(value)

            block_color = self.COLORS.get(abs_val, (128, 128, 128))

            pygame.draw.rect(self.screen, block_color, rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

            if abs_val > 0:
                text_color = self.get_text_color(block_color)
                val_surf = self.small_font.render(str(abs_val), True, text_color)

                text_rect = val_surf.get_rect(center=rect.center)
                self.screen.blit(val_surf, text_rect)

    def draw_ghost_piece(self):
        """Oblicza i rysuje 'cień' klocka tam, gdzie wyląduje."""
        block = self.handler._TetrisHandler__player.get_block()
        if not block:
            return

        pos = self.handler._TetrisHandler__player_top_left
        ghost_y = pos.get_y()

        while not self.grid.is_gird_overlap(block, Vec2(pos.get_x(), ghost_y + 1)):
            ghost_y += 1

        shape = block.get_shape()
        for x in range(shape.get_x()):
            for y in range(shape.get_y()):
                val = block.get_value(x, y)
                if val != 0:
                    self.draw_cell(pos.get_x() + x, ghost_y + y, val, is_ghost=True)

    def draw_ui(self):
        """Rysuje panel boczny z punktami i informacjami."""
        panel_rect = pygame.Rect(self.game_width, 0, self.ui_width, self.height)
        pygame.draw.rect(self.screen, (30, 30, 30), panel_rect)
        pygame.draw.line(self.screen, (100, 100, 100), (self.game_width, 0), (self.game_width, self.height), 2)

        score_label = self.small_font.render("Total Score", True, (150, 150, 150))
        self.screen.blit(score_label, (self.game_width + 20, 30))

        score_val = self.font.render(str(self.handler.get_points()), True, (255, 255, 255))
        self.screen.blit(score_val, (self.game_width + 20, 55))

        average_score_label = self.small_font.render("Score per Block", True, (150, 150, 150))
        self.screen.blit(average_score_label, (self.game_width + 20, 100))

        average_score_val = self.font.render(f"{self.handler.get_points_divided_by_used_blocks():.2f}", True,
                                             (255, 255, 255))
        self.screen.blit(average_score_val, (self.game_width + 20, 125))

        controls = ["UP: Rotate", "LEFT/RIGHT: Move", "DOWN: Soft Drop"]
        for i, text in enumerate(controls):
            ctrl_surf = self.small_font.render(text, True, (100, 100, 100))
            self.screen.blit(ctrl_surf, (self.game_width + 33, self.height - 130 + (i * 20)))

    def draw_game(self):
        """Główna pętla renderująca."""
        self.screen.fill(self.COLORS[0])

        for x in range(self.grid.get_shape().get_x()):
            pygame.draw.line(self.screen, self.COLORS["grid"], (x * self.cell_size, 0),
                             (x * self.cell_size, self.height))
        for y in range(self.grid.get_shape().get_y()):
            pygame.draw.line(self.screen, self.COLORS["grid"], (0, y * self.cell_size),
                             (self.game_width, y * self.cell_size))

        self.draw_ghost_piece()

        full_grid = self.handler.get_draw_grid()
        shape = full_grid.get_shape()
        for y in range(shape.get_y()):
            for x in range(shape.get_x()):
                val = full_grid.get_value(x, y)
                if val != 0:
                    self.draw_cell(x, y, val)

        self.draw_ui()

    def run(self):
        self.init_pygame()

        DROP_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(DROP_EVENT, 500)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == DROP_EVENT:
                    self.handler.update()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.handler.try_move(is_right=False)
                    elif event.key == pygame.K_RIGHT:
                        self.handler.try_move(is_right=True)
                    elif event.key == pygame.K_UP:
                        self.handler.try_rotate(is_clockwise=True)
                    elif event.key == pygame.K_DOWN:
                        self.handler.update()

            if self.handler.is_game_over():
                self.running = False

            self.draw_game()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
