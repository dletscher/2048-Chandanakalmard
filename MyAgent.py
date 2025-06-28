from Game2048 import *

class Player(BasePlayer):
    def __init__(self, timeLimit):
        BasePlayer.__init__(self, timeLimit)
        self._nodeCount = 0
        self._parentCount = 0
        self._childCount = 0
        self._depthCount = 0
        self._count = 0

    def findMove(self, state):
        self._count += 1
        actions = self.moveOrder(state)
        if not actions:
            return
        depth = 1
        while self.timeRemaining():
            self._depthCount += 1
            self._parentCount += 1
            self._nodeCount += 1
            best = -float('inf')
            bestMove = actions[0]

            for a in actions:
                result = state.move(a)
                if not self.timeRemaining(): return
                v = self.expectiPlayer(result, depth - 1)
                if v is None: return
                if v > best:
                    best = v
                    bestMove = a

            self.setMove(bestMove)
            depth += 1

    def maxPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1

        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)

        actions = self.moveOrder(state)
        if not actions:
            return self.heuristic(state)

        self._parentCount += 1
        best = -float('inf')
        for a in actions:
            if not self.timeRemaining(): return None
            result = state.move(a)
            v = self.expectiPlayer(result, depth - 1)
            if v is None: return None
            if v > best:
                best = v
        return best

    def expectiPlayer(self,state,depth):
        self._nodeCount+=1
        self._childCount+=1

        if state.gameOver():
            return state.getScore()
        if depth==0:
            return self.heuristic(state)

        self._parentCount+=1
        total=0
        possibilities=state.possibleTiles()
        if not possibilities:
            return self.heuristic(state)

        for (tile,val) in possibilities:
            if not self.timeRemaining(): return None
            next_state=state.addTile(tile, val)
            result=self.maxPlayer(next_state, depth - 1)
            if result is None:
                return None
            total+=result

        return total/len(possibilities)

    def heuristic(self, state):
        board=[[state.getTile(r, c) for c in range(4)] for r in range(4)]
        tiles=[tile for row in board for tile in row]
        empty=tiles.count(0)
        max_tile=max(tiles)

        weight=[
            [32768,16384,8192,4096],
            [256,128,64,32],
            [16,8,4,2],
            [1,1,1,1]
        ]

        corner_score=sum(board[r][c]*weight[r][c] for r in range(4) for c in range(4))
        empty_score=empty*3000
        def is_monotonic(line):
            return all(i>=j for i,j in zip(line, line[1:]))or all(i<=j for i,j in zip(line, line[1:]))

        m=0
        for row in board:
            m+=is_monotonic(row)
        for col in zip(*board):
            m+=is_monotonic(col)
        m*=15000

       
        s=0
        for r in range(4):
            for c in range(3):
                s-=abs(board[r][c]-board[r][c+1])
        for c in range(4):
            for r in range(3):
                s-=abs(board[r][c]-board[r+1][c])
        s*=30

       
        merges=0
        for r in range(4):
            for c in range(3):
                if board[r][c] and board[r][c] == board[r][c+1]:
                    merges+=1
        for c in range(4):
            for r in range(3):
                if board[r][c] and board[r][c] == board[r+1][c]:
                    merges+=1
        merges*=25000
        return corner_score+empty_score+m+s+merges

    def moveOrder(self, state):
        c=['U','L','R','D']  
        a=state.actions()
        return [move for move in c if move in a]

    def stats(self):
        print(f'Average depth: {self._depthCount / self._count:.2f}')
        print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
