# AlphaGoZero-9x9

If you do not have 5000 GPUs to play with, this is for you to explore the DeepMind Paper about AlphaGo Zero.

The DeepMind's AlphaGo Zero idea is super simple:

1. Use MCTS to generate the training examples.
2. Use these examples to train a neural network.

Although there are existing github implementations. However,they are either too complicated or too hard to follow. I tried to make a smaller sized board from Leela Zero to play with with no luck.

Luckly there is another great concise implementation of other simple games, please refer to https://web.stanford.edu/~surag/posts/alphazero.html,
my repo was base on this implementation.

**To run training:**
Install Pytorch, please refer to: https://pytorch.org/
```
git clone https://github.com/wensdong/AlphaGoZero-9x9.git
cd AlphaGoZero-9x9
python main.py
```
**To play(you need train first, to obtain a model):**
```
python pit.py
```
**Results:**

Start with training 3x3, takes a couple of minutes, you can have a bot with winning rate 99% againt a random player.
