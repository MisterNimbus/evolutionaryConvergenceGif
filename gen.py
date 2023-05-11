import math
import random
import string

target = "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor"
population_size = 100
mutation_rate = 0.09

"""
(phrase, fitness)
"""
population = []

def createPop():

    for i in range(0, population_size):
        population.append((''.join(random.choice(string.ascii_letters + string.digits +' ') for _ in range(len(target))), 0))

    calcFitness()

def createNewPop():
    matingPool = []
    for item in population:
        for i in range(item[1]):
            matingPool.append(item)
    if  len(matingPool) ==0:
        matingPool = population

    population.clear()

    for i in range(population_size):
        parent1 = matingPool[random.randint(0, len(matingPool)-1)]
        parent2 = matingPool[random.randint(0, len(matingPool)-1)]
        evolvedPhrase = mutate(crossover(parent1[0], parent2[0]))
        child = (evolvedPhrase,0)
        population.append(child)
    
    calcFitness()

def calcFitness():
    global population
    for j in range(len(population)):
        score = 0
        for i in range(len(target)):
            if target[i] == population[j][0][i]:
                score += 1
        population[j] = (population[j][0], math.floor(100*(score/len(target))))

    population = sorted(population, key=lambda x: x[1], reverse=True)


def crossover(parent1:str, parent2:str):
    result = ""
    for i in range(len(target)):
        if i % 2 == 0:
            result += parent1[i]
        else:
            result += parent2[i]
    return result

def mutate(phrase:str):
    p = list(phrase)
    for i in range(len(phrase)):
        if random.uniform(0, 1) < mutation_rate:
            if p[i] != target[i]:
                p[i] = random.choice(string.ascii_letters + string.digits + ' ')
    return "".join(p)



createPop()
generations = 0
while True:
    createNewPop()
    print(population[0])
    generations += 1
    if  population[0][1] == 100 :
        print("Number of generations: " + str(generations))
        break;