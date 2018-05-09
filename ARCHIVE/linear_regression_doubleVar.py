import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib import cm
import numpy as np

# X = thetaOne
# Y = thetaZero
# Z = costFunc

np.set_printoptions(threshold=10, precision=3)

def cost(X, Y):
    results = []
    for i in range(m):
        x = hTheta(element[i][0], X, Y)
        result = (x-element[i][1])**2
        results.append(result)

    yRes = (1 / m) * np.sum(results)     # thetaZero
    xRes = (1 / 2*m) * np.sum(results) # thetaOne
    # xRes = (1 / (2*m)) * np.sum(results)
    return np.sin(np.sqrt(X ** 2 + Y ** 2))

def hTheta(x, thetaOne, thetaZero):
    return thetaZero + (thetaOne*x)

thetaZero = np.linspace(-10, 10, 50)
thetaOne = np.linspace(-10, 10, 50)

thetaZero, thetaOne = np.meshgrid(thetaZero, thetaOne)

element = np.array([[1,1],[2,2],[3,3]])
m = len(element)

costFunc = []
costFuncRes = []

for i in range(len(thetaOne)):
    costFunc.append(cost(thetaOne[i], thetaZero[i]))
    # for j in range(len(thetaZero)):
    #     costFuncRes.append(cost(thetaOne[i], thetaZero[j]))
    # costFunc.append(costFuncRes)
    # costFuncRes = []

print("ThetaOne:", thetaOne, "\nThetaOne shape:", np.shape(thetaOne))
print("ThetaZero:", thetaZero, "\nThetaZero shape:", np.shape(thetaZero))
print("CostFunc:", costFunc, "\nCostFunc shape:", np.shape(costFunc))

# Plot the surface.
fig = plt.figure()
ax = fig.gca(projection='3d')
plot =  ax.plot_surface(X=thetaOne, Y=thetaZero, Z=np.array(costFunc), cmap='coolwarm', edgecolor='none')
fig.colorbar(plot, shrink=0.5, aspect=5)
ax.set_xlabel('thetaOne')
ax.set_ylabel('thetaZero')
ax.set_zlabel('costFunc')
# plt.plot(thetaOne, costFunc, label="cost")
plt.legend()
plt.show()

#redefine thetaZero, thetaOne
thetaZero = thetaZero[int(np.where(costFunc==min(costFunc, key=abs))[0][0])]
thetaOne = thetaOne[int(np.where(costFunc==min(costFunc, key=abs))[0][0])]

print("Predicted value for thetaOne: %f" % thetaOne)
print("Predicted value for thetaZero: %f" % thetaZero)