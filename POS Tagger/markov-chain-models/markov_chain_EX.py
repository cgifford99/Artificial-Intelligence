import numpy as np


randArray = np.full((6, 6), 6)

weatherCond = ["sunny", "cloudy", "rainy", "snow"]
weatherProb = np.array([[0.5, 0.3, 0.1, 0.1],
                        [0.2, 0.2, 0.4, 0.2],
                        [0.3, 0.1, 0.4, 0.2],
                        [0.1, 0.4, 0.2, 0.3]])
initialStateProb = [0.1, 0.6, 0.2, 0.1]
weatherProbConvert = np.array([])

initialState = np.random.choice(a= len(initialStateProb), p=initialStateProb)
for i in range(len(weatherProb[:,initialState])):
    weatherProbConvert = np.append(weatherProbConvert, weatherProb[initialState][i])
nextState = np.random.choice(a= len(weatherProbConvert), p=weatherProbConvert)
nextPath = weatherProb[nextState][initialState]

initialState = weatherCond[initialState]
nextState = weatherCond[nextState]

print("Day 1: %s" % initialState)
print("Day 2: %s" % nextState)

# Random choice testing
numDays = [0, 0, 0, 0]

for i in range(100):
    initialState = np.random.choice(a=len(initialStateProb), p=initialStateProb)
    for j in range(4):
        if initialState == j:
            numDays[j] += 1
    initialState = weatherCond[initialState]
    print("Day %d: %s" % (i + 3, initialState))

print("Sunny appeared %s times" % numDays[0])
print("Cloudy appeared %s times" % numDays[1])
print("Rainy appeared %s times" % numDays[2])
print("Snowy appeared %s times" % numDays[3])