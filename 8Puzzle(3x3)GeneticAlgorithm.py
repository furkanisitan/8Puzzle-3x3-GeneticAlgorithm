import numpy as np
from enum import Enum
from random import randint


MAX_GENERATION = 1000
POPULATION_SIZE = 20
CHROMOSOME_LENGTH = 20
NUMBER_OF_SELECTED_CHROMOSOME = 3
INCREMENT_RANGE_FOR_CHROMOSOME_LENGTH = 50
INCREMENT_SIZE_FOR_CHROMOSOME_LENGTH = 5

goal = np.array([[1, 2, 3], [8, 9, 4], [7, 6, 5]])
initial = np.array([[1, 3, 2], [8, 9, 4], [5, 6, 7]])


class Direction(Enum):
    U = 1
    R = 2
    D = 3
    L = 4

    def isEqual(self, direction):
        return self == direction

    def isOpposite(self, direction):
        return abs(self.value - direction.value) == 2

    def getOpposite(self):
        return Direction(self.value - 2) if self.value > 2 else Direction(self.value + 2)

    def getDifferent(self):
        enums = list(Direction)
        enums.remove(self)
        return enums[randint(0, 2)]

    def getDifferentAxis(self):
        enums = list(Direction)
        enums.remove(self)
        enums.remove(self.getOpposite())
        return enums[randint(0, 1)]


class Puzzle:

    def __init__(self):
        self.puzzle = np.array(initial)

    def move(self, direction):

        if not isinstance(direction, Direction):
            raise TypeError('direction must be an instance of Direction Enum')

        x, y = np.where(self.puzzle == 9)
        if direction == Direction.U:
            if x == 0:
                raise IndexError("the x coordinate cannot be a negative value")
            self.__swap([x, y], [x-1, y])
        elif direction == Direction.R:
            if y == 2:
                raise IndexError(
                    "the y coordinate exceeds the range of the puzzle.")
            self.__swap([x, y], [x, y+1])
        elif direction == Direction.D:
            if x == 2:
                raise IndexError(
                    "the x coordinate exceeds the range of the puzzle.")
            self.__swap([x, y], [x+1, y])
        elif direction == Direction.L:
            if y == 0:
                raise IndexError("the y coordinate cannot be a negative value")
            self.__swap([x, y], [x, y-1])

    def __swap(self, coordinate1, coordinate2):
        tmp = self.puzzle[coordinate1[0], coordinate1[1]]
        self.puzzle[coordinate1[0], coordinate1[1]
                    ] = self.puzzle[coordinate2[0], coordinate2[1]]
        self.puzzle[coordinate2[0], coordinate2[1]] = tmp

    def fitness(self):
        mdis = 0
        for i in range(3):
            for j in range(3):
                if (goal[i, j] == 9):
                    continue
                x, y = np.where(self.puzzle == goal[i, j])
                mdis += abs(x[0]-i) + abs(y[0]-j)
        return mdis

    def __str__(self):
        return str(self.puzzle)


def createChromosome(length=CHROMOSOME_LENGTH):
    chromosome = []
    enums = list(Direction)
    [chromosome.append(enums[randint(0, 3)]) for i in range(length)]
    return chromosome


def initializePopulation():
    population = []
    [population.append(createChromosome(CHROMOSOME_LENGTH))
     for i in range(POPULATION_SIZE)]
    return population


# <chromosome>'a (yani List<Direction>) düzeltme uygular
# - 3x3 lük puzzle da peş peşe 3 kere aynı yöne hareket yapılamaz
# - Peş peşe zıt hareketler yapmak anlamsızdır/gereksizdir
def mutation(chromosome):
    lenght = len(chromosome)

    if (lenght < 2):
        return chromosome

    if (lenght < CHROMOSOME_LENGTH):
        chromosome += createChromosome(CHROMOSOME_LENGTH-lenght)

    if (chromosome[0].isOpposite(chromosome[1])):
        chromosome[1] = chromosome[1].getDifferent()

    for i in range(2, lenght):
        # peş peşe 3 kere aynı hareket
        if (chromosome[i].isEqual(chromosome[i-2]) and chromosome[i].isEqual(chromosome[i-1])):
            chromosome[i] = chromosome[i-1].getDifferentAxis()
        # zıt yön
        elif(chromosome[i].isOpposite(chromosome[i-1])):
            chromosome[i] = chromosome[i-1].getDifferent()


# <chromosome>'u başlangıç puzzle'ına uygular.
# Eğer yönlerden biri puzzle'a uygulandığında puzzle'ın dışına çıkılıyor ise
# bu yön farklı eksenden bir yön ile değiştirilir.
def applyChromosomeToPuzzle(chromosome):
    puzzle = Puzzle()
    i = 0
    while i < len(chromosome):
        try:
            if (puzzle.fitness() == 0):
                return [chromosome[:i], puzzle]
            puzzle.move(chromosome[i])
            i += 1
        except IndexError:
            chromosome[i] = chromosome[i].getDifferentAxis()
    return [chromosome, puzzle]


def crossover(chromosomes, index=0):
    if (NUMBER_OF_SELECTED_CHROMOSOME == index+1):
        return
    for i in range(index+1, NUMBER_OF_SELECTED_CHROMOSOME):
        chromosomes += (crossing(chromosomes[index], chromosomes[i]))
    crossover(chromosomes, index+1)


def crossing(chromosome1, chromosome2):
    i = randint(0, CHROMOSOME_LENGTH//2-1)
    j = randint(CHROMOSOME_LENGTH//2, CHROMOSOME_LENGTH)

    c1 = chromosome1[:i] + chromosome2[i:]
    c2 = chromosome2[:i] + chromosome1[i:]

    c3 = chromosome1[:j] + chromosome2[j:]
    c4 = chromosome2[:j] + chromosome1[j:]

    c5 = chromosome1[:i] + chromosome2[i:j] + chromosome1[j:]
    c6 = chromosome2[:i] + chromosome1[i:j] + chromosome2[j:]

    c7 = chromosome1[j:] + chromosome1[:i] + chromosome2[i:j]
    c8 = chromosome2[j:] + chromosome2[:i] + chromosome1[i:j]

    c9 = chromosome2[i:j] + chromosome1[:i] + chromosome1[j:]
    c10 = chromosome1[i:j] + chromosome2[:i] + chromosome2[j:]

    return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]


# En iy kromozomları döner.
# return : [[chromosome, puzzle], ...]
def selection(chromosomes):
    res = []
    for chromosome in chromosomes:
        tmp = applyChromosomeToPuzzle(chromosome)
        res.append([tmp[0], tmp[1]])
    res.sort(key=lambda x: x[1].fitness())
    return res[:NUMBER_OF_SELECTED_CHROMOSOME]


def getStrOfChromosome(chromosome):
    txt = ', '.join([x.name for x in chromosome])
    return f"{txt}"


def solution():

    global CHROMOSOME_LENGTH
    generation, numOfIncrement, bestmdis = 0, 0, 36
    bestSelection = []

    population = initializePopulation()
    while generation < MAX_GENERATION:

        generation += 1

        # mutasyon
        for item in (population):
            mutation(item)

        # seçilim
        slct = selection(population)
        mdis = slct[0][1].fitness()
        population = [item[0] for item in slct]

        # en iyi seçim
        if (mdis < bestmdis):
            bestmdis = mdis
            bestSelection = slct[0]

        # kromozom uzunluğunu arttırma
        if (generation//INCREMENT_RANGE_FOR_CHROMOSOME_LENGTH > numOfIncrement):
            numOfIncrement += 1
            CHROMOSOME_LENGTH += INCREMENT_SIZE_FOR_CHROMOSOME_LENGTH

        print(f"generation: {generation} | fitness: {mdis}")

        # Sonuç bulundu
        if (mdis == 0):
            break

        crossover(population)

    print("---------------------------")
    print("initial")
    print(initial)
    print()
    print("goal")
    print(goal)
    print("---------------------------")
    print(f"fitness: {bestSelection[1].fitness()}")
    print(f"best chromosome\n{getStrOfChromosome(bestSelection[0])}")
    print(f"final status\n{bestSelection[1]}")


if __name__ == "__main__":
    solution()
