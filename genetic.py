class Genetic:


    def __init__(self,state):
        self.state = state
        self.height=self.height_count()
        self.kolone=self.column_heights()


    def bumpines(self):

        ret_val=0
        for k in range(len(self.kolone)):
            if (k!=9):
                ret_val+=abs(self.kolone[k]-self.kolone[k+1])
        return ret_val


    def height_count(self):
        for i in range(len(self.state)):
            for j in range(10):
                if self.state[i][j]==1:
                    return i

    def column_heights(self):
        kolone = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(10):
            for j in range(self.height, len(self.state)):
                if self.state[j][i] == 1:
                    kolone[i] = 20 - j
                    break
        return kolone


    def holes(self):
        holes=0
        for i in range(10):
            for j in range(len(self.state)-1,self.height-1,-1):
                if (self.state[j][i]==0):
                    for k in range(j,self.height-1,-1):
                        if self.state[k][i]==1:
                            holes+=1
                            break

        return holes


    def agg_height(self):

        ret_val = 0
        for k in self.kolone:
            ret_val += k
        return ret_val

    def complete_lines(self):
        ret_val=0
        for i in range(self.height,20):
            if all(x == 1 for x in self.state[i]):
                ret_val+=1

        return ret_val

    def heuristic(self):
        a = -0.510066
        b = 0.760666
        c = -0.35663
        d = -0.184483

        return a*self.agg_height() + b*self.complete_lines() + c*self.holes() + d*self.bumpines()

if __name__ == "__main__":
    stanje = [
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
              [0, 1, 1, 1, 1, 1, 1, 0, 0, 1],
              [0, 1, 1, 0, 1, 1, 1, 1, 1, 1],
              [1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
              [1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    gen = Genetic(stanje)
    print gen.height
    print gen.kolone
    print gen.bumpines()
    print gen.holes()
    print gen.agg_height()
    print gen.complete_lines()
    print gen.heuristic()