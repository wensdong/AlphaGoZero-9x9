# AlphaGoZero-9x9
This is to create an adjustable sized board to explore DeepMind Paper about AlphaGo Zero, so that normal people can play with the algorithm.

The DeepMind's AlphaGo Zero idea is super simple:

1. Use MCTS to generate the training examples.
2. Use these examples to train a neural network.

However, the existing github implementation is too complicated, e.g. Leela Zero is about 10,000 lines of codes, they are hard to read and the instruction is difficult to follow. I was trying to make a smaller sized board from Leela Zero to play with it with no luck.
