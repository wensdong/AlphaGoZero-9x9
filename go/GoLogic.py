
"""Author: Wen Dong (credit to Eric P. Nichols)
Date: 20/4/2018
Board class
Board data:
    1=white, -1=black, 0 =empty
    first dim is row, 2ndis columm:
Points are stored and manipulated as (x,y) tuple
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
        self.pieces = [None]*self.n
        for i in range(self.n):
            self.pieces[i] = [0]*self.n

    # add [][] indexer syntax to the Board
    def __getitem__(self, index):
        return self.pieces[index]

    def countDiff(self, color):
        """Counts the # pieces of the given color
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
        for an empty point, if it is is_surrounded by opponent pieces, then move is forbidden;
        if it connect to other its own pieces, and the connected pieces is is_surrounded by opponet pieces,
        then the move is forbidden; However, if above 2 conditions cause opponent' pieces to be killed,
        and not cause the board to become the state before your opponet's last move, then the move is legal.
        """
        moves = [] # stores the legal moves.
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==0:
                    if not self.is_surrounded((x, y), color):
                        if not self.is_2eyes((x, y), color):
                            """must empty space and not suicide"""
                            moves.append((x,y))
                    else:
                        if self.is_surrounded((x,y), color):
                            if self.is_kill((x,y), color) and not self.is_ko((x,y), color):
                                moves.append((x,y))
        return list(moves)

    def has_legal_moves(self, color):
        if len(self.get_legal_moves(color)) > 0:
            return True


    def is_kill(self, point, color):
        """looking for -color pieces in neighbor, other cases return None; test only,
        no move is made, so take off piece after placed"""
        u,v=point
        assert(self[u][v] ==0)
        dead_pieces = []
        self[u][v] = color
        for x, y in self.get_neighbors_(point, color):
            if self.is_surrounded((x, y), -color):
                for x, y in self.connected((x,y), -color):
                    dead_pieces.append((x,y))
        if len(dead_pieces) > 0:
            self[u][v] = 0
            return str(True), dead_pieces
        else:
            self[u][v] = 0
            return False


    def perform_kill(self, point, color):
        """take out opponent's pieces, if there is no qi; use with self.execute_move"""
        killed_pieces = []
        for x, y in self.get_neighbors_(point, color):
            if self.is_surrounded((x, y), -color):
                for x, y in self.connected((x,y), -color):
                    self[x][y]=0
                    killed_pieces.append((x, y))
        return killed_pieces

    def get_neighbors(self, point, color):
        """from left, right, up and down four directions, get its own pieces for a point"""
        x, y = point
        neighbors = []

        for direction in self.__directions:
            x, y =list(map(sum, zip(point, direction)))
            if all(list(map(lambda x: 0<= x < self.n, (x, y)))):
                if self[x][y] == color:
                    neighbors.append((x, y))
        return neighbors

    def get_neighbors_any(self, point, color):
        """from left, right, up and down four directions, get neighbors for a point"""
        x, y = point
        neighbors = []

        for direction in self.__directions:
            x, y =list(map(sum, zip(point, direction)))
            if all(list(map(lambda x: 0<= x < self.n, (x, y)))):

                    neighbors.append((x, y))
        return neighbors

    def get_neighbors_(self, point, color):
        """get neighbors of opposite color pieces"""
        (x, y) = point
        neighbors_ = []

        for direction in self.__directions:
            x, y =list(map(sum, zip(point, direction)))
            if all(list(map(lambda x: 0<= x < self.n, (x, y)))):
                if self[x][y] == -color:
                    neighbors_.append((x, y))
        return neighbors_

    def get_qi(self, point, color):
        """get liberties of a point"""
        qi = []
        (x, y) =point
        for direction in self.__directions:
            x, y =list(map(sum, zip(point, direction)))
            if all(list(map(lambda x: 0<= x < self.n, (x, y)))):
                if self[x][y] == 0:
                    qi.append((x, y))
        return qi


    def connected(self, point, color):
        """return a point's connected pieces for its own color"""
        collection = []
        new_collection = []
        collection.append(point)
        new =self.get_neighbors(point, color)
        collection = collection + new
        new_new = []
        count = 0

        while  count < 10:       #solve indefinite loops for board size below 9x9
            for x, y in new:
                new_new = self.get_neighbors((x, y), color)
                for u, v in new_new:
                    if (u, v) not in collection:
                        collection.append((u, v))
                        new_collection.append((u, v))
            new=new_collection
            count +=1

        return collection


    def is_2eyes(self, point, color):
        """for a group of connected pieces, if there are 2 empty point inside, then the group is live group"""
        conn = []
        nei = self.get_neighbors((point), color)

        conn_dict = {}

        if len(nei) > 1:
            conn = self.connected(nei[0], color)
            if all((x, y) in conn for (x, y) in nei):
                nei_of_conn = [self.get_neighbors_any((x,y), color) for x, y in conn]
                nei_of_conn_flat = [item for sublist in nei_of_conn for item in sublist]
                nei_of_conn_dict = {k:nei_of_conn_flat.count(k) for k in nei_of_conn_flat}
                """find all points, which have 4 its own neighbors at inside board position, 3 at edge and 2 at corner"""
                inside_points = {k: v for k, v in nei_of_conn_dict.items() if v==4}
                edge_points = {(x,y): v for (x,y), v in nei_of_conn_dict.items() if v == 3 and ((x==self.n - 1 and                             not y== self.n-1) or (y == self.n -1 and not x == self.n-1) or                             (x ==0 and not y ==0) or (y ==0 and not x ==0))}

                corner_points = {(x,y): v for (x,y), v in nei_of_conn_dict.items() if v == 2 and                                  ((x ==self.n-1 or x ==0) and (y == self.n-1 or y == 0))}

                ok_points = {**corner_points, **edge_points, **inside_points}
                """ covert dict to list for key only"""
                ok_points = [key for key, value in ok_points.items()]
                """filter one of 2 eyes"""
                eyes = [(x, y) for (x, y) in ok_points if self[x][y] == 0]

                if len(eyes) == 2 and point in eyes:
                    return True


    def is_surrounded(self, point, color):
        """ one or a connected group of own pieces is surrounded ? """
        x, y = point
        if self[x][y] ==0:
            self[x][y] = color
            if all(len(self.get_qi((x,y), color)) == 0 for x, y in self.connected(point, color)):
                #if not all([self[x][y]==color for x, y in self.get_neighbors_any((x, y), color)]):
                self[x][y] = 0
                return True
            else:
                self[x][y] =0
                return False
        else:
            if all(len(self.get_qi((x,y), color)) == 0 for x, y in self.connected(point, color)):
                return True
            else:
                return False


    def is_ko(self, point, color):
        """test whether the move is ko, which cause board status return to previous status,
        before your opponent's last move"""
        x, y = point
        assert(self[x][y] == 0)

        if self.history_ and self.history:
            if self.history_[-1] is not None:
                if self.is_kill((point), color):
                    _, dead_pieces = self.is_kill((point), color)
                    if len(dead_pieces) == 1:
                        if self.history_[-1][-1] == point and dead_pieces[0] == self.history[-1]:
                            return True
    def cycle(self, pint, color):
        board_his

    def execute_move(self, move, color):
        """Perform the given move on the board; remove opponet pieces if kill (1=white,-1=black)
        """
        x, y= move
        if (x, y) in self.get_legal_moves(color):
            self[x][y] = color
            self.history.append((x, y))
            dead_pieces = self.perform_kill(move, color)
            if len(dead_pieces) > 0:
                self.history_.append(dead_pieces)
            else:
                self.history_.append(None)
            #add board state to deque
            self.board_his.append(self.pieces)

            return self.history, self.history_


            
