import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D
import numpy as np

thetaZero = np.linspace(-100, 100, 10000)
thetaOne = np.linspace(-100, 100, 10000)

element = [[1,2],[2,3],[3,4]]
m = len(element)

#integrate thetaZero into cost function. otherwise it yells
def cost(thetaOne, thetaZero):
    results = []
    for i in range(m):
        x = hTheta(element[i][0], thetaOne, thetaZero)
        result = (x-element[i][1])**2
        results.append(result)

    thetaZero = (1 / m) * np.sum(results)
    thetaOne = (1 / m) * np.sum(results) * x
    return [thetaOne, thetaZero]

def hTheta(x, thetaOne, thetaZero):
    return thetaZero + (thetaOne*x)

costFunc = []
for i in range(len(thetaOne)):
    costFunc.append(cost(thetaOne[i], thetaZero[i]))

#matplotlib
ax = plt.figure().add_subplot(111, projection='3d')
ax.plot_surface(thetaOne, thetaZero, costFunc)
plt.legend()
plt.show()

#redefine thetaZero, thetaOne
thetaZero = thetaZero[int(np.where(costFunc==min(costFunc, key=abs))[0][0])]
thetaOne = thetaOne[int(np.where(costFunc==min(costFunc, key=abs))[0][0])]

print("Predicted value for thetaOne: %f" % thetaOne)
print("Predicted value for thetaZero: %f" % thetaZero)
