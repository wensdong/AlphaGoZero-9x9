"""
3x3 Go — Human (White ○) vs Engine (Black ●)
Engine uses MCTS+NNet if ./temp/best.pth.tar exists, else Greedy fallback.

Run: conda run -n base python play_gui.py
"""
import sys, os, time
import numpy as np
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from go.GoGame import GoGame
from go.GoPlayers import GreedyGoPlayer
from utils import dotdict

# ── colours ──────────────────────────────────────────────────────────────────
BG       = '#C8A96E'
LINE     = '#5C3A1E'
BLACK_S  = '#1a1a1a'
BLACK_SH = '#4a4a4a'
WHITE_S  = '#f5f5f0'
WHITE_SH = '#ffffff'
HINT     = '#90EE90'
HOVER_W  = '#dddddd'
LABEL_FG = '#3a2010'
BTN_BG   = '#8B6340'
BTN_FG   = '#ffffff'

CELL   = 110
MARGIN = 80
RADIUS = 42

ENGINE_DELAY_MS = 400   # pause before engine moves (feels more natural)


def load_engine(game):
    """Return engine callable(board) -> action. Uses NNet if model exists."""
    model_path = os.path.join(os.path.dirname(__file__), 'temp', 'best.pth.tar')
    if os.path.exists(model_path):
        try:
            from go.pytorch.NNet import NNetWrapper as NNet
            from MCTS import MCTS
            nnet = NNet(game)
            nnet.load_checkpoint('./temp', 'best.pth.tar')
            args = dotdict({'numMCTSSims': 25, 'cpuct': 1.0})
            mcts = MCTS(game, nnet, args)
            print('[Engine] Loaded NNet + MCTS from temp/best.pth.tar')
            return lambda board: int(np.argmax(mcts.getActionProb(board, temp=0)))
        except Exception as e:
            print(f'[Engine] NNet load failed ({e}), using Greedy fallback')
    print('[Engine] Using GreedyGoPlayer')
    greedy = GreedyGoPlayer(game)
    return greedy.play


class GoGUI:
    # Engine = Black (player=1), Human = White (player=-1)
    ENGINE_PLAYER = 1
    HUMAN_PLAYER  = -1

    def __init__(self, n=3):
        self.n    = n
        self.game = GoGame(n)
        self.engine = load_engine(self.game)
        self._reset_state()

        # ── window ────────────────────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title(f'Go {n}×{n}  —  You: White ○  |  Engine: Black ●')
        self.root.configure(bg='#6B4423')
        self.root.resizable(False, False)

        size = MARGIN * 2 + CELL * (n - 1)
        outer = tk.Frame(self.root, bg='#6B4423', padx=12, pady=12)
        outer.pack()

        self.status_var = tk.StringVar()
        tk.Label(outer, textvariable=self.status_var,
                 font=('Helvetica', 15, 'bold'),
                 bg='#6B4423', fg='#F5DEB3', pady=6).pack()

        self.canvas = tk.Canvas(outer, width=size, height=size,
                                bg=BG, highlightthickness=3,
                                highlightbackground='#5C3A1E')
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self._click)
        self.canvas.bind('<Motion>',   self._hover)
        self.canvas.bind('<Leave>',    self._leave)

        self.score_var = tk.StringVar()
        tk.Label(outer, textvariable=self.score_var,
                 font=('Helvetica', 12),
                 bg='#6B4423', fg='#F5DEB3', pady=4).pack()

        bf = tk.Frame(outer, bg='#6B4423')
        bf.pack(pady=6)
        tk.Button(bf, text='Pass', font=('Helvetica', 12, 'bold'),
                  bg=BTN_BG, fg=BTN_FG, activebackground='#A0744A',
                  relief='flat', padx=14, pady=4,
                  command=self._human_pass).pack(side=tk.LEFT, padx=8)
        tk.Button(bf, text='New Game', font=('Helvetica', 12, 'bold'),
                  bg=BTN_BG, fg=BTN_FG, activebackground='#A0744A',
                  relief='flat', padx=14, pady=4,
                  command=self._new_game).pack(side=tk.LEFT, padx=8)

        self.hover = None
        self._draw()
        self._update_status()

        # Engine goes first (it's Black)
        self.root.after(ENGINE_DELAY_MS, self._engine_move)

    # ── state ─────────────────────────────────────────────────────────────────
    def _reset_state(self):
        self.board  = self.game.getInitBoard()
        self.player = 1       # Black (engine) always starts
        self.passes = 0
        self.over   = False
        self.hover  = None

    # ── coordinates ───────────────────────────────────────────────────────────
    def _to_px(self, row, col):
        return MARGIN + col * CELL, MARGIN + row * CELL

    def _from_px(self, px, py):
        col = round((px - MARGIN) / CELL)
        row = round((py - MARGIN) / CELL)
        if 0 <= row < self.n and 0 <= col < self.n:
            cx, cy = self._to_px(row, col)
            if abs(px - cx) < CELL * 0.45 and abs(py - cy) < CELL * 0.45:
                return row, col
        return None

    def _rc_to_action(self, row, col):
        return self.n * row + col

    # ── drawing ───────────────────────────────────────────────────────────────
    def _draw(self):
        c = self.canvas
        c.delete('all')
        n = self.n

        for i in range(n):
            x0, y0 = self._to_px(0, i);     x1, y1 = self._to_px(n-1, i)
            c.create_line(x0, y0, x1, y1, width=2, fill=LINE)
            x0, y0 = self._to_px(i, 0);     x1, y1 = self._to_px(i, n-1)
            c.create_line(x0, y0, x1, y1, width=2, fill=LINE)

        for i in range(n):
            x, y = self._to_px(0, i)
            c.create_text(x, y - MARGIN // 2, text=str(i),
                          font=('Helvetica', 11, 'bold'), fill=LABEL_FG)
            x, y = self._to_px(i, 0)
            c.create_text(x - MARGIN // 2, y, text=str(i),
                          font=('Helvetica', 11, 'bold'), fill=LABEL_FG)

        # valid-move hints (only when it's the human's turn)
        human_turn = (self.player == self.HUMAN_PLAYER) and not self.over
        if human_turn:
            valids = self.game.getValidMoves(self.board, self.player)
            for row in range(n):
                for col in range(n):
                    if valids[self._rc_to_action(row, col)]:
                        px, py = self._to_px(row, col)
                        r = RADIUS * 0.22
                        c.create_oval(px-r, py-r, px+r, py+r,
                                      fill=HINT, outline='')

            # ghost stone on hover
            if self.hover:
                row, col = self.hover
                if valids[self._rc_to_action(row, col)]:
                    px, py = self._to_px(row, col)
                    c.create_oval(px-RADIUS, py-RADIUS, px+RADIUS, py+RADIUS,
                                  fill=HOVER_W, outline='#888888', stipple='gray50')

        # stones
        for row in range(n):
            for col in range(n):
                val = self.board[row][col]
                if val == 0:
                    continue
                px, py = self._to_px(row, col)
                if val == 1:    # Black (engine)
                    c.create_oval(px-RADIUS, py-RADIUS, px+RADIUS, py+RADIUS,
                                  fill=BLACK_S, outline='#000000', width=2)
                    c.create_oval(px-RADIUS*.5, py-RADIUS*.55,
                                  px-RADIUS*.05, py-RADIUS*.15,
                                  fill=BLACK_SH, outline='')
                else:           # White (human, −1)
                    c.create_oval(px-RADIUS, py-RADIUS, px+RADIUS, py+RADIUS,
                                  fill=WHITE_S, outline='#999999', width=2)
                    c.create_oval(px-RADIUS*.45, py-RADIUS*.55,
                                  px-RADIUS*.05, py-RADIUS*.15,
                                  fill=WHITE_SH, outline='')

    def _update_status(self):
        if self.over:
            return
        if self.player == self.ENGINE_PLAYER:
            self.status_var.set('Engine thinking…  ●')
        else:
            self.status_var.set('Your turn  —  White ○')
        b = int(np.sum(self.board == 1))
        w = int(np.sum(self.board == -1))
        self.score_var.set(f'Engine ●  {b}     You ○  {w}')

    # ── engine ────────────────────────────────────────────────────────────────
    def _engine_move(self):
        if self.over or self.player != self.ENGINE_PLAYER:
            return
        # get canonical board (engine is always asked to play as player 1)
        canonical = self.game.getCanonicalForm(self.board, self.player)
        action = self.engine(canonical)
        self._apply_move(action, is_pass=(action == self.n * self.n))

    # ── human input ───────────────────────────────────────────────────────────
    def _hover(self, event):
        if self.player != self.HUMAN_PLAYER or self.over:
            return
        pos = self._from_px(event.x, event.y)
        if pos != self.hover:
            self.hover = pos
            self._draw()

    def _leave(self, event):
        if self.hover is not None:
            self.hover = None
            self._draw()

    def _click(self, event):
        if self.over or self.player != self.HUMAN_PLAYER:
            return
        pos = self._from_px(event.x, event.y)
        if pos is None:
            return
        row, col = pos
        action = self._rc_to_action(row, col)
        valids = self.game.getValidMoves(self.board, self.player)
        if not valids[action]:
            return
        self._apply_move(action, is_pass=False)

    def _human_pass(self):
        if self.over or self.player != self.HUMAN_PLAYER:
            return
        self._apply_move(self.n * self.n, is_pass=True)

    # ── shared move logic ─────────────────────────────────────────────────────
    def _apply_move(self, action, is_pass):
        if is_pass:
            self.passes += 1
        else:
            self.passes = 0

        self.board, self.player = self.game.getNextState(
            self.board, self.player, action)
        self.hover = None
        self._draw()

        if self.passes >= 2:
            self._end_game()
            return

        result = self.game.getGameEnded(self.board, self.player)
        if result != 0:
            self._end_game(result)
            return

        self._update_status()

        # schedule engine move if it's now the engine's turn
        if self.player == self.ENGINE_PLAYER and not self.over:
            self.root.after(ENGINE_DELAY_MS, self._engine_move)

    # ── game over ─────────────────────────────────────────────────────────────
    def _end_game(self, result=None):
        self.over = True
        b = int(np.sum(self.board == 1))
        w = int(np.sum(self.board == -1))

        if result is None or result == 0:
            if b > w:   winner = 'Engine (Black ●) wins!'
            elif w > b: winner = 'You (White ○) win!'
            else:       winner = "It's a draw!"
        elif result == 1:
            winner = ('Engine (Black ●) wins!'
                      if self.player == self.ENGINE_PLAYER
                      else 'You (White ○) win!')
        else:
            winner = ('You (White ○) win!'
                      if self.player == self.ENGINE_PLAYER
                      else 'Engine (Black ●) wins!')

        self.status_var.set(f'Game over  —  {winner}')
        self.score_var.set(f'Final  —  Engine ●  {b}     You ○  {w}')
        self._draw()
        messagebox.showinfo('Game Over', winner)

    def _new_game(self):
        self._reset_state()
        self.engine = load_engine(self.game)   # reload in case model trained
        self._draw()
        self._update_status()
        self.root.after(ENGINE_DELAY_MS, self._engine_move)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    GoGUI(n).run()
