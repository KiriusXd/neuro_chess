import pygame
import logging
from logic import Board, Pawn, Knight, Bishop, Rook, Queen, King

logging.basicConfig(filename='chess_log.txt', level=logging.DEBUG, encoding='utf-8')

# Константы
WIDTH, HEIGHT = 640, 640
SQUARE_SIZE = WIDTH // 8

# Загрузка изображений
def load_images():
    images = {}
    piece_types = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
    colors = ['white', 'black']
    for color in colors:
        for piece in piece_types:
            images[f'{color}_{piece}'] = pygame.transform.scale(
                pygame.image.load(f'img/chess/{color}_{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE)
            )
    return images

class ChessGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Шахматы")
        self.clock = pygame.time.Clock()
        self.images = load_images()
        self.board = Board()
        self.selected_piece = None

    def draw_board(self):
        colors = [pygame.Color('white'), pygame.Color('gray')]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                piece = self.board.board[row][col]
                if piece:
                    self.draw_piece(piece, col, row)

    def draw_piece(self, piece, x, y):
        piece_type = type(piece).__name__.lower()
        piece_color = piece.color
        self.screen.blit(self.images[f'{piece_color}_{piece_type}'], (x*SQUARE_SIZE, y*SQUARE_SIZE))

    def highlight_moves(self, piece, x, y):
        for mx, my in piece.get_possible_moves(self.board.board, y, x):
            pygame.draw.rect(self.screen, pygame.Color('red'), (my*SQUARE_SIZE, mx*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

    def main_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                    logging.debug(f"Нажатие на клетку ({x}, {y})")
                    if self.selected_piece:
                        try:
                            self.board.move_piece(self.selected_piece, (y, x))
                            self.selected_piece = None
                            if self.board.is_checkmate('black'):
                                logging.info("Шах и мат! Белые победили!")
                                running = False
                            elif self.board.is_stalemate('black'):
                                logging.info("Пат! Ничья!")
                                running = False
                        except ValueError as e:
                            self.selected_piece = None
                            logging.error(str(e))
                    else:
                        piece = self.board.board[y][x]
                        if piece and piece.color == 'white':  # Или другой цвет в зависимости от выбранной стороны
                            self.selected_piece = (y, x)
            self.draw_board()
            if self.selected_piece:
                piece = self.board.board[self.selected_piece[0]][self.selected_piece[1]]
                self.highlight_moves(piece, self.selected_piece[1], self.selected_piece[0])
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = ChessGame()
    game.main_loop()
