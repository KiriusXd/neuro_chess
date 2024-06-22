import tensorflow as tf
import numpy as np
import random
import os
from logic import Board, Pawn, Knight, Bishop, Rook, Queen, King
from multiprocessing import Pool, cpu_count

# Построение модели
def build_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu', input_shape=(8, 8, 12)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(64, activation='softmax')  # Softmax для предсказания вероятности каждого возможного хода
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# Получение состояния доски
def get_board_state(board):
    state = np.zeros((8, 8, 12), dtype=int)
    piece_to_index = {
        'Pawn': 0, 'Knight': 1, 'Bishop': 2, 'Rook': 3, 'Queen': 4, 'King': 5
    }
    for x in range(8):
        for y in range(8):
            piece = board.board[x][y]
            if piece is not None:
                idx = piece_to_index[type(piece).__name__]
                if piece.color == 'black':
                    idx += 6
                state[x, y, idx] = 1
    return state

# Самообучение для одной пары моделей
def self_play_for_pair(pair_index, model1, model2, num_games=1000):
    train_X1 = []
    train_y1 = []
    train_X2 = []
    train_y2 = []

    for game in range(num_games):
        board = Board()
        current_models = [model1, model2]
        random.shuffle(current_models)  # Случайный выбор порядка игроков
        move_history = []

        while not board.is_checkmate(board.current_turn) and not board.is_stalemate(board.current_turn):
            player = board.current_turn
            model_idx = 0 if player == 'white' else 1
            state = get_board_state(board)
            move_probs = current_models[model_idx].predict(np.expand_dims(state, axis=0))[0]
            possible_moves = board.get_all_possible_moves()
            move_idx = np.argmax(move_probs[:len(possible_moves)])
            move = possible_moves[move_idx]
            board.move_piece(move[0], move[1])
            move_history.append((state, move))

        # Обработка результата игры
        if board.is_checkmate('white') or board.is_checkmate('black'):
            winner = 'black' if board.current_turn == 'white' else 'white'
            for state, move in move_history:
                if winner == 'white':
                    train_X1.append(state)
                    train_y1.append(move)
                else:
                    train_X2.append(state)
                    train_y2.append(move)
        elif board.is_stalemate('white') or board.is_stalemate('black'):
            # При пате никто не получает очков
            continue

    return train_X1, train_y1, train_X2, train_y2

# Обучение одной пары моделей
def train_pair(pair_index):
    model1 = build_model()
    model2 = build_model()
    train_X1, train_y1, train_X2, train_y2 = self_play_for_pair(pair_index, model1, model2, num_games=10)

    model1.fit(np.array(train_X1), np.array(train_y1), epochs=5, batch_size=32, validation_split=0.2)
    model2.fit(np.array(train_X2), np.array(train_y2), epochs=5, batch_size=32, validation_split=0.2)

    # Сохранение лучшей модели
    score1 = model1.evaluate(np.array(train_X1), np.array(train_y1), verbose=0)
    score2 = model2.evaluate(np.array(train_X2), np.array(train_y2), verbose=0)
    winner_model = model1 if score1[1] > score2[1] else model2

    model_path = os.path.join("models", f"model_pair_{pair_index}_winner.keras")
    winner_model.save(model_path)
    print(f"Сохранена лучшая модель пары {pair_index} в {model_path}")

# Обучение моделей с использованием нескольких ядер
def train_multiple_pairs(num_pairs):
    num_cores = cpu_count() // 2  # Используем половину доступных ядер
    if num_pairs>num_cores:
        print('Пар нейросетей больше чем ядер, их количество будет уменьшено')
        while num_pairs>num_cores:
            num_pairs=-1        
    with Pool(processes=num_cores) as pool:
        pool.map(train_pair, range(num_pairs))

# Определение наилучшей модели среди всех сохраненных
def find_best_model(models_dir='models'):
    model_files = [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.endswith('.keras')]
    best_model = None
    best_accuracy = 0

    for model_file in model_files:
        model = tf.keras.models.load_model(model_file)
        test_X, test_y = generate_test_data()
        score = model.evaluate(test_X, test_y, verbose=0)
        print(f'Model {model_file}: Accuracy - {score[1]}')
        if score[1] > best_accuracy:
            best_accuracy = score[1]
            best_model = model

    return best_model

# Генерация фиктивного тестового набора данных
def generate_test_data(num_samples=100):
    test_X = []
    test_y = []
    for _ in range(num_samples):
        board = Board()
        board.randomize()  # Допустим, у вас есть метод randomize, который случайным образом расставляет фигуры на доске
        state = get_board_state(board)
        possible_moves = board.get_all_possible_moves()
        move = random.choice(possible_moves)
        test_X.append(state)
        test_y.append(move)
    return np.array(test_X), np.array(test_y)

if __name__ == "__main__":
    train_multiple_pairs(num_pairs=3)
    best_model = find_best_model()
    os.makedirs('best_models', exist_ok=True)
    if best_model:
        best_model.save("best_models/best_model.keras")
        print("Лучшая модель сохранена в best_models/best_model.keras")
    else:
        print("Не удалось определить лучшую модель")
