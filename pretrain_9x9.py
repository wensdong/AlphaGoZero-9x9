"""
Pre-training for 9x9 Go (supervised learning / behavioural cloning).

WHY THIS EXISTS
---------------
An AlphaZero network starts with random weights.  On a 9x9 board that means
every action — including "pass" — gets roughly 1/82 probability.  The MCTS
almost never picks pass, so games run for 300+ moves (captures cycling back
and forth) instead of the expected 60-80.  That makes self-play training ~5x
slower than it should be.

This script fixes the cold-start by training the network on games played by a
simple rule-based heuristic BEFORE self-play begins.  After pre-training the
network understands:
  • captures are good
  • passing is a real option (games end)
  • what a winning / losing board looks like (value head)

Run: conda run -n base python pretrain_9x9.py
Then set load_model=True in main_9x9.py before running the full training.
"""

import numpy as np
import time
import os
from random import shuffle

from go.GoGame import GoGame
from go.GoLogic import Board
from go.pytorch.NNet import NNetWrapper as nn
from utils import dotdict

# ── configuration ────────────────────────────────────────────────────────────
N          = 9      # board size
NUM_GAMES  = 500    # games to generate; more → better pre-training, slower run
PASS_WHEN_FILL_RATIO = 0.65   # pass once this fraction of the board is filled
# ─────────────────────────────────────────────────────────────────────────────


# ── heuristic helpers ─────────────────────────────────────────────────────────

def _count_captures(b, x, y, color):
    """
    How many opponent stones would placing `color` at (x, y) capture?

    A group is captured when its last liberty is taken.  We check each
    opponent neighbour: if its only liberty is (x, y) it would be captured.

    We do this WITHOUT modifying the board — just by inspecting liberties.
    """
    captured = 0
    already_counted = set()   # avoid double-counting connected groups

    for nx, ny in b._neighbors(x, y):
        if b[nx][ny] == -color and (nx, ny) not in already_counted:
            liberties = b._liberties_of_group(nx, ny)
            if len(liberties) == 1 and liberties[0] == (x, y):
                # this whole group dies — count it once
                group = b._group(nx, ny)
                already_counted.update(group)
                captured += len(group)

    return captured


def heuristic_action(board_arr, color, n):
    """
    Simple one-ply heuristic for generating training games.

    Priority order:
      1. Pass if the board is >= PASS_WHEN_FILL_RATIO full.
         (teaches the network that games have an ending)
      2. Play the move that captures the most opponent stones.
         (teaches the network that captures are valuable)
      3. Otherwise pick a random legal move.
         (gives variety so we don't overfit to one style of play)
    """
    b = Board(n)
    b.bs = np.copy(board_arr)

    legal = b.get_legal_moves(color)

    # ── rule 1: pass when board is full enough ────────────────────────────
    filled = int(np.count_nonzero(board_arr))
    if not legal or filled / (n * n) >= PASS_WHEN_FILL_RATIO:
        return n * n   # pass action index = n²

    # ── rule 2: pick the best capturing move ─────────────────────────────
    best_action   = None
    best_captures = 0

    for x, y in legal:
        caps = _count_captures(b, x, y, color)
        if caps > best_captures:
            best_captures = caps
            best_action   = x * n + y

    if best_action is not None:
        return best_action

    # ── rule 3: random legal move ─────────────────────────────────────────
    x, y = legal[np.random.randint(len(legal))]
    return x * n + y


# ── game generation ───────────────────────────────────────────────────────────

def play_one_game(game):
    """
    Play a complete game between two heuristic players and return training
    examples of the form  (canonical_board, policy_vector, value).

    canonical_board  — board state from the perspective of the player to move
                       (GoGame.getCanonicalForm flips the sign for player -1)
    policy_vector    — one-hot over actions; 1.0 at the chosen move
    value            — +1.0 if that player eventually won, -1.0 if they lost
    """
    board  = game.getInitBoard()
    player = 1          # player 1 = white (1), player -1 = black (-1)
    examples           = []
    consecutive_passes = 0
    max_moves          = 2 * game.n * game.n   # safety cap — same as Coach

    for _ in range(max_moves):
        # canonical board: always shown from the current player's point of view
        canonical = game.getCanonicalForm(board, player)

        action = heuristic_action(board, player, game.n)

        # one-hot policy: we "supervised" the network to copy the heuristic
        pi = np.zeros(game.getActionSize(), dtype=np.float32)
        pi[action] = 1.0

        # store (canonical_board, who_moved, policy)  — value filled in later
        examples.append((canonical, player, pi))

        # track two consecutive passes → game over
        if action == game.n * game.n:
            consecutive_passes += 1
        else:
            consecutive_passes = 0

        board, player = game.getNextState(board, player, action)

        if consecutive_passes >= 2:
            break

    # ── score the finished game ───────────────────────────────────────────
    # countDiff(1) = (white stones) − (black stones); positive ⟹ white wins
    b = Board(game.n)
    b.bs = np.copy(board)
    score = b.countDiff(1)

    # assign +1 / -1 to every example depending on whether THAT player won
    result = []
    for canonical, p, pi in examples:
        # v is from player-1's perspective; multiply by p to flip for player -1
        v = 1.0 if score > 0 else -1.0
        result.append((canonical, pi, float(v * p)))

    return result


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    game = GoGame(N)
    nnet = nn(game)

    print(f'Pre-training on {N}x{N} Go')
    print(f'Generating {NUM_GAMES} heuristic games …\n')

    all_examples = []
    total_moves  = 0
    t0           = time.time()

    for i in range(NUM_GAMES):
        examples = play_one_game(game)
        all_examples.extend(examples)
        total_moves += len(examples)

        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            avg_len = total_moves / (i + 1)
            print(f'  {i+1:4d}/{NUM_GAMES} games | '
                  f'{len(all_examples):6d} examples | '
                  f'avg game length: {avg_len:.1f} moves | '
                  f'{elapsed:.0f}s elapsed')

    avg_len = total_moves / NUM_GAMES
    print(f'\nDone.  {len(all_examples)} training examples, '
          f'average game length {avg_len:.1f} moves')
    print(f'(compare: untrained self-play averages ~326 moves — '
          f'{326/avg_len:.1f}x improvement)\n')

    # shuffle before training so the network sees mixed positions per batch
    shuffle(all_examples)

    print('Training network on heuristic data …')
    nnet.train(all_examples)

    # save as the starting checkpoint for self-play
    os.makedirs('./temp_9x9', exist_ok=True)
    nnet.save_checkpoint('./temp_9x9', 'best.pth.tar')

    print('\nCheckpoint saved to ./temp_9x9/best.pth.tar')
    print('Next step: in main_9x9.py set  load_model=True  then run main_9x9.py')


if __name__ == '__main__':
    main()
