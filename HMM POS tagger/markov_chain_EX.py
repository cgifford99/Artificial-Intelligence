import numpy as np

weatherCond = ["sunny", "cloudy", "rainy"]
weatherProb = np.array([[0.6, 0.3, 0.1],
                        [0.2, 0.3, 0.5],
                        [0.4, 0.1, 0.5]])
initialStateProb = [0.6, 0.3, 0.1]
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
countArr = [0, 0, 0]

for i in range(100):
    initialState = np.random.choice(a=len(initialStateProb), p=initialStateProb)
    for j in range(3):
        if initialState == j:
            countArr[j] += 1
    initialState = weatherCond[initialState]
    print("Day %d: %s" % (i + 3, initialState))

print("Sunny appeared %s times" % countArr[0])
print("Cloudy appeared %s times" % countArr[1])
print("Rainy appeared %s times" % countArr[2])