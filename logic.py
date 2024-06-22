import numpy as np
import random
class Piece:
    def __init__(self, color):
        self.color = color

    def get_possible_moves(self, board, x, y):
        raise NotImplementedError("Этот метод должен быть переопределен подклассами")

class Pawn(Piece):
    def get_possible_moves(self, board, x, y):
        moves = []
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1
        if 0 <= x + direction < 8 and board[x + direction][y] is None:
            moves.append((x + direction, y))
            if x == start_row and 0 <= x + 2 * direction < 8 and board[x + 2 * direction][y] is None:
                moves.append((x + 2 * direction, y))
        if 0 <= x + direction < 8:
            if y > 0 and board[x + direction][y - 1] is not None and board[x + direction][y - 1].color != self.color:
                moves.append((x + direction, y - 1))
            if y < 7 and board[x + direction][y + 1] is not None and board[x + direction][y + 1].color != self.color:
                moves.append((x + direction, y + 1))
        return moves

class Knight(Piece):
    def get_possible_moves(self, board, x, y):
        moves = []
        potential_moves = [
            (x + 2, y + 1), (x + 2, y - 1), (x - 2, y + 1), (x - 2, y - 1),
            (x + 1, y + 2), (x + 1, y - 2), (x - 1, y + 2), (x - 1, y - 2)
        ]
        for mx, my in potential_moves:
            if 0 <= mx < 8 and 0 <= my < 8 and (board[mx][my] is None or board[mx][my].color != self.color):
                moves.append((mx, my))
        return moves

class Bishop(Piece):
    def get_possible_moves(self, board, x, y):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in directions:
            mx, my = x + dx, y + dy
            while 0 <= mx < 8 and 0 <= my < 8:
                if board[mx][my] is None:
                    moves.append((mx, my))
                elif board[mx][my].color != self.color:
                    moves.append((mx, my))
                    break
                else:
                    break
                mx += dx
                my += dy
        return moves

class Rook(Piece):
    def get_possible_moves(self, board, x, y):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            mx, my = x + dx, y + dy
            while 0 <= mx < 8 and 0 <= my < 8:
                if board[mx][my] is None:
                    moves.append((mx, my))
                elif board[mx][my].color != self.color:
                    moves.append((mx, my))
                    break
                else:
                    break
                mx += dx
                my += dy
        return moves

class Queen(Piece):
    def get_possible_moves(self, board, x, y):
        return Bishop(self.color).get_possible_moves(board, x, y) + Rook(self.color).get_possible_moves(board, x, y)

class King(Piece):
    def get_possible_moves(self, board, x, y):
        moves = []
        potential_moves = [
            (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
            (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)
        ]
        for mx, my in potential_moves:
            if 0 <= mx < 8 and 0 <= my < 8 and (board[mx][my] is None or board[mx][my].color != self.color):
                moves.append((mx, my))
        return moves


class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
        self.current_turn = 'white'

    def setup_board(self):
        # Установка пешек
        for i in range(8):
            self.board[1][i] = Pawn('black')
            self.board[6][i] = Pawn('white')

        # Установка ладей
        self.board[0][0] = Rook('black')
        self.board[0][7] = Rook('black')
        self.board[7][0] = Rook('white')
        self.board[7][7] = Rook('white')

        # Установка коней
        self.board[0][1] = Knight('black')
        self.board[0][6] = Knight('black')
        self.board[7][1] = Knight('white')
        self.board[7][6] = Knight('white')

        # Установка слонов
        self.board[0][2] = Bishop('black')
        self.board[0][5] = Bishop('black')
        self.board[7][2] = Bishop('white')
        self.board[7][5] = Bishop('white')

        # Установка королев и королей
        self.board[0][3] = Queen('black')
        self.board[0][4] = King('black')
        self.board[7][3] = Queen('white')
        self.board[7][4] = King('white')

    def move_piece(self, start_pos, end_pos):
        x1, y1 = start_pos
        x2, y2 = end_pos
        piece = self.board[x1][y1]
        if piece and end_pos in piece.get_possible_moves(self.board, x1, y1):
            self.board[x2][y2] = piece
            self.board[x1][y1] = None
            self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        else:
            raise ValueError("Invalid move")

    def is_in_check(self, color):
        king_pos = self.find_king(color)
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    if king_pos in piece.get_possible_moves(self.board, row, col):
                        return True
        return False

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for move in piece.get_possible_moves(self.board, row, col):
                        original_piece = self.board[move[0]][move[1]]
                        self.board[move[0]][move[1]] = piece
                        self.board[row][col] = None
                        if not self.is_in_check(color):
                            self.board[move[0]][move[1]] = original_piece
                            self.board[row][col] = piece
                            return False
                        self.board[move[0]][move[1]] = original_piece
                        self.board[row][col] = piece
        return True

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for move in piece.get_possible_moves(self.board, row, col):
                        original_piece = self.board[move[0]][move[1]]
                        self.board[move[0]][move[1]] = piece
                        self.board[row][col] = None
                        if not self.is_in_check(color):
                            self.board[move[0]][move[1]] = original_piece
                            self.board[row][col] = piece
                            return False
                        self.board[move[0]][move[1]] = original_piece
                        self.board[row][col] = piece
        return True

    def get_all_possible_moves(self):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == self.current_turn:
                    piece_moves = piece.get_possible_moves(self.board, row, col)
                    for move in piece_moves:
                        moves.append(((row, col), move))
        return moves

    def randomize(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]  # Очистка инициализации доски

        piece_types = [Pawn, Knight, Bishop, Rook, Queen, King]
        starting_rows = {'white': 0, 'black': 7}

        # Расстановка пешек
        for file in range(8):
            self.board[starting_rows['white'] + 1][file] = Pawn('white')
            self.board[starting_rows['black'] - 1][file] = Pawn('black')

        # Расстановка остальных фигур
        random.shuffle(piece_types)
        for color in ['white', 'black']:
            row = starting_rows[color]
            for piece_type in piece_types:
                column = random.randint(0, 7)
                while self.board[row][column] is not None:
                    column = random.randint(0, 7)
                self.board[row][column] = piece_type(color)



