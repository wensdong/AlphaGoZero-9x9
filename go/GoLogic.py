
# coding: utf-8

# In[78]:

"""Author: Wen Dong (credit to Eric P. Nichols)
Date: 20/4/2018
Board class
Board data:
    1=white, -1=black, 0 =empty
    first dim is row, 2ndis columm:
Points are stored and manipulated as (x,y) tuple
"""

class Board():

    # list of all 4 directions on the board, as (x,y) offsets
    __directions = [(1,0),(0,-1),(-1,0),(0,1)]

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
        for an empty point, if it is surrounded by opponent pieces, then move is forbidden;
        if it connect to other its own pieces, and the connected pieces is surrounded by opponet pieces,
        then the move is forbidden; However, if above 2 conditions cause opponent' pieces to be killed,
        and not cause the board to become the state before your opponet's last move, then the move is legal.
        """

        moves = [] # stores the legal moves.

        # Get all the empty space
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==0:
                    if not self.surrounded((x, y), color):
                        moves.append((x,y))
                    elif self.surrounded((x,y), color):
                        if self.is_kill((x, y), color) and not self.returned_board((x, y), color):
                            moves.append((x,y))

        return list(moves)

    def has_legal_moves(self, color):
        if len(self.get_legal_moves(color)) > 0:
            return True

    def is_kill(self, point, color):
        """looking for -color pieces in neighbor, other cases return None; test only,
        no move is made, so take off piece after placed"""
        u,v=point
        true_list = []
        for x, y in self. get_neighbors_(point, color):
            self[u][v] = color
            if self.surrounded((x, y), -color):

                true_list.append((x,y))
                if len(true_list) > 0:
                    self[u][v] = 0
                    return True
                else:
                    return False


    def perform_kill(self, point, color):
        """take out opponent's pieces, if there is no qi; use with self.execute_move"""
        killed_pieces = []
        for x, y in self. get_neighbors_(point, color):
            if self.surrounded((x, y), -color):
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

        while  count < 10:       #solve indefinite loops
            for x, y in new:
                new_new = self.get_neighbors((x, y), color)
                for u, v in new_new:
                    if (u, v) not in collection:
                        collection.append((u, v))
                        new_collection.append((u, v))
            new=new_collection
            count +=1

        return collection


    def surrounded(self, point, color):
        """by opponent's pieces of one or a connected group of own pieces"""

        if all(len(self.get_qi((x,y), color)) == 0 for x, y in self.connected(point, color)):
            #if not all([self[x][y]==color for x, y in self.get_neighbors_any((x, y), color)]):
                return True
        else:
            return False



    def returned_board(self, point, color):
        """test whether the move is ko, which cause board status return to previous status,
        before your opponent's last move"""
        x, y = point
        self[x][y]= color
        ko = self.perform_kill(point, color)
        if len(ko) == 1:
            u,v = ko[0]

            if self.surrounded((u,v), -color):
                self[x][y] = color
                if self.is_kill((u,v), -color):
                    self[u][v] = - color
                    if self.perform_kill((u,v), -color) ==[point]:
                        self[x][y] = 0
                        self [u][v] = - color
                        return True


    def execute_move(self, move, color):
        """Perform the given move on the board; remove opponet pieces if kill (1=white,-1=black)
        """
        x, y= move
        self[x][y] = color
        if self.is_kill(move, color):
            self[x][y] = color
            self.perform_kill(move, color)



