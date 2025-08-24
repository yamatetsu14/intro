# othello.py
# シンプルなコンソール版オセロ（2人対戦用）

BOARD_SIZE = 8

def init_board():
    """初期盤面を作成"""
    board = [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    board[3][3] = board[4][4] = "O"
    board[3][4] = board[4][3] = "X"
    return board

def print_board(board):
    """盤面を表示"""
    print("  " + " ".join(str(i) for i in range(BOARD_SIZE)))
    for i, row in enumerate(board):
        print(str(i) + " " + " ".join(row))
    print()

def is_on_board(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def valid_moves(board, player):
    """有効な手をリストで返す"""
    opponent = "O" if player == "X" else "X"
    moves = []

    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] != ".":
                continue
            flips = []
            # 8方向チェック
            for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                nx, ny = x + dx, y + dy
                temp = []
                while is_on_board(nx, ny) and board[nx][ny] == opponent:
                    temp.append((nx, ny))
                    nx += dx
                    ny += dy
                if is_on_board(nx, ny) and board[nx][ny] == player and temp:
                    flips.extend(temp)
            if flips:
                moves.append((x, y))
    return moves

def make_move(board, x, y, player):
    """石を置いて盤面を更新"""
    opponent = "O" if player == "X" else "X"
    board[x][y] = player
    # 8方向の石を裏返す
    for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
        nx, ny = x + dx, y + dy
        flips = []
        while is_on_board(nx, ny) and board[nx][ny] == opponent:
            flips.append((nx, ny))
            nx += dx
            ny += dy
        if is_on_board(nx, ny) and board[nx][ny] == player:
            for fx, fy in flips:
                board[fx][fy] = player

def count_discs(board):
    """石の数を数える"""
    x_count = sum(row.count("X") for row in board)
    o_count = sum(row.count("O") for row in board)
    return x_count, o_count

def main():
    board = init_board()
    player = "X"

    while True:
        print_board(board)
        moves = valid_moves(board, player)

        if not moves:
            print(f"{player} の置ける場所がありません。パスします。")
            player = "O" if player == "X" else "X"
            if not valid_moves(board, player):
                break
            continue

        print(f"{player} の番です。有効な手: {moves}")
        x, y = map(int, input("置く位置を x y で入力してください: ").split())

        if (x, y) not in moves:
            print("無効な手です。もう一度入力してください。")
            continue

        make_move(board, x, y, player)
        player = "O" if player == "X" else "X"

    # ゲーム終了
    print_board(board)
    x_count, o_count = count_discs(board)
    print(f"X: {x_count}, O: {o_count}")
    if x_count > o_count:
        print("X の勝ち！")
    elif o_count > x_count:
        print("O の勝ち！")
    else:
        print("引き分け！")

if __name__ == "__main__":
    main()