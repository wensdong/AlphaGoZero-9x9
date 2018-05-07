# AlphaGoZero-9x9
This is to create an adjustable sized board to explore the DeepMind Paper about AlphaGo Zero, because I do not have thoursands GPUs to play with.

The DeepMind's AlphaGo Zero idea is super simple:

1. Use MCTS to generate the training examples.
2. Use these examples to train a neural network.

Although there are existing github implementation such as Leela Zero, a great effort. However, the program has about 10,000 lines of codes, they are hard to read and the instruction is difficult to follow. I tried to make a smaller sized board from Leela Zero to play with with no luck.

Luckly there is another great concise implementation of other simple games, please refer to https://web.stanford.edu/~surag/posts/alphazero.html,
my repo was base on this implementation.

**To run training:**
```
git clone https://github.com/wensdong/AlphaGoZero-9x9.git
cd AlphaGoZero-9x9
python mainG.py
```
**To play(you need train first, to obtain a model):**
```
python pit.py
```
**Results:**

Please look at the results folder. I trained on AWS P2 for about 5 hours, the bot's winning rate is about 95% against the random or the greedy player.
