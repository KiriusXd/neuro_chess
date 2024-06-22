class ChessGUI:
    def __init__(self, root):
        # ... ваш предыдущий код ...
        self.canvas.bind("<Button-1>", self.on_click)
        self.selected_piece = None

    def on_click(self, event):
        x, y = event.x // 50, event.y // 50
        if self.selected_piece:
            self.board.move_piece(self.selected_piece, (x, y))
            self.selected_piece = None
            self.draw_board()
        else:
            self.selected_piece = (x, y)

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                color = 'white' if (row + col) % 2 == 0 else 'gray'
                self.canvas.create_rectangle(col*50, row*50, (col+1)*50, (row+1)*50, fill=color)
                piece = self.board.board[row][col]
                if piece:
                    self.draw_piece(piece, col, row)

    def draw_piece(self, piece, x, y):
        # Логика отображения фигур на доске
        pass
