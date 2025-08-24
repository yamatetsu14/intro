# othello_gui_ai.py
# Tkinterで作るAI対戦オセロ（リバーシ）
# 人間(黒=X) vs AI(白=O)

import tkinter as tk
from tkinter import messagebox
import copy
import math
import time

BOARD_SIZE = 8
CELL = 64            # マスのピクセル
MARGIN = 20          # 余白
STONE_R = 24         # 石の半径
BG = "#2f4f4f"
GRID = "#3d5f5f"
HINT = "#7fffd4"     # 合法手ハイライト
HUMAN, AI = "X", "O"

DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# 盤面の位置評価（角=高、辺=中、隅の隣=低）
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
    b = [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    b[3][3] = b[4][4] = "O"
    b[3][4] = b[4][3] = "X"
    return b

def on_board(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def valid_moves(board, player):
    opp = "O" if player == "X" else "X"
    moves = []
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] != ".":
                continue
            flips_any = False
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                seen = False
                while on_board(nx, ny) and board[nx][ny] == opp:
                    seen = True
                    nx += dx; ny += dy
                if seen and on_board(nx, ny) and board[nx][ny] == player:
                    flips_any = True
                    break
            if flips_any:
                moves.append((x, y))
    return moves

def make_move(board, x, y, player):
    """置ける前提で呼ぶ。裏返しを適用し盤面を返す"""
    opp = "O" if player == "X" else "X"
    nb = copy.deepcopy(board)
    nb[x][y] = player
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        path = []
        while on_board(nx, ny) and nb[nx][ny] == opp:
            path.append((nx, ny))
            nx += dx; ny += dy
        if path and on_board(nx, ny) and nb[nx][ny] == player:
            for px, py in path:
                nb[px][py] = player
    return nb

def count_discs(board):
    x = sum(r.count("X") for r in board)
    o = sum(r.count("O") for r in board)
    return x, o

def game_over(board):
    return not valid_moves(board, "X") and not valid_moves(board, "O")

def evaluate(board, player):
    """簡易評価：位置重み + 石差 + モビリティ"""
    opp = "O" if player == "X" else "X"
    score_pos = 0
    x_cnt, o_cnt = 0, 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == "X":
                score_pos += POS_WEIGHT[i][j]
                x_cnt += 1
            elif board[i][j] == "O":
                score_pos -= POS_WEIGHT[i][j]
                o_cnt += 1
    # 石差（黒正とする。playerが白なら符号反転する）
    disc_diff = (x_cnt - o_cnt)
    # モビリティ（合法手の数差）
    mob = len(valid_moves(board, "X")) - len(valid_moves(board, "O"))

    raw = 4*score_pos + 2*disc_diff + 8*mob
    return raw if player == "X" else -raw

def minimax(board, player, depth=3, alpha=-math.inf, beta=math.inf):
    """αβ枝刈りミニマックス。player視点の最大化"""
    if depth == 0 or game_over(board):
        return evaluate(board, player), None

    me = player
    opp = "O" if me == "X" else "X"
    moves = valid_moves(board, me)
    if not moves:
        # パスして相手の手番へ
        score, _ = minimax(board, opp, depth-1, alpha, beta)
        return score, None

    best_move = None
    for mv in sorted(moves, key=lambda m: -POS_WEIGHT[m[0]][m[1]]):
        nb = make_move(board, mv[0], mv[1], me)
        # 相手番の評価は反転して返ってくるように、相手を最大化させて自分は最小化
        score, _ = minimax_opponent(nb, opp, depth-1, alpha, beta, player_root=player)
        if score > alpha:
            alpha = score
            best_move = mv
        if alpha >= beta:
            break
    return alpha, best_move

def minimax_opponent(board, player, depth, alpha, beta, player_root):
    """相手側のノード（最小化側）"""
    if depth == 0 or game_over(board):
        return evaluate(board, player_root), None

    me = player
    opp = "O" if me == "X" else "X"
    moves = valid_moves(board, me)
    if not moves:
        score, _ = minimax(board, opp, depth-1, alpha, beta)  # 相手がパス→自分手番へ
        return score, None

    best_move = None
    for mv in sorted(moves, key=lambda m: POS_WEIGHT[m[0]][m[1]]):
        nb = make_move(board, mv[0], mv[1], me)
        score, _ = minimax(nb, opp, depth-1, alpha, beta)
        if score < beta:
            beta = score
            best_move = mv
        if alpha >= beta:
            break
    return beta, best_move

class OthelloGUI:
    def __init__(self, depth=3):
        self.depth = depth
        self.board = init_board()
        self.turn = HUMAN  # 先手：人間（黒）
        self.root = tk.Tk()
        self.root.title("Othello - Human (Black) vs AI (White)")
        w = MARGIN*2 + CELL*BOARD_SIZE
        h = MARGIN*2 + CELL*BOARD_SIZE + 60
        self.canvas = tk.Canvas(self.root, width=w, height=h, bg=BG, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.status = tk.StringVar()
        self.status.set("あなたの番です（黒）")
        self.label = tk.Label(self.root, textvariable=self.status, fg="white", bg=BG, font=("Helvetica", 14))
        self.label.place(x=MARGIN, y=MARGIN + CELL*BOARD_SIZE + 10)

        self.btn = tk.Button(self.root, text="リセット", command=self.reset)
        self.btn.place(x=w-90, y=MARGIN + CELL*BOARD_SIZE + 10)
        self.draw()

        # 人間が置けなければ即AIに回す
        self.root.after(200, self.maybe_pass_to_ai)

    def reset(self):
        self.board = init_board()
        self.turn = HUMAN
        self.status.set("あなたの番です（黒）")
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        # 盤
        x0 = MARGIN
        y0 = MARGIN
        for i in range(BOARD_SIZE+1):
            # 縦線
            self.canvas.create_line(x0 + i*CELL, y0, x0 + i*CELL, y0 + CELL*BOARD_SIZE, fill=GRID)
            # 横線
            self.canvas.create_line(x0, y0 + i*CELL, x0 + CELL*BOARD_SIZE, y0 + i*CELL, fill=GRID)

        # ハイライト（合法手）
        for (i, j) in valid_moves(self.board, self.turn):
            cx = x0 + j*CELL + CELL//2
            cy = y0 + i*CELL + CELL//2
            self.canvas.create_oval(cx-6, cy-6, cx+6, cy+6, outline=HINT, fill=HINT)

        # 石
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == ".":
                    continue
                cx = x0 + j*CELL + CELL//2
                cy = y0 + i*CELL + CELL//2
                color = "black" if self.board[i][j] == "X" else "white"
                outline = "white" if color == "black" else "black"
                self.canvas.create_oval(cx-STONE_R, cy-STONE_R, cx+STONE_R, cy+STONE_R,
                                        fill=color, outline=outline, width=2)

        # スコア
        xb, ob = count_discs(self.board)
        self.canvas.create_text(MARGIN, 8, anchor="nw", fill="white",
                                text=f"黒(X): {xb}   白(O): {ob}", font=("Helvetica", 13, "bold"))

    def pos_from_xy(self, x, y):
        ix = (y - MARGIN) // CELL
        iy = (x - MARGIN) // CELL
        if 0 <= ix < BOARD_SIZE and 0 <= iy < BOARD_SIZE:
            return int(ix), int(iy)
        return None

    def on_click(self, event):
        if self.turn != HUMAN or game_over(self.board):
            return
        p = self.pos_from_xy(event.x, event.y)
        if not p:
            return
        x, y = p
        moves = valid_moves(self.board, HUMAN)
        if (x, y) not in moves:
            self.status.set("そこには置けません。ハイライト箇所を選んでください。")
            return
        self.board = make_move(self.board, x, y, HUMAN)
        self.turn = AI
        self.draw()
        self.root.after(100, self.ai_move_step)

    def ai_move_step(self):
        if game_over(self.board):
            self.finish()
            return
        # AIが置けるか
        if not valid_moves(self.board, AI):
            # パス
            self.status.set("AIはパス。あなたの番です。")
            self.turn = HUMAN
            self.draw()
            if not valid_moves(self.board, HUMAN):
                self.finish()
            return

        self.status.set("AIが考えています…")
        self.root.update_idletasks()
        start = time.time()
        depth = self.depth
        # 終盤は深く読む
        empty = sum(r.count(".") for r in self.board)
        if empty <= 14:
            depth = min(5, depth+1)
        score, mv = minimax(self.board, AI, depth=depth)
        # 念のためフォールバック
        if mv is None:
            mvs = valid_moves(self.board, AI)
            mv = max(mvs, key=lambda m: POS_WEIGHT[m[0]][m[1]])
        self.board = make_move(self.board, mv[0], mv[1], AI)
        took = time.time() - start
        self.status.set(f"AIの手：{mv}（{took:.2f}s） あなたの番です。")
        self.turn = HUMAN
        self.draw()
        if not valid_moves(self.board, HUMAN):
            # 人間が置けなければAI続行
            if not valid_moves(self.board, AI):
                self.finish()
            else:
                self.status.set("あなたはパス。AIの番です。")
                self.turn = AI
                self.root.after(200, self.ai_move_step)

    def maybe_pass_to_ai(self):
        if self.turn == HUMAN and not valid_moves(self.board, HUMAN):
            self.status.set("あなたは置ける場所がありません。AIの番です。")
            self.turn = AI
            self.draw()
            self.root.after(200, self.ai_move_step)

    def finish(self):
        xb, ob = count_discs(self.board)
        self.draw()
        if xb > ob:
            msg = f"ゲーム終了：黒(X) {xb} - 白(O) {ob}\nあなたの勝ち！"
        elif ob > xb:
            msg = f"ゲーム終了：黒(X) {xb} - 白(O) {ob}\nAIの勝ち。"
        else:
            msg = f"ゲーム終了：黒(X) {xb} - 白(O) {ob}\n引き分け。"
        messagebox.showinfo("結果", msg)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # 深さは2～4程度が目安。数値を上げると強くなるが思考時間が延びます。
    app = OthelloGUI(depth=3)
    app.run()