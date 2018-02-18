import os.path
class State:


    def __init__(self):
        self.states=[]
        self.actions=[]



class Candidate:

    def __init__(self,height,lines,holes,bump,fit):

        self.heightWeight = height
        self.linesWeight = lines
        self.holesWeight = holes
        self.bumpinessWeight = bump
        self.fitness = fit

    def __str__(self):
        return "%f , %f , %f , %f, %f " % (self.heightWeight, self.linesWeight, self.holesWeight, self.bumpinessWeight, self.fitness)

if __name__=="__main__":
    s = Candidate(None,None,None,None,None)
    file = open("gen4.txt", "a")

    print naming_file(2)
