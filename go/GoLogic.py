"""
Go board logic.
Board encoding: 1=white, -1=black, 0=empty
Points are (x, y) tuples, x=column, y=row (0-indexed).
"""
import numpy as np
from collections import deque


class Board:

    _DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def __init__(self, n):
        self.n = n
        self.bs = [[0] * n for _ in range(n)]
        # last_move[color] = point of the last single stone placed by that color
        # (used for ko detection)
        self._ko_point = None      # the single point that is forbidden this turn
        self._ko_color = None      # for which color it is forbidden

    # ------------------------------------------------------------------
    # indexing

    def __getitem__(self, index):
        return self.bs[index]

    # ------------------------------------------------------------------
    # public API

    def countDiff(self, color):
        """Return (# color stones) - (# opponent stones)."""
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y] == color:
                    count += 1
                elif self[x][y] == -color:
                    count -= 1
        return count

    def has_legal_moves(self, color):
        return len(self.get_legal_moves(color)) > 0

    def get_legal_moves(self, color):
        """Return list of legal (x, y) moves for color."""
        moves = []
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y] == 0 and self._is_legal(x, y, color):
                    moves.append((x, y))
        return moves

    def execute_move(self, move, color):
        """Place stone at move=(x,y) for color; capture dead opponent groups.
        Returns (history, history_) for compatibility with existing Coach/Arena code.
        Caller is responsible for only passing legal moves.
        """
        x, y = move
        self[x][y] = color

        # capture dead opponent groups
        captured = []
        for nx, ny in self._neighbors(x, y):
            if self[nx][ny] == -color and not self._has_liberty_group(nx, ny):
                captured.extend(self._remove_group(nx, ny))

        # update ko: if exactly one stone was captured and the placing stone
        # itself would now have exactly one liberty (which is the captured point),
        # then that captured point is ko-forbidden for the opponent next turn.
        if len(captured) == 1:
            cx, cy = captured[0]
            # the placed stone's group must have exactly one liberty = the captured point
            group_libs = self._liberties_of_group(x, y)
            if len(group_libs) == 1 and group_libs[0] == (cx, cy):
                self._ko_point = (cx, cy)
                self._ko_color = -color
            else:
                self._ko_point = None
                self._ko_color = None
        else:
            self._ko_point = None
            self._ko_color = None

        # return dummy history structures (Coach uses these only for bookkeeping)
        return None, None

    # ------------------------------------------------------------------
    # legality helpers

    def _is_legal(self, x, y, color):
        """True iff placing color at (x,y) is legal (empty, not suicide, not ko)."""
        # ko check
        if self._ko_point == (x, y) and self._ko_color == color:
            return False

        # temporarily place the stone
        self[x][y] = color

        # capture opponent groups that would die
        would_capture = []
        for nx, ny in self._neighbors(x, y):
            if self[nx][ny] == -color and not self._has_liberty_group(nx, ny):
                would_capture.extend(self._group(nx, ny))

        # suicide: after captures, does our group have any liberty?
        legal = self._has_liberty_group(x, y) or len(would_capture) > 0

        # undo
        self[x][y] = 0

        return legal

    # ------------------------------------------------------------------
    # group / liberty utilities

    def _neighbors(self, x, y):
        """Yield valid board neighbors of (x, y)."""
        for dx, dy in self._DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.n and 0 <= ny < self.n:
                yield nx, ny

    def _group(self, x, y):
        """Return list of all stones connected to (x,y) of the same color."""
        color = self[x][y]
        visited = set()
        queue = deque([(x, y)])
        visited.add((x, y))
        while queue:
            cx, cy = queue.popleft()
            for nx, ny in self._neighbors(cx, cy):
                if (nx, ny) not in visited and self[nx][ny] == color:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return list(visited)

    def _has_liberty_group(self, x, y):
        """True iff the group containing (x,y) has at least one liberty."""
        color = self[x][y]
        visited = set()
        queue = deque([(x, y)])
        visited.add((x, y))
        while queue:
            cx, cy = queue.popleft()
            for nx, ny in self._neighbors(cx, cy):
                if self[nx][ny] == 0:
                    return True
                if (nx, ny) not in visited and self[nx][ny] == color:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return False

    def _liberties_of_group(self, x, y):
        """Return list of liberty points of the group containing (x,y)."""
        color = self[x][y]
        visited_stones = set()
        liberties = set()
        queue = deque([(x, y)])
        visited_stones.add((x, y))
        while queue:
            cx, cy = queue.popleft()
            for nx, ny in self._neighbors(cx, cy):
                if self[nx][ny] == 0:
                    liberties.add((nx, ny))
                elif (nx, ny) not in visited_stones and self[nx][ny] == color:
                    visited_stones.add((nx, ny))
                    queue.append((nx, ny))
        return list(liberties)

    def _remove_group(self, x, y):
        """Remove all stones in the group at (x,y); return list of removed points."""
        stones = self._group(x, y)
        for sx, sy in stones:
            self[sx][sy] = 0
        return stones
