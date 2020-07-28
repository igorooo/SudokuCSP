import csv
from random import shuffle, randint, choice
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt


def parser(filePath):
    sudoku_instances = []
    with open(filePath, 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')

        for row in csv_reader:
            instance = {'id': row[0],
                        'difficulty': row[1],
                        'puzzle': row[2]}
            if len(row) == 4:
                if len(row[3]) > 3:
                    instance['solution'] = row[3]

            sudoku_instances.append(instance)
    sudoku_instances.pop(0)
    return sudoku_instances


class Domain:
    def __init__(self, board):
        self.domains = {}
        for j in range(9):
            for i in range(9):
                if board[j][i] != 0:
                    self.domains[(j, i)] = [board[j][i]]
                else:
                    self.domains[(j, i)] = [1,2,3,4,5,6,7,8,9]

    def updateDomain(self, jj, ii, value, board):
        f = lambda x: int(x / 3) * 3
        outOfDomainElems = False
        exclusions = 0

        #square update
        for j in range(f(jj), f(jj)+3):
            for i in range(f(ii), f(ii)+3):
                if j != jj and i != ii and value in self.domains[(j, i)]:
                    self.domains[(j, i)].remove(value)
                    exclusions += 1

                    # if no more available values in domain and still no value on board
                    if len(self.domains[(j, i)]) ==  board[j, i] == 0:
                        outOfDomainElems = True

        #horizontal update
        for i in range(9):
            if i != ii and value in self.domains[(jj, i)]:
                self.domains[(jj, i)].remove(value)
                exclusions += 1

                if len(self.domains[(jj, i)]) == board[jj, i] == 0:
                    outOfDomainElems = True

        #vertical update
        for j in range(9):
            if j != jj and value in self.domains[(j, ii)]:
                self.domains[(j, ii)].remove(value)
                exclusions += 1

                if len(self.domains[(j, ii)]) == board[j, ii] == 0:
                    outOfDomainElems = True

        return outOfDomainElems, exclusions

    def pickSmallestDomain(self, board):
        bestL = 10
        bJ, bI = 0, 0
        for j in range(9):
            for i in range(9):
                if len(self.domains[(j, i)]) < bestL and board[j, i] == 0:
                    bestL = len(self.domains[(j, i)])
                    bJ, bI = j, i
        return bJ, bI

    def pickFirstAvailable(self, board):
        for j in range(9):
            for i in range(9):
                if board[j, i] == 0:
                    return j, i
        raise AssertionError("board filled!")

    def pickRandom(self, board):
        options = []
        for j in range(9):
            for i in range(9):
                if board[j, i] == 0:
                    options.append((j, i))
        return choice(options)



    def getDomain(self, j, i):
        return self.domains[(j, i)]


class SudokuCSP:

    SMALLEST_DOMAIN = 'Smallest Domain'
    RANDOM = 'Random'
    IN_ORDER = 'In Order'
    LESS_CONSTR = 'Less constrainting'

    TRESHOLD = 1000000

    def __init__(self, puzzlePlain):
        board = SudokuCSP.parsePuzzle(puzzlePlain)
        self.domains = Domain(board)

        # j : column number, i : row number, v : value that we want to check if exist
        row_constraint = lambda j, i, v, board: False if v in board[j, :] else True
        column_constraint = lambda j, i, v, board: False if v in board[:, i] else True
        square_constraint = lambda j, i, v, board: False if v in board[int(j / 3) * 3: int(j / 3) * 3 + 3,
                                                                 int(i / 3) * 3: int(i / 3) * 3 + 3] else True
        self.constraints = [row_constraint, column_constraint, square_constraint]


    def backtracingSearchStart(self, forwardChecking=False, pickVarMethod=SMALLEST_DOMAIN, pickValMethod=RANDOM):
        board = np.zeros((9,9))
        domains = deepcopy(self.domains)
        solutions = []
        self.globalStepsCounter = 0

        self.backtraceingSearch(board, domains, solutions, stepsNumber=0, forwardChecking=forwardChecking,
                                pickVarMethod=pickVarMethod, pickValMethod=pickValMethod)
        return solutions, self.globalStepsCounter


    def backtraceingSearch(self, board, domains, solutions, stepsNumber, forwardChecking, pickVarMethod, pickValMethod):
        #print(self.globalStepsCounter)
        self.globalStepsCounter += 1
        if self.globalStepsCounter > SudokuCSP.TRESHOLD:
            return

        j, i = 0, 0
        if pickVarMethod == SudokuCSP.RANDOM:
            j, i = domains.pickRandom(board)
        elif pickVarMethod == SudokuCSP.IN_ORDER:
            j, i = domains.pickFirstAvailable(board)
        else:
            j, i = domains.pickSmallestDomain(board)

        values = None
        if pickValMethod == SudokuCSP.RANDOM:
            values = self.pickValLessConstr(domains.getDomain(j, i), j, i, domains, board)
        elif pickValMethod == SudokuCSP.IN_ORDER:
            values = self.pickValLessConstr(domains.getDomain(j, i), j, i, domains, board)
        else:
            values = self.pickValLessConstr(domains.getDomain(j, i), j, i, domains, board)

        for elem in values:
            if self.checkConstraints(j, i, elem, board):
                tempBoard = deepcopy(board)
                tempBoard[j, i] = elem
                dom = deepcopy(domains)

                outOfAvailableDomainElems, _ = dom.updateDomain(j, i, elem, tempBoard)
                if forwardChecking and outOfAvailableDomainElems:
                    #then omit current tree
                    continue

                if stepsNumber < 80:
                    self.backtraceingSearch(tempBoard, dom, solutions, stepsNumber + 1, forwardChecking,
                                            pickVarMethod, pickValMethod)
                if stepsNumber >= 80:
                    tempBoard[j, i] = elem
                    solutions.append(tempBoard)
                    return



    def pickValRandom(self, domain, j, i, domains, board):
        tmp = domain[:]
        shuffle(tmp)
        return tmp

    def pickValInOrder(self, domain, j, i, domains, board):
        return domain[:]

    def pickValLessConstr(self, domain, j, i, domains, board):
        arr = []
        for elem in domain:
            doms = deepcopy(domains)
            _, exclusives = doms.updateDomain(j, i, elem, board)
            arr.append((elem, exclusives))
        res = [x[0] for x in sorted(arr, key=lambda x : x[1], reverse=True)]
        return res

    def checkConstraints(self, column, row, value, board):
        for constraint in self.constraints:
            if constraint(column, row, value, board) == False:
                return False
        return True

    @staticmethod
    def parsePuzzle(puzzlePlain):
        board = np.zeros((9,9))
        i = j = 0
        # j column
        # i row
        for ch in puzzlePlain:
            if ch != '.':
                board[j, i] = int(ch)

            i = i + 1
            if i >= 9:
                i = 0
                j = j + 1
        return board

    @staticmethod
    def printBoard(board):
        for j in range(9):
            for i in range(9):
                print(board[j, i], end=' ')
            print('')

if __name__ == '__main__':
    sudoku_tasks = parser('../data/Sudoku.csv')
    #puzzlePlain = '625..1..8.7..8...68........2....4....4..1.3........1.......7.32.....6.9..84.3....'

    # first number
    # 1 - SMALLEST DOMAIN VAR
    # 2 - RANDOM VAR
    # 3 - IN ORDER VAR

    # second number
    # 1 - LESS CONSTRAINTING VAL
    # 2 - RANDOM VAL
    # 3 - IN ORDER VAL

    # third number
    # 1 - with forward checking
    # 0 - without forward checking

    results = {
        '110' : [],
        '120' : [],
        '130' : [],
        '121' : [],
        '211' : [],
        '221' : [],
        '231' : [],
        '311' : [],
        '321' : [],
        '331' : [],
    }

    iter = 0

    for task in sudoku_tasks:
        print("ID: %s,  DIFFICULTY: %s" % (task['id'], task['difficulty']))
        sudoku = SudokuCSP(task['puzzle'])

        results['110'].append(sudoku.backtracingSearchStart(forwardChecking=False,
                                                         pickVarMethod=SudokuCSP.SMALLEST_DOMAIN,
                                                         pickValMethod=SudokuCSP.LESS_CONSTR))

        results['120'].append(sudoku.backtracingSearchStart(forwardChecking=False,
                                                            pickVarMethod=SudokuCSP.SMALLEST_DOMAIN,
                                                            pickValMethod=SudokuCSP.RANDOM))

        results['130'].append(sudoku.backtracingSearchStart(forwardChecking=False,
                                                            pickVarMethod=SudokuCSP.SMALLEST_DOMAIN,
                                                            pickValMethod=SudokuCSP.IN_ORDER))

        results['121'].append(sudoku.backtracingSearchStart(forwardChecking=True,
                                                            pickVarMethod=SudokuCSP.SMALLEST_DOMAIN,
                                                            pickValMethod=SudokuCSP.RANDOM))

        results['211'].append(sudoku.backtracingSearchStart(forwardChecking=True,
                                                            pickVarMethod=SudokuCSP.RANDOM,
                                                            pickValMethod=SudokuCSP.LESS_CONSTR))

        results['221'].append(sudoku.backtracingSearchStart(forwardChecking=True,
                                                            pickVarMethod=SudokuCSP.RANDOM,
                                                            pickValMethod=SudokuCSP.RANDOM))

        results['231'].append(sudoku.backtracingSearchStart(forwardChecking=True,
                                                            pickVarMethod=SudokuCSP.RANDOM,
                                                            pickValMethod=SudokuCSP.IN_ORDER))

        results['311'].append(sudoku.backtracingSearchStart(forwardChecking=True,
                                                            pickVarMethod=SudokuCSP.IN_ORDER,
                                                            pickValMethod=SudokuCSP.LESS_CONSTR))

        results['321'].append(sudoku.backtracingSearchStart(forwardChecking=True,
                                                            pickVarMethod=SudokuCSP.IN_ORDER,
                                                            pickValMethod=SudokuCSP.RANDOM))

        results['331'].append(sudoku.backtracingSearchStart(forwardChecking=True,
                                                            pickVarMethod=SudokuCSP.IN_ORDER,
                                                            pickValMethod=SudokuCSP.IN_ORDER))

        iter += 1
        break


    stepsArr = [i for i in range(1, iter + 1)]


    for key, result in results.items():

        noOfSteps = []
        noOfSolutions = []

        for res in result:
            noOfSolutions.append(len(res[0]))
            noOfSteps.append(res[1])


        plt.figure().suptitle('Wyniki(' + key + ')', fontsize=10)
        plt.plot(stepsArr, noOfSolutions, 'r+')
        plt.legend()
        plt.show()
        plt.clf()
        plt.figure().suptitle('Liczb kroków(' + key + ')', fontsize=10)
        plt.plot(stepsArr, noOfSteps)
        plt.legend()
        plt.show()








