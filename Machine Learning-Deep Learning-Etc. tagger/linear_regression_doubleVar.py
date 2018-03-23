import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib import cm
import numpy as np

np.set_printoptions(threshold=10, precision=3)
#integrate thetaZero into cost function. otherwise it yells
def cost(thetaOne, thetaZero):
    results = []
    for i in range(m):
        x = hTheta(element[i][0], thetaOne, thetaZero)
        result = (x-element[i][1])**2
        results.append(result)

    thetaZRes = (1 / m) * np.sum(results)
    thetaORes = (1 / m) * np.sum(results*x)
    return thetaORes

def hTheta(x, thetaOne, thetaZero):
    return thetaZero + (thetaOne*x)

thetaZero = np.linspace(-10, 10, 100)
thetaOne = np.linspace(-10, 10, 100)

thetaZero, thetaOne = np.meshgrid(thetaZero, thetaOne)

element = np.array([[1,2],[2,3],[3,4]])
m = len(element)

costFunc = []
for j in range(len(thetaOne)):
    result = cost(thetaOne[j], thetaZero[j])
    costFunc.append(result)

costFuncArr = costFunc
costFunc = []
for i in range(len(costFuncArr)):
    costFunc.append(costFuncArr)

# print(costFunc)
#
# print("ThetaOne:", thetaOne, "\nThetaOne shape:", np.shape(thetaOne))
# print("ThetaZero:", thetaZero, "\nThetaZero shape:", np.shape(thetaZero))
# print("CostFunc:", costFunc, "\nCostFunc shape:", np.shape(costFunc))

# thetaOne = np.arange(-5, 5, 0.25)
# thetaZero = np.arange(-5, 5, 0.25)
# thetaOne, thetaZero = np.meshgrid(thetaOne, thetaZero)
# R = np.sqrt(thetaOne**2 + thetaZero**2)
# costFunc = np.sin(R)


# Plot the surface.
fig = plt.figure()
ax = fig.gca(projection='3d')
plot =  ax.plot_surface(X=thetaOne, Y=thetaZero, Z=np.array(costFunc), rstride=1, cstride=1,
                cmap='coolwarm', edgecolor='none')
fig.colorbar(plot, shrink=0.5, aspect=5)
ax.set_xlabel('thetaOne')
ax.set_ylabel('thetaZero')
ax.set_zlabel('costFunc')
plt.show()

#redefine thetaZero, thetaOne
thetaZero = thetaZero[int(np.where(costFunc==min(costFunc, key=abs))[0][0])]
thetaOne = thetaOne[int(np.where(costFunc==min(costFunc, key=abs))[0][0])]

print("Predicted value for thetaOne: %f" % thetaOne)
print("Predicted value for thetaZero: %f" % thetaZero)