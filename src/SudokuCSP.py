import csv
from random import shuffle
import numpy as np
from copy import deepcopy


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

    def updateDomain(self, jj, ii, value):
        f = lambda x: int(x / 3) * 3

        #square update
        for j in range(f(jj), f(jj)+3):
            for i in range(f(ii), f(ii)+3):
                if j != jj and i != ii and value in self.domains[(j, i)]:
                    self.domains[(j, i)].remove(value)

        #horizontal update
        for i in range(9):
            if i != ii and value in self.domains[(jj, i)]:
                self.domains[(jj, i)].remove(value)

        #vertical update
        for j in range(9):
            if j != jj and value in self.domains[(j, ii)]:
                self.domains[(j, ii)].remove(value)

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



    def getDomain(self, j, i):
        return self.domains[(j, i)]


class SudokuCSP:

    def __init__(self, puzzlePlain):
        board = SudokuCSP.parsePuzzle(puzzlePlain)
        self.domains = Domain(board)

        # j : column number, i : row number, v : value that we want to check if exist
        row_constraint = lambda j, i, v, board: False if v in board[j, :] else True
        column_constraint = lambda j, i, v, board: False if v in board[:, i] else True
        square_constraint = lambda j, i, v, board: False if v in board[int(j / 3) * 3: int(j / 3) * 3 + 3,
                                                                 int(i / 3) * 3: int(i / 3) * 3 + 3] else True
        self.constraints = [row_constraint, column_constraint, square_constraint]


    def backtracingSearchStart(self):
        board = np.zeros((9,9))
        domains = deepcopy(self.domains)
        solutions = []
        self.globalStepsCounter = 0

        self.backtraceingSearch(board, domains, solutions, stepsNumber=0)
        return solutions, self.globalStepsCounter


    def backtraceingSearch(self, board, domains, solutions, stepsNumber):
        self.globalStepsCounter += 1
        j, i = domains.pickSmallestDomain(board)
        #j, i = domains.pickFirstAvailable(board)

        for elem in self.pickValRandom(domains.getDomain(j, i)):
            if self.checkConstraints(j, i, elem, board):
                tempBoard = deepcopy(board)
                tempBoard[j, i] = elem
                dom = deepcopy(domains)
                dom.updateDomain(j, i, elem)
                if stepsNumber < 80:
                    self.backtraceingSearch(tempBoard, dom, solutions, stepsNumber + 1)
                if stepsNumber >= 80:
                    tempBoard[j, i] = elem
                    solutions.append(tempBoard)
                    return



    def pickValRandom(self, domain):
        tmp = domain[:]
        shuffle(tmp)
        return tmp

    def pickValInOrder(self, domain):
        return domain[:]

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

    for task in sudoku_tasks:
        sudoku = SudokuCSP(task['puzzle'])
        solutions, steps = sudoku.backtracingSearchStart()
        print("ID: %s,  DIFFICULTY: %s" % (task['id'], task['difficulty']))
        print('Total steps: %d' % (steps))
        print("Solutions: %d" % (len(solutions)))
        for num, sol in enumerate(solutions):
            print("------ Solution number: %d -----" % (num+1))
            print(sol)
        if "solution" in task:
            print("Given solution:")
            print(SudokuCSP.parsePuzzle(task['solution']))




