import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D
import numpy as np

#integrate thetaZero into cost function. otherwise it yells
def cost(thetaOne):
    results = []
    for i in range(m):
        x = hTheta(element[i][0], thetaOne, thetaZero)
        result = (x-element[i][1])**2
        results.append(result)

    thetaOne = (1 / (2*m)) * np.sum(results)
    return thetaOne

def hTheta(x, thetaOne, thetaZero):
    return thetaZero + (thetaOne*x)

thetaZero = -20
thetaOne = np.linspace(-100, 100, 100)

element = [[1,1],[2,2],[3,3],[4,4]]
m = len(element)

costFunc = []
for i in range(len(thetaOne)):
    costFunc.append(cost(thetaOne[i]))

print("ThetaOne:", thetaOne, "\nThetaOne shape:", np.shape(thetaOne))
print("ThetaZero:", thetaZero, "\nThetaZero shape:", np.shape(thetaZero))
print("CostFunc:", costFunc, "\nCostFunc shape:", np.shape(costFunc))


#matplotlib
plt.plot(thetaOne, costFunc)
plt.legend()
plt.show()

#redefine thetaZero, thetaOne
thetaZero = thetaZero
thetaOne = thetaOne[int(np.where(costFunc==min(costFunc, key=abs))[0][0])]

print("Predicted value for thetaOne: %f" % thetaOne)
print("Predicted value for thetaZero: %f" % thetaZero)
