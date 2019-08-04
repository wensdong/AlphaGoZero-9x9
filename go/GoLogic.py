
"""Author: Wen Dong (credit to Eric P. Nichols)
Date: 20/4/2018
Board class
Board data:
    1=white, -1=black, 0 =empty
    first dim is row, 2ndis columm:
Points are stored and manipulated as (x,y) tuple #####
"""
import numpy as np
import collections
from collections import deque


class Board():

    # list of all 4 directions on the board, as (x,y) offsets
    __directions = [(1,0),(0,-1),(-1,0),(0,1)]
    history = collections.deque(maxlen=8)  #keep a record of game history for color
    history_ = collections.deque(maxlen=8)
    board_his = collections.deque(maxlen=8)
    board_his_ = collections.deque(maxlen=8)


    def __init__(self, n):
        "Set up initial board configuration."

        self.n = n
        # Create the empty board array.
        self.bs = [None]*self.n
        for i in range(self.n):
            self.bs[i] = [0]*self.n

    # add [][] indexer syntax to the Board
    def __getitem__(self, index):
        return self.bs[index]

    def countDiff(self, color):
        """Counts the # bs of the given color
        (1 for white, -1 for black, 0 for empty spaces)"""
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==color:
                    count += 1
                if self[x][y]==-color:
                    count -= 1
        return count

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color. 1 for white, -1 for black.
        for an empty point, if it is _is_surrounded by opponent bs, then move is forbidden;
        if it connect to other its own bs, and the _connected bs is _is_surrounded by opponet bs,
        then the move is forbidden; However, if above 2 conditions cause opponent' bs to be killed,
        and not cause the board to become the state before your opponet's last move, then the move is legal.
        """
        moves = [] # stores the legal moves.
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==0:
                    if self._is_surrounded((x, y), color):
                        if self._is_kill((x,y), color) and not self._is_ko((x,y), color):
                            moves.append((x,y))
                        
                    else:
                        #if self._is_surrounded((x,y), color):
                        if not self._is_2eyes((x, y), color):
                            """must empty space and not suicide"""
                            moves.append((x,y))
                        
        return list(moves)

    def has_legal_moves(self, color):
        if len(self.get_legal_moves(color)) > 0:
            return True

    def execute_move(self, move, color):
        """Perform the given move on the board; remove opponet bs if kill (1=white,-1=black)
        """
        x, y= move
        if (x, y) in self.get_legal_moves(color):
            self[x][y] = color
            self.history.append((x, y))
            dead_pieces = self._perform_kill(move, color)
            if len(dead_pieces) > 0:
                self.history_.append(dead_pieces)
            else:
                self.history_.append(None)
            #add board state to deque
            self.board_his.append(np.copy(self.bs))

            return self.history, self.history_



    def _is_kill(self, point, color):
        """looking for -color bs in neighbor, other cases return None; test only,
        no move is made, so take off piece after placed"""
        u,v=point
        assert(self[u][v] ==0)
        dead_pieces = []
        self[u][v] = color
        for x, y in self._get_neighbors_(point, color):
            if self._is_surrounded((x, y), -color):
                for x, y in self._connected((x,y), -color):
                    dead_pieces.append((x,y))
        if len(dead_pieces) > 0:
            self[u][v] = 0
            return str(True), dead_pieces
        else:
            self[u][v] = 0
            return False


    def _perform_kill(self, point, color):
        """take out opponent's bs, if there is no qi; use with self.execute_move"""
        killed_pieces = []
        for x, y in self._get_neighbors_(point, color):
            if self._is_surrounded((x, y), -color):
                for x, y in self._connected((x,y), -color):
                    self[x][y]=0
                    killed_pieces.append((x, y))
        return killed_pieces

    def _get_neighbors(self, point, color):
        """from left, right, up and down four directions, get its own bs for a point"""
        x, y = point
        neighbors = []

        for direction in self.__directions:
            x, y =list(map(sum, zip(point, direction)))

            
            if all(list(map(lambda x: 0<= x < self.n, (x, y)))):
                if self[x][y] == color:
                    neighbors.append((x, y))
           
        return neighbors

    def _get_neighbors_any(self, point, color):
        """from left, right, up and down four directions, get neighbors for a point"""
        x, y = point
        neighbors = []

        for direction in self.__directions:
            x, y =list(map(sum, zip(point, direction)))
            if all(list(map(lambda x: 0<= x < self.n, (x, y)))):

                    neighbors.append((x, y))
        return neighbors

    def _get_neighbors_(self, point, color):
        """get neighbors of opposite color bs"""
        (x, y) = point
        neighbors_ = []

        for direction in self.__directions:
            x, y =list(map(sum, zip(point, direction)))
            if all(list(map(lambda x: 0<= x < self.n, (x, y)))):
                if self[x][y] == -color:
                    neighbors_.append((x, y))
        return neighbors_

    def _get_qi(self, point, color):
        """get liberties of a point"""
        qi = []
        (x, y) =point
        for direction in self.__directions:
            x, y =list(map(sum, zip(point, direction)))
            if all(list(map(lambda x: 0<= x < self.n, (x, y)))):
                if self[x][y] == 0:
                    qi.append((x, y))
        return qi


    def _connected(self, point, color):
        """return a point's _connected bs for its own color"""
        collection = []
        new_collection = []
        collection.append(point)
        new =self._get_neighbors(point, color)
        collection = collection + new
        new_new = []
        count = 0

        while  count < 10:       #solve indefinite loops for board size below 9x9
            for x, y in new:
                new_new = self._get_neighbors((x, y), color)
                for u, v in new_new:
                    if (u, v) not in collection:
                        collection.append((u, v))
                        new_collection.append((u, v))
            new=new_collection
            count +=1

        return collection


    def _find_eye(self, point, color):
        """for a group of _connected bs, if there are 2 empty point inside, then the group is live group"""
        conn = []
        nei = self._get_neighbors((point), color)

        conn_dict = {}

        if len(nei) > 1:
            conn = self._connected(point, color)
            if all((x, y) in conn for (x, y) in nei):
                nei_of_conn = [self._get_neighbors_any((x,y), color) for x, y in conn]
                nei_of_conn_flat = [item for sublist in nei_of_conn for item in sublist]
                nei_of_conn_dict = {k:nei_of_conn_flat.count(k) for k in nei_of_conn_flat}
                """find all points, which have 4 its own neighbors at inside board position, 3 at edge and 2 at corner"""
                inside_points = {k: v for k, v in nei_of_conn_dict.items() if v==4}
                edge_points = {(x,y): v for (x,y), v in nei_of_conn_dict.items() if v == 3 and ((x==self.n - 1 and not y== self.n-1) or (y == self.n -1 and not x == self.n-1) or (x ==0 and not y ==0) or (y ==0 and not x ==0))}

                corner_points = {(x,y): v for (x,y), v in nei_of_conn_dict.items() if v == 2 and ((x ==self.n-1 or x ==0) and (y == self.n-1 or y == 0))}

                ok_points = {**corner_points, **edge_points, **inside_points}
                """ covert dict to list for key only"""
                ok_points = [key for key, value in ok_points.items()]
                """filter one of 2 eyes"""
                eyes = [(x, y) for (x, y) in ok_points if self[x][y] == 0]

                if len(eyes) == 2 and point in eyes:

                    return [(x, y) for (x, y) in eyes if (x, y)!= point]

    def _is_2eyes(self, point, color):
        
        another_eye = self._find_eye(point, color) 
        if another_eye: 
            eye = self._find_eye(another_eye[0], color)
            if eye:
                if eye[0] == point:
                    return True

    def _is_oneEye(self, point, color):
        x,y = point
        if len(self._get_neighbors(point, color)) == 4:
            return True
        if len(self._get_neighbors(point, color)) == 3 and ((x==self.n - 1 and not y== self.n-1) or (y == self.n -1 and not x == self.n-1) or (x ==0 and not y ==0) or (y ==0 and not x ==0)):
            return True
        if len(self._get_neighbors(point, color)) == 2 and ((x ==self.n-1 or x ==0) and (y == self.n-1 or y == 0)):

            return True



    def _is_surrounded(self, point, color):
        """ one or a _connected group of own bs is surrounded ? """
        x, y = point
        if self[x][y] ==0:
            self[x][y] = color
            if all(len(self._get_qi((x,y), color)) == 0 for x, y in self._connected(point, color)):
                #if not all([self[x][y]==color for x, y in self._get_neighbors_any((x, y), color)]):
                self[x][y] = 0
                return True
            else:
                self[x][y] =0
                return False
        else:
            if all(len(self._get_qi((x,y), color)) == 0 for x, y in self._connected(point, color)):
                return True
            else:
                return False


    def _is_ko(self, point, color):
        """test whether the move is ko, which cause board status return to previous status,
        before your opponent's last move"""
        x, y = point
        assert(self[x][y] == 0)

        if self.history_ and self.history:
            if self.history_[-1] is not None:
                if self._is_kill((point), color):
                    _, dead_pieces = self._is_kill((point), color)
                    if len(dead_pieces) == 1:
                        if self.history_[-1][-1] == point and dead_pieces[0] == self.history[-1]:
                            return True
   


            
