import pygame
import random

CELL_SIZE = 40
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (169, 169, 169)
RED = (255, 0, 0)
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.revealed = False
        self.flagged = False
        self.adjacent_mines = 0

    def draw(self, screen):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if self.revealed:
            pygame.draw.rect(screen, WHITE, rect)
            if self.is_mine:
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 4)
            elif self.adjacent_mines > 0:
                font = pygame.font.SysFont(None, 24)
                text = font.render(str(self.adjacent_mines), True, BLACK)
                screen.blit(text, text.get_rect(center=rect.center))
        else:
            pygame.draw.rect(screen, GREY, rect)
            if self.flagged:
                pygame.draw.line(screen, BLACK, rect.topleft, rect.bottomright, 2)
                pygame.draw.line(screen, BLACK, rect.bottomleft, rect.topright, 2)
        pygame.draw.rect(screen, BLACK, rect, 2)

class Board:
    def __init__(self, grid_size, num_mines, game):
        self.grid_size = grid_size
        self.num_mines = num_mines
        self.board = [[Cell(x, y) for y in range(grid_size)] for x in range(grid_size)]
        self.mines_generated = False
        self.game = game  # Odkaz na hru

    def generate_mines(self, first_x, first_y):
        mines_placed = 0
        safe_zone = {(first_x + dx, first_y + dy) for dx in range(-2, 2) for dy in range(-1, 2)}
        while mines_placed < self.num_mines:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            if (x, y) not in safe_zone and not self.board[x][y].is_mine:
                self.board[x][y].is_mine = True
                mines_placed += 1
        self.calculate_adjacent_mines()

    def calculate_adjacent_mines(self):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if self.board[x][y].is_mine:
                    continue
                self.board[x][y].adjacent_mines = sum(
                    self.board[nx][ny].is_mine
                    for dx in range(-1, 2)
                    for dy in range(-1, 2)
                    if 0 <= (nx := x + dx) < self.grid_size and 0 <= (ny := y + dy) < self.grid_size
                )

    def reveal_cell(self, x, y):
        if not self.mines_generated:
            self.generate_mines(x, y)
            self.mines_generated = True
        if self.board[x][y].revealed or self.board[x][y].flagged:
            return
        if self.board[x][y].is_mine:
            self.game.lost = True  # Prohra
            return
        self.flood_fill(x, y)

    def flood_fill(self, x, y):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if not (0 <= cx < self.grid_size and 0 <= cy < self.grid_size):
                continue
            cell = self.board[cx][cy]
            if cell.revealed or cell.flagged:
                continue
            cell.revealed = True
            if cell.adjacent_mines == 0 and not cell.is_mine:
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        stack.append((cx + dx, cy + dy))

    def toggle_flag(self, x, y):
        if not self.board[x][y].revealed:
            self.board[x][y].flagged = not self.board[x][y].flagged

    def is_victory(self):
        return all(cell.revealed or cell.is_mine for row in self.board for cell in row)

    def draw(self, screen):
        for row in self.board:
            for cell in row:
                cell.draw(screen)

class MineSweeperGame:
    def __init__(self, grid_size=10, num_mines=10):
        self.grid_size = max(5, grid_size)

        max_mines = (self.grid_size * self.grid_size) // 2
        self.num_mines = min(num_mines, max_mines)

        self.width = self.grid_size * CELL_SIZE
        self.height = self.grid_size * CELL_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.lost = False
        self.victory = False
        self.board = Board(self.grid_size, self.num_mines, self)
        self.running = True


    def run(self):
        while self.running:
            self.handle_events()
            if self.lost:
                self.running = False
            elif self.board.is_victory():
                self.victory = True
                self.running = False
            self.draw_screen()
            self.clock.tick(30)
        self.show_end_message()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                x //= CELL_SIZE
                y //= CELL_SIZE
                if event.button == 1:
                    self.board.reveal_cell(x, y)
                elif event.button == 3:
                    self.board.toggle_flag(x, y)

    def draw_screen(self):
        self.screen.fill(BLACK)
        self.board.draw(self.screen)
        pygame.display.flip()

    def show_end_message(self):
        font = pygame.font.SysFont(None, 50)
        message = "Vyhrál jsi!" if self.victory else "Prohrál jsi!"
        text = font.render(message, True, WHITE)
        self.screen.fill(BLACK)
        self.screen.blit(text, text.get_rect(center=(self.width // 2, self.height // 2)))
        pygame.display.flip()
        pygame.time.delay(3000)
