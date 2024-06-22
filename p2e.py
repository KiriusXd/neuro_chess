class Bot:
    def __init__(self, color):
        self.color = color

    def get_best_move(self, board):
        # Реализация алгоритма Minimax
        pass

class ChessGUI:
    def __init__(self, root):
        # ... ваш предыдущий код ...
        self.bot = Bot("black")

    def on_click(self, event):
        x, y = event.x // 50, event.y // 50
        if self.selected_piece:
            self.board.move_piece(self.selected_piece, (x, y))
            self.selected_piece = None
            self.draw_board()
            self.bot_move()
        else:
            self.selected_piece = (x, y)

    def bot_move(self):
        move = self.bot.get_best_move(self.board)
        self.board.move_piece(move[0], move[1])
        self.draw_board()
