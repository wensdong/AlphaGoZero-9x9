"""
9x9 Go — AlphaZero training
Run: conda run -n base python main_9x9.py

RECOMMENDED WORKFLOW
--------------------
1. conda run -n base python pretrain_9x9.py
       Generates 500 heuristic games, trains the network, saves
       ./temp_9x9/best.pth.tar.  Takes ~5-10 min on GPU.
       Average game length drops from ~326 → ~70 moves.

2. Set load_model=True below, then run this file for the full training.
"""
import time
from Coach import Coach
from go.GoGame import GoGame
from go.pytorch.NNet import NNetWrapper as nn
from utils import dotdict

args = dotdict({
    # ── training scale ────────────────────────────────────────────────────
    # Validation run  →  numIters=1,  numEps=10,  arenaCompare=10
    # Full training   →  numIters=30, numEps=100, arenaCompare=20
    'numIters':                     1,
    'numEps':                       10,
    'arenaCompare':                 10,

    # ── MCTS ──────────────────────────────────────────────────────────────
    'numMCTSSims':                  25,   # simulations per move
    'cpuct':                        1,    # exploration constant
    'tempThreshold':                20,   # moves before temperature drops to 0

    # ── learning ──────────────────────────────────────────────────────────
    'updateThreshold':              0.55, # new model must win >55% to be accepted
    'maxlenOfQueue':                500000,
    'numItersForTrainExamplesHistory': 20,

    # ── checkpoints ───────────────────────────────────────────────────────
    'checkpoint':                   './temp_9x9/',
    # Set load_model=True after running pretrain_9x9.py
    'load_model':                   False,
    'load_folder_file':             ('./temp_9x9/', 'best.pth.tar'),
})

if __name__ == '__main__':
    t0 = time.time()
    print(f'Board: 9x9  |  numMCTSSims: {args.numMCTSSims}  |  numEps: {args.numEps}  |  numIters: {args.numIters}')
    print('This is a validation run (1 iter, 10 eps). Timing will extrapolate to full run.')

    g = GoGame(9)
    nnet = nn(g)

    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

    c = Coach(g, nnet, args)
    c.learn()

    elapsed = time.time() - t0
    print(f'\nValidation run complete in {elapsed/60:.1f} min')
    print(f'Extrapolated full run (30 iters, 100 eps): ~{elapsed * 30 * 10 / 60:.0f} min  ({elapsed * 30 * 10 / 3600:.1f} h)')
