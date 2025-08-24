# othello_gui.py
# Tkinter GUI版オセロ（人間=黒X, AI=白O）

import tkinter as tk
from tkinter import messagebox
import copy, math, time

BOARD_SIZE = 8
CELL = 60
MARGIN = 20
STONE_R = 24

HUMAN, AI = "X", "O"
EMPTY = "."

BG_COLOR = "#2f4f4f"
GRID_COLOR = "#3d5f5f"
HINT_COLOR = "#7fffd4"   # 合法手の点
TEXT_COLOR = "white"

DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# 角重視の簡易位置評価
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

def in_bounds(x, y): return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def valid_moves(board, player):
    opp = AI if player == HUMAN else HUMAN
    moves = []
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] != EMPTY: continue
            ok = False
            for dx, dy in DIRECTIONS:
                nx, ny = x+dx, y+dy
                seen = False
                while in_bounds(nx, ny) and board[nx][ny] == opp:
                    seen = True; nx += dx; ny += dy
                if seen and in_bounds(nx, ny) and board[nx][ny] == player:
                    ok = True; break
            if ok: moves.append((x, y))
    return moves

def make_move(board, x, y, player):
    opp = AI if player == HUMAN else HUMAN
    nb = copy.deepcopy(board)
    nb[x][y] = player
    for dx, dy in DIRECTIONS:
        nx, ny = x+dx, y+dy
        path = []
        while in_bounds(nx, ny) and nb[nx][ny] == opp:
            path.append((nx, ny)); nx += dx; ny += dy
        if path and in_bounds(nx, ny) and nb[nx][ny] == player:
            for px, py in path: nb[px][py] = player
    return nb

def count_discs(board):
    x = sum(r.count("X") for r in board)
    o = sum(r.count("O") for r in board)
    return x, o

def game_over(board):
    return not valid_moves(board, HUMAN) and not valid_moves(board, AI)

def evaluate(board, root_player=HUMAN):
    # 位置重み + 石差 + モビリティ
    score_pos = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == "X": score_pos += POS_WEIGHT[i][j]
            elif board[i][j] == "O": score_pos -= POS_WEIGHT[i][j]
    x_cnt, o_cnt = count_discs(board)
    disc_diff = x_cnt - o_cnt
    mob_diff = len(valid_moves(board, HUMAN)) - len(valid_moves(board, AI))
    raw = 4*score_pos + 2*disc_diff + 8*mob_diff
    return raw if root_player == HUMAN else -raw

def minimax_max(board, me, opp, depth, alpha, beta, root_player):
    if depth == 0 or game_over(board): return evaluate(board, root_player), None
    mvs = valid_moves(board, me)
    if not mvs: return minimax_min(board, me, opp, depth-1, alpha, beta, root_player)
    best = None
    for mv in sorted(mvs, key=lambda m: -POS_WEIGHT[m[0]][m[1]]):
        nb = make_move(board, mv[0], mv[1], me)
        sc, _ = minimax_min(nb, me, opp, depth-1, alpha, beta, root_player)
        if sc > alpha: alpha, best = sc, mv
        if alpha >= beta: break
    return alpha, best

def minimax_min(board, me, opp, depth, alpha, beta, root_player):
    if depth == 0 or game_over(board): return evaluate(board, root_player), None
    mvs = valid_moves(board, opp)
    if not mvs: return minimax_max(board, me, opp, depth-1, alpha, beta, root_player)
    best = None
    for mv in sorted(mvs, key=lambda m: POS_WEIGHT[m[0]][m[1]]):
        nb = make_move(board, mv[0], mv[1], opp)
        sc, _ = minimax_max(nb, me, opp, depth-1, alpha, beta, root_player)
        if sc < beta: beta, best = sc, mv
        if alpha >= beta: break
    return beta, best

def ai_choice(board, depth=2):
    me, opp = AI, HUMAN
    score, mv = minimax_max(board, me, opp, depth, -math.inf, math.inf, root_player=HUMAN)
    if mv is None:
        mvs = valid_moves(board, me)
        if not mvs: return None
        mv = max(mvs, key=lambda m: POS_WEIGHT[m[0]][m[1]])
    return mv

class OthelloApp:
    def __init__(self, depth=2):
        self.depth = depth
        self.board = init_board()
        self.turn = HUMAN  # 先手：人間
        self.root = tk.Tk()
        self.root.title("Othello GUI - Human (Black) vs AI (White)")
        w = MARGIN*2 + CELL*BOARD_SIZE
        h = MARGIN*2 + CELL*BOARD_SIZE + 60
        self.canvas = tk.Canvas(self.root, width=w, height=h, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.status = tk.StringVar()
        self.status.set("あなたの番です（黒）")
        self.label = tk.Label(self.root, textvariable=self.status, fg=TEXT_COLOR, bg=BG_COLOR, font=("Helvetica", 13))
        self.label.place(x=MARGIN, y=MARGIN + CELL*BOARD_SIZE + 12)

        self.reset_btn = tk.Button(self.root, text="リセット", command=self.reset)
        self.reset_btn.place(x=w-90, y=MARGIN + CELL*BOARD_SIZE + 10)

        self.draw()
        self.root.after(200, self.maybe_pass_to_ai)

    def reset(self):
        self.board = init_board()
        self.turn = HUMAN
        self.status.set("あなたの番です（黒）")
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        x0, y0 = MARGIN, MARGIN
        # グリッド
        for i in range(BOARD_SIZE+1):
            self.canvas.create_line(x0 + i*CELL, y0, x0 + i*CELL, y0 + CELL*BOARD_SIZE, fill=GRID_COLOR)
            self.canvas.create_line(x0, y0 + i*CELL, x0 + CELL*BOARD_SIZE, y0 + i*CELL, fill=GRID_COLOR)
        # 合法手ハイライト
        for (i, j) in valid_moves(self.board, self.turn):
            cx = x0 + j*CELL + CELL//2
            cy = y0 + i*CELL + CELL//2
            self.canvas.create_oval(cx-6, cy-6, cx+6, cy+6, outline=HINT_COLOR, fill=HINT_COLOR)
        # 石
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                v = self.board[i][j]
                if v == EMPTY: continue
                cx = x0 + j*CELL + CELL//2
                cy = y0 + i*CELL + CELL//2
                fill = "black" if v == "X" else "white"
                outline = "white" if v == "X" else "black"
                self.canvas.create_oval(cx-STONE_R, cy-STONE_R, cx+STONE_R, cy+STONE_R,
                                        fill=fill, outline=outline, width=2)
        # スコア
        xb, ob = count_discs(self.board)
        self.canvas.create_text(MARGIN, 8, anchor="nw", fill=TEXT_COLOR,
                                text=f"黒(X): {xb}   白(O): {ob}", font=("Helvetica", 13, "bold"))

    def pos_from_xy(self, x, y):
        i = (y - MARGIN) // CELL
        j = (x - MARGIN) // CELL
        if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE: return int(i), int(j)
        return None

    def on_click(self, e):
        if self.turn != HUMAN or game_over(self.board): return
        pos = self.pos_from_xy(e.x, e.y)
        if not pos: return
        i, j = pos
        mvs = valid_moves(self.board, HUMAN)
        if (i, j) not in mvs:
            self.status.set("そこには置けません（点の位置をクリック）")
            return
        self.board = make_move(self.board, i, j, HUMAN)
        self.turn = AI
        self.draw()
        self.root.after(80, self.ai_step)

    def ai_step(self):
        if game_over(self.board): return self.finish()
        mvs = valid_moves(self.board, AI)
        if not mvs:
            self.status.set("AIは置けません（パス）。あなたの番です。")
            self.turn = HUMAN
            self.draw()
            if not valid_moves(self.board, HUMAN): self.finish()
            return
        self.status.set("AIが思考中…")
        self.root.update_idletasks()
        start = time.time()
        mv = ai_choice(self.board, depth=self.depth)
        took = time.time() - start
        if mv is None:
            self.status.set("AIの着手に失敗。あなたの番です。")
            self.turn = HUMAN
            return
        self.board = make_move(self.board, mv[0], mv[1], AI)
        self.status.set(f"AIの手: {mv}（{took:.2f}s） あなたの番です。")
        self.turn = HUMAN
        self.draw()
        if not valid_moves(self.board, HUMAN):
            if not valid_moves(self.board, AI): self.finish()
            else:
                self.status.set("あなたは置けません（パス）。AIの番です。")
                self.turn = AI
                self.root.after(200, self.ai_step)

    def maybe_pass_to_ai(self):
        if self.turn == HUMAN and not valid_moves(self.board, HUMAN):
            self.status.set("あなたは置けません（パス）。AIの番です。")
            self.turn = AI
            self.draw()
            self.root.after(200, self.ai_step)

    def finish(self):
        xb, ob = count_discs(self.board)
        self.draw()
        if xb > ob: msg = f"ゲーム終了：黒(X) {xb} - 白(O) {ob}\nあなたの勝ち！"
        elif ob > xb: msg = f"ゲーム終了：黒(X) {xb} - 白(O) {ob}\nAIの勝ち。"
        else: msg = f"ゲーム終了：黒(X) {xb} - 白(O) {ob}\n引き分け。"
        messagebox.showinfo("結果", msg)

    def run(self): self.root.mainloop()

if __name__ == "__main__":
    # depthは2〜4あたりが実用。上げると強いが時間がかかります。
    OthelloApp(depth=2).run()