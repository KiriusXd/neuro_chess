import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import logging
from logic import Board, Pawn, Knight, Bishop, Rook, Queen, King

logging.basicConfig(filename='chess_log.txt', level=logging.DEBUG, encoding='utf-8')

class StartWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Выбор стороны")
        
        self.label = tk.Label(root, text="Выберите действие:")
        self.label.pack()

        self.white_button = tk.Button(root, text="Играть за белых", command=self.start_game_white)
        self.white_button.pack(pady=10)

        self.black_button = tk.Button(root, text="Играть за черных", command=self.start_game_black)
        self.black_button.pack(pady=10)

        self.test_button = tk.Button(root, text="Тестирование", command=self.test_board)
        self.test_button.pack(pady=10)

    def start_game_white(self):
        self.root.destroy()
        root = tk.Tk()
        gui = ChessGUI(root, 'white')
        root.mainloop()

    def start_game_black(self):
        self.root.destroy()
        root = tk.Tk()
        gui = ChessGUI(root, 'black')
        root.mainloop()

    def test_board(self):
        self.root.destroy()
        root = tk.Tk()
        gui = ChessTest(root)
        root.mainloop()

class ChessTest:
    def __init__(self, root):
        self.root = root
        self.board = Board()
        self.load_images()
        self.create_widgets()
        self.selected_piece = None

    def load_images(self):
        self.images = {}
        piece_types = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
        colors = ['white', 'black']
        for color in colors:
            for piece in piece_types:
                self.images[f'{color}_{piece}'] = ImageTk.PhotoImage(
                    Image.open(f'img/chess/{color}_{piece}.png').resize((80, 80))
                )

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=640, height=640)
        self.canvas.pack()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                color = 'white' if (row + col) % 2 == 0 else 'gray'
                self.canvas.create_rectangle(col*80, row*80, (col+1)*80, (row+1)*80, fill=color)
                piece = self.board.board[row][col]
                if piece:
                    self.draw_piece(piece, col, row)

    def draw_piece(self, piece, x, y):
        piece_type = type(piece).__name__.lower()
        piece_color = piece.color
        self.canvas.create_image(x*80+40, y*80+40, image=self.images[f'{piece_color}_{piece_type}'])

    def on_click(self, event):
        x, y = event.x // 80, event.y // 80
        logging.debug(f"Нажатие на клетку ({x}, {y})")
        if self.selected_piece:
            try:
                self.board.move_piece(self.selected_piece, (y, x))
                self.selected_piece = None
                self.draw_board()
            except ValueError as e:
                self.selected_piece = None
                logging.error(str(e))
            self.draw_board()
        else:
            piece = self.board.board[x][y]
            if piece:
                self.selected_piece = (y, x)
                self.highlight_moves(y, x)

    def highlight_moves(self, x, y):
        piece = self.board.board[x][y]
        if piece:
            for mx, my in piece.get_possible_moves(self.board.board, x, y):
                self.canvas.create_rectangle(my*80, mx*80, (my+1)*80, (mx+1)*80, outline="red", width=3)

if __name__ == "__main__":
    root = tk.Tk()
    start_window = StartWindow(root)
    root.mainloop()

class ChessGUI:
    def __init__(self, root, side):
        self.root = root
        self.side = side
        self.board = Board()
        self.load_images()
        self.create_widgets()
        self.selected_piece = None

        self.debug_window = tk.Toplevel(root)
        self.debug_text = tk.Text(self.debug_window, height=20, width=80)
        self.debug_text.pack()

    def load_images(self):
        self.images = {}
        piece_types = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
        colors = ['white', 'black']
        for color in colors:
            for piece in piece_types:
                self.images[f'{color}_{piece}'] = ImageTk.PhotoImage(
                    Image.open(f'img/chess/{color}_{piece}.png').resize((80, 80))
                )

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=640, height=640)
        self.canvas.pack()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                color = 'white' if (row + col) % 2 == 0 else 'gray'
                self.canvas.create_rectangle(col*80, row*80, (col+1)*80, (row+1)*80, fill=color)
                piece = self.board.board[row][col]
                if piece:
                    self.draw_piece(piece, col, row)

    def draw_piece(self, piece, x, y):
        piece_type = type(piece).__name__.lower()
        piece_color = piece.color
        self.canvas.create_image(x*80+40, y*80+40, image=self.images[f'{piece_color}_{piece_type}'])

    def on_click(self, event):
        x, y = event.x // 80, event.y // 80
        logging.debug(f"Нажатие на клетку ({x}, {y})")
        if self.selected_piece:
            try:
                self.board.move_piece(self.selected_piece, (y, x))
                self.selected_piece = None
                if self.board.is_checkmate('black'):
                    messagebox.showinfo("Игра окончена", "Шах и мат! Белые победили!")
                    self.root.quit()
                elif self.board.is_stalemate('black'):
                    messagebox.showinfo("Игра окончена", "Пат! Ничья!")
                    self.root.quit()
                self.draw_board()
            except ValueError as e:
                self.selected_piece = None
                logging.error(str(e))
            self.draw_board()
        else:
            piece = self.board.board[x][y]
            if piece and piece.color == self.side:
                self.selected_piece = (y, x)
                self.highlight_moves(y, x)

    def highlight_moves(self, x, y):
        piece = self.board.board[x][y]
        if piece:
            for mx, my in piece.get_possible_moves(self.board.board, x, y):
                self.canvas.create_rectangle(my*80, mx*80, (my+1)*80, (mx+1)*80, outline="red", width=3)

    def log_debug(self, message):
        self.debug_text.insert(tk.END, message + "\n")
        self.debug_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    start_window = StartWindow(root)
    root.mainloop()
