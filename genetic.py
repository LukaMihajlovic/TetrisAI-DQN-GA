import random
import math
from state import Candidate
from figures import Figure
from tetris import Tetris
from heuristic import Genetic
import os.path




def object_compare(x, y):
    if y.fitness > x.fitness:
        return 1
    elif x.fitness == y.fitness:
        return 0
    else:  # x.fitness < y.fitness
        return -1

def naming_file(n):
    num=n
    name = "gen" + str(num) + ".txt"
    if os.path.isfile(name):
        num +=1
        return naming_file(num)
    else:
        return name


class Genetic1:


    def randomInteger(self,min,max):
        return math.floor(random.random() * (max-min) + min)

    def normalize(self,candidate):
        norm = math.sqrt(candidate.heightWeight * candidate.heightWeight + candidate.linesWeight * candidate.linesWeight + candidate.holesWeight * candidate.holesWeight + candidate.bumpinessWeight * candidate.bumpinessWeight)
        candidate.heightWeight /= norm
        candidate.linesWeight /= norm
        candidate.holesWeight /= norm
        candidate.bumpinessWeight /= norm

    def generateRandomCandidate(self):

        candidate = Candidate(None,None,None,None,None)
        candidate.heightWeight = random.random() - 0.5
        candidate.linesWeight = random.random() - 0.5
        candidate.holesWeight = random.random() - 0.5
        candidate.bumpinessWeight = random.random() - 0.5

        self.normalize(candidate)
        return candidate


    def sort_candidates(self,candidates):
        candidates.sort(object_compare)
        return candidates

    def computeFitnesses(self,candidates,numberOfGames,maxNumberOfMoves):
        dict = {}
        for e in Figure:
            dict[e.name] = e.value
        for i in range(len(candidates)):
            print i
            candidate = candidates[i]
            totalScore=0
            for j in range(numberOfGames):
                tetris = Tetris()
                nextFigure = tetris.stone_next()
                score = 0
                numberOfMoves = 0
                while numberOfMoves < maxNumberOfMoves and not tetris.end_game():
                    numberOfMoves+=1
                    state = tetris.generate_states_for_action(dict, nextFigure)
                    nextFigure = tetris.stone_next()

                    maks_heuristic = -10000
                    maks_idx = 0
                    for i in range(len(state.states)):

                        genetic = Genetic(state.states[i])

                        heuristic = genetic.training(candidate.heightWeight,candidate.linesWeight,candidate.holesWeight,candidate.bumpinessWeight)
                        if heuristic > maks_heuristic:
                            maks_heuristic = heuristic
                            maks_idx = i

                    tetris.state = state.states[maks_idx]
                    score+=tetris.check_for_cleared_lines()

                totalScore+=score

            candidate.fitness=totalScore


    def selectPair(self,candidates,ways):
        indices=[]
        for i in range(len(candidates)):
            indices.append(i)

        fittestCandidateIndex1 = None
        fittestCandidateIndex2 = None

        for j in range(ways):
            num = self.randomInteger(0,len(indices))
            selectedIndex = indices[int(num)]
            del indices[int(num)]

            if fittestCandidateIndex1 == None or selectedIndex < fittestCandidateIndex1:
                fittestCandidateIndex2=fittestCandidateIndex1
                fittestCandidateIndex1=selectedIndex

            elif fittestCandidateIndex2 == None or selectedIndex < fittestCandidateIndex2:
                fittestCandidateIndex2 = selectedIndex

        ret_val=[]
        if (candidates[fittestCandidateIndex1].fitness == 0 and candidates[fittestCandidateIndex2].fitness == 0):
            return self.selectPair(candidates,ways)
        ret_val.append(candidates[fittestCandidateIndex1])
        ret_val.append(candidates[fittestCandidateIndex2])
        return ret_val

    def cross_over(self,candidate1,candidate2):
        candidate = Candidate(None,None,None,None,None)

        candidate.heightWeight = candidate1.fitness * candidate1.heightWeight + candidate2.fitness * candidate2.heightWeight
        candidate.linesWeight = candidate1.fitness * candidate1.linesWeight + candidate2.fitness * candidate2.linesWeight
        candidate.holesWeight = candidate1.fitness * candidate1.holesWeight + candidate2.fitness * candidate2.holesWeight
        candidate.bumpinessWeight = candidate1.fitness * candidate1.bumpinessWeight + candidate2.fitness * candidate2.bumpinessWeight

        self.normalize(candidate)

        return candidate

    def mutate(self,candidate):
        quantity = random.random() * 0.4 - 0.2
        num = self.randomInteger(0,4)

        if num == 0:
            candidate.heightWeight += quantity

        if num == 1:
            candidate.linesWeight += quantity

        if num == 2:
            candidate.holesWeight += quantity

        if num == 3:
            candidate.bumpinessWeight += quantity

    def deleteNLast(self,candidates,newCandidates):

        del candidates[-len(newCandidates):len(candidates)]
        for i in newCandidates:
            candidates.append(i)
        self.sort_candidates(candidates)



if __name__=="__main__":

    g=Genetic1()
    candidates=[]

    for i in range(100):
        candidates.append(g.generateRandomCandidate())

    print ("Computing fitnesses of initial population...")

    g.computeFitnesses(candidates, 5, 200)
    g.sort_candidates(candidates)

    print ("//////////////")
    print (str(candidates[0].fitness))
    print("///////////////")


    count = 0
    fileName = naming_file(0)
    while True:
        newCandidates=[]
        for i in range(30):
            pair = g.selectPair(candidates,10)
            candidate = g.cross_over(pair[0],pair[1])
            if (random.random()<0.05):
                g.mutate(candidate)

            g.normalize(candidate)
            newCandidates.append(candidate)

        print ("Computing fitnesses of new candidates. (" + str(count) + ")")

        g.computeFitnesses(newCandidates,5,200)
        g.deleteNLast(candidates,newCandidates)
        totalFitness = 0
        for i in range(len(candidates)):
            totalFitness += candidates[i].fitness

        with open(fileName, "a") as file:

            file.write("Average cleared lines = " + str(totalFitness / len(candidates))+"\n")
            file.write("Most cleared lines = " + str(candidates[0].fitness) + "(" + str(count) + ")"+"\n")
            file.write("Best heuristic values = " + str(candidates[0].heightWeight)+" | "+str(candidates[0].linesWeight)+" | "+ str(candidates[0].holesWeight)+" | "+str(candidates[0].bumpinessWeight)+"|" + "(" + str(count) + ")"+"\n")
            file.write("\n")
        print("Average fitness = " + str(totalFitness / len(candidates)))
        print("Highest fitness = " + str(candidates[0].fitness) + "(" + str(count) + ")")
        print("Fittest candidate = " + str(candidates[0].heightWeight)+" | "+str(candidates[0].linesWeight)+" | "+ str(candidates[0].holesWeight)+" | "+str(candidates[0].bumpinessWeight)+"|" + "(" + str(count) + ")")






