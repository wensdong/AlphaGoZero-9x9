"""test is_2eyes"""


print("####the following test 2 eyes####")
import numpy as np
import sys
sys.path.append('..')

from GoLogic import Board

b=Board(3)
b.bs=np.array([[-1,0,-1],[1,-1,0],[0,0,0]])
print("borad status\n",b.bs)

print("b.execute_move((0,1),1),print(borad status,b.bs)")
b.execute_move((0,1),1)
print("borad status\n",b.bs)

print("legal move for -1")

print(b.get_legal_moves(-1))





