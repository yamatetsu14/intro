# othello_ai_console.py
# コンソール版オセロ：人間(黒=X) vs AI(白=O)

import math
import copy

BOARD_SIZE = 8
HUMAN, AI = "X", "O"
EMPTY = "."

DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# 角重視の位置評価（簡易）
POS_WEIGHT = [
    [120,-20, 20,  5,  5, 20,-20,120],
    [-20,-40, -5, -5, -5, -5,-40,-20],
    [ 20, -5, 15,  3,  3, 15, -5, 20],
    [  5, -5,  3,  3,  3,  3, -5,  5],
    [  5, -5,  3,  3,  3,  3, -5,  5],
    [ 20, -5, 15,  3,  3, 15, -5, 20],
    [-20,-40, -5, -5, -5, -5,-40,-20],
    [120,-20, 20,  5,  5, 20,-20,120],
]

def init_board():
    b = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    b[3][3] = b[4][4] = "O"
    b[3][4] = b[4][3] = "X"
    return b

def in_bounds(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def print_board(board):
    print("   " + " ".join(str(j) for j in range(BOARD_SIZE)))
    for i in range(BOARD_SIZE):
        print(f"{i}  " + " ".join(board[i]))
    x_cnt, o_cnt = count_discs(board)
    print(f"X(黒): {x_cnt}  O(白): {o_cnt}\n")

def count_discs(board):
    x = sum(r.count("X") for r in board)
    o = sum(r.count("O") for r in board)
    return x, o

def valid_moves(board, player):
    opp = AI if player == HUMAN else HUMAN
    moves = []
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] != EMPTY:
                continue
            flips_any = False
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                seen = False
                while in_bounds(nx, ny) and board[nx][ny] == opp:
                    seen = True
                    nx += dx; ny += dy
                if seen and in_bounds(nx, ny) and board[nx][ny] == player:
                    flips_any = True
                    break
            if flips_any:
                moves.append((x, y))
    return moves

def make_move(board, x, y, player):
    """前提：合法手。裏返し適用した新盤面を返す"""
    opp = AI if player == HUMAN else HUMAN
    nb = copy.deepcopy(board)
    nb[x][y] = player
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        path = []
        while in_bounds(nx, ny) and nb[nx][ny] == opp:
            path.append((nx, ny))
            nx += dx; ny += dy
        if path and in_bounds(nx, ny) and nb[nx][ny] == player:
            for px, py in path:
                nb[px][py] = player
    return nb

def game_over(board):
    return not valid_moves(board, HUMAN) and not valid_moves(board, AI)

def evaluate(board, player_root=HUMAN):
    """位置重み + 石差 + モビリティ（簡易）"""
    score_pos = 0
    x_cnt, o_cnt = count_discs(board)
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == "X":
                score_pos += POS_WEIGHT[i][j]
            elif board[i][j] == "O":
                score_pos -= POS_WEIGHT[i][j]
    disc_diff = x_cnt - o_cnt
    mob_diff = len(valid_moves(board, HUMAN)) - len(valid_moves(board, AI))
    raw = 4*score_pos + 2*disc_diff + 8*mob_diff
    return raw if player_root == HUMAN else -raw

def minimax_max(board, me, opp, depth, alpha, beta, player_root):
    """me側：最大化ノード"""
    if depth == 0 or game_over(board):
        return evaluate(board, player_root), None
    mvs = valid_moves(board, me)
    if not mvs:
        # パスして相手番へ
        return minimax_min(board, me, opp, depth-1, alpha, beta, player_root)
    best = None
    for mv in sorted(mvs, key=lambda m: -POS_WEIGHT[m[0]][m[1]]):
        nb = make_move(board, mv[0], mv[1], me)
        sc, _ = minimax_min(nb, me, opp, depth-1, alpha, beta, player_root)
        if sc > alpha:
            alpha, best = sc, mv
        if alpha >= beta:
            break
    return alpha, best

def minimax_min(board, me, opp, depth, alpha, beta, player_root):
    """opp側：最小化ノード"""
    if depth == 0 or game_over(board):
        return evaluate(board, player_root), None
    mvs = valid_moves(board, opp)
    if not mvs:
        # 相手がパス→自分手番へ
        return minimax_max(board, me, opp, depth-1, alpha, beta, player_root)
    best = None
    for mv in sorted(mvs, key=lambda m: POS_WEIGHT[m[0]][m[1]]):
        nb = make_move(board, mv[0], mv[1], opp)
        sc, _ = minimax_max(nb, me, opp, depth-1, alpha, beta, player_root)
        if sc < beta:
            beta, best = sc, mv
        if alpha >= beta:
            break
    return beta, best

def ai_choice(board, depth=3):
    """AI(白=O)の手をミニマックスで選ぶ"""
    me, opp = AI, HUMAN
    score, mv = minimax_max(board, me, opp, depth, -math.inf, math.inf, player_root=HUMAN)
    if mv is None:
        mvs = valid_moves(board, me)
        if not mvs:
            return None
        # 位置重みで最良
        mv = max(mvs, key=lambda m: POS_WEIGHT[m[0]][m[1]])
    return mv

def main():
    board = init_board()
    turn = HUMAN  # 先手：人間（黒）
    depth = 3     # AIの読み深さ（2～4目安）

    print("=== コンソール版オセロ（人間: 黒X / AI: 白O）===\n")
    while True:
        print_board(board)

        if game_over(board):
            break

        moves = valid_moves(board, turn)
        if not moves:
            print(f"{turn} は置ける場所がありません（パス）。\n")
            turn = AI if turn == HUMAN else HUMAN
            continue

        if turn == HUMAN:
            print(f"あなたの番（X）。合法手: {moves}")
            try:
                s = input("行 列 を半角スペース区切りで入力（例: 2 3）: ").strip()
                x, y = map(int, s.split())
            except Exception:
                print("入力形式が無効です。例: 2 3\n")
                continue
            if (x, y) not in moves:
                print("その位置には置けません。合法手から選んでください。\n")
                continue
            board = make_move(board, x, y, HUMAN)
            turn = AI
        else:
            print("AIが思考中…")
            mv = ai_choice(board, depth=depth)
            if mv is None:
                print("AIはパス。\n")
                turn = HUMAN
            else:
                x, y = mv
                board = make_move(board, x, y, AI)
                print(f"AIの手: {(x, y)}\n")
                turn = HUMAN

    # ゲーム終了
    print_board(board)
    x_cnt, o_cnt = count_discs(board)
    if x_cnt > o_cnt:
        print("結果：あなたの勝ち！")
    elif o_cnt > x_cnt:
        print("結果：AIの勝ち。")
    else:
        print("結果：引き分け。")

if __name__ == "__main__":
    main()