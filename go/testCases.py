
# In[79]:


"""test returned_board"""
import numpy as np
b=Board(3)

b[0][0] =1
b[2][1] =1
b[1][2] = -1
b[0][1]=-1
b[1][0]=0
b[1][1]=1
bs=np.copy(b.pieces)
print(bs)
print(b.returned_board((0,2),1))
"""
x, y = (0,2)
b[x][y]= 1
ko = b.perform_kill((x,y), 1)
print(ko)
if len(ko) == 1:
    u,v = ko[0]
    print(u)

    if b.surrounded((u,v), -1):
        print(" pass one")
        b[x][y]= 1
        if b.is_kill((u,v), -1):

            print(" pass the two")
            b[u][v] = - 1
            if b.perform_kill((u,v), -1) == [(0,2)]:
                b[x][y] = 0
                b[u][v] = - 1
                print("True")

#print(b.get_legal_moves(1))
#print(b.returned_board((0,2),1))

b=Board(5)

b[0][0] =1
b[2][1] =1
b[1][2] = 1
b[0][1]=1
b[1][0]=0
b[1][1]=-1
b[1][3] =1
b[1][4]=1

bs=np.copy(b.pieces)
print(bs)
print(b.get_legal_moves(1))
print(b.surrounded((0,2), -1))
print(b.connected((1,1),1))
"""


# In[80]:

""" test key functions"""

import numpy as np
b=Board(3)

b[0][0] =1
b[2][1] =1
b[1][2] = -1
b[0][1]=-1
b[1][0]=0
b[1][1]=1
b[1][0]=1
b[0][2]=-1
#b[0][3]=1
#b[1][3]=1
bs=np.copy(b.pieces)
print(bs)

print(b.surrounded((0,2), 1))

print(b.get_qi((0,2),1))

#print(b.get_legal_moves(1))

print(b.get_qi((1,1),1))
print("following is surrounded")
print(b.surrounded((1,1),1))
print(b.is_kill((1,2),1))
b[1][2]=1
print(b.perform_kill((1,2),1))


# In[ ]:
