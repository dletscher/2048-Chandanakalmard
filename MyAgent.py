from Game2048 import *
import math

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
        moves = self.moveOrder(state)
        d = 1
        bestMove = None
        maxD=7 # this will prevent over runs
        while self.timeRemaining() and d<=maxD:
            self._depthCount += 1
            self._parentCount += 1
            self._nodeCount += 1
            bestVal = float('-inf')
            for m in moves:
                if not self.timeRemaining(): return
                nextState = state.move(m)
                if nextState._board==state._board: continue #Added this to avoid un-neccesary search
                val = self.minPlayer(nextState, d - 1)
                if val is None: return
                if val > bestVal:
                    bestVal = val
                    bestMove = m
            self.setMove(bestMove)
            d += 1

    def maxPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1
        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)
        best = float('-inf')
        for m in self.moveOrder(state):
            if not self.timeRemaining(): return
            nextState = state.move(m)
            if nextState._board == state._board: continue
            val = self.minPlayer(nextState, depth - 1)
            if val is None: return
            best = max(best, val)
        return best

    def minPlayer(self, state, depth):
        self._nodeCount += 1
        self._childCount += 1
        if state.gameOver():
            return state.getScore()
        if depth == 0:
            return self.heuristic(state)
        options = state.possibleTiles()
        total = 0
        for (pos, val) in options:#Added expected value 
            if not self.timeRemaining(): return
            nextState=state.addTile(pos, val)
            p=0.9 if val==1 else 0.1
            score = self.maxPlayer(nextState,depth - 1)
            if score is None: return
            total+=p*score
        return total/len(options) if options else self.heuristic(state)

    def heuristic(self, state):
        tiles=state._board
        currScore=state.getScore()
        empty=tiles.count(0)
        emptyBonus=math.log2(empty+1)*300
        maxTile=max(tiles)
        corners=[0,3,12,15]
        if any(tiles[i]==maxTile for i in corners):
            cornerBonus=5000
        else:
            cornerBonus=-3000
        weights=[
            262144,131072,65536,32768,
            2,4,8,16,
            32,64,128,256,
            512,1024,2048,4096
        ]
        snakeScore=sum((2**tiles[i])*weights[i] for i in range(16) if tiles[i]>0)
        snakeScore=snakeScore/(maxTile*500+1)
        def isSmooth(line):
            return all(x>=y for x,y in zip(line,line[1:])) or all(x<=y for x,y in zip(line,line[1:]))
        smoothScore=0
        for i in range(4):
            row=tiles[i*4:(i+1)*4]
            col=tiles[i::4]
            if isSmooth(row): smoothScore+=1200
            if isSmooth(col): smoothScore+=1200
        path=[0,1,2,3,7,6,5,4,8,9,10,11,15,14,13,12]
        penalty=sum(-3000 for i in range(16) if tiles[i]>=maxTile-2 and i not in path)
        return currScore+emptyBonus+cornerBonus+snakeScore+smoothScore+penalty

    def moveOrder(self, state):
        p={'D':0,'L':1,'U':2,'R':3}
        return sorted(state.actions(),key=lambda m: p.get(m,4))

    def stats(self):
        print(f'Average depth: {self._depthCount/self._count:.2f}')
        print(f'Branching: {self._childCount/self._parentCount:.2f}')
