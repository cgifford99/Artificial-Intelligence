import numpy as np
import time

inputX = np.arange(0, 10, 1/64)
expecOutput = np.arange(0, 1, 1/16)
hiddenUnits = [64, 32, 24, 16]
steps = 1000
learningRate = 1


class Node:
    def __init__(self, inputs, weights, biases, nodeNum, actFunc):
        self.inputs = inputs
        self.weights = weights
        self.biases = biases
        self.nodeNum = nodeNum
        self.actFunc = actFunc

    def activate(self, layer):
        results = []
        # # iterate through each incoming input
        for inputID in range(len(self.inputs)):
            results.append(self.inputs[inputID] * self.weights[layer][self.nodeNum][inputID])
        results.append(self.biases[layer][self.nodeNum])
        actOutput = np.sum(results)
        return self.actFunc(actOutput)


class Network:
    def __init__(self, xSize, ySize, hiddenLayers, learningRate, actFunc):
        self.xSize = xSize
        self.ySize = ySize
        self.hiddenLayers = hiddenLayers
        self.learningRate = learningRate
        self.layers = []
        self.layers.append(xSize)
        for i in range(len(hiddenLayers)):
            self.layers.append(hiddenLayers[i])
        self.layers.append(ySize)

        if actFunc.__name__ is 'sigmoid':
            self.actFunc = Activation().sigmoid
            self.actFuncDerivative = Activation().sigmoidDerivation
        # other activation functions below are nonfunctional
        elif actFunc.__name__ is 'softmax':
            self.actFunc = Activation().softmax
            self.actFuncDerivative = Activation().softmaxDerivation
        elif actFunc.__name__ is 'relu':
            self.actFunc = Activation().relu
            self.actFuncDerivative = Activation().reluDerivation

    def setWeights(self, layers, num):
        # setting initial weights for the first step
        # these will quickly get overwritten, but constructs the weight vector shape to be used throughout
        if num == 1:
            num = np.random.uniform(0, 1)
        layerWeight = []
        for i in range(len(layers) - 1):
            nodeWeight = []
            for j in range(layers[i + 1]):
                initWeight = []
                for k in range(layers[i]):
                    initWeight.append(num)
                nodeWeight.append(initWeight)
            layerWeight.append(nodeWeight)
        return layerWeight

    def setBias(self, layers, num):
        if num == 1:
            num = np.random.randint(0, 1)
        layerBias = []
        for i in range(len(layers) - 1):
            nodeBias = []
            for i in range(layers[i + 1]):
                nodeBias.append(num)
            layerBias.append(nodeBias)
        return layerBias

    def train(self, x, w, b, expecX):
        # inital foward pass
        x = self.forwardProp(x, w, b)
        # error is evaluated and an attempt to reduce is made
        self.errorSum = self.errorEval(x, expecX)
        # backpropagation begins
        w, b = self.backProp(x, expecX, w, b)
        return x, w, b

    def errorEval(self, outputX, targetX):
        # evaluate error at each step
        # this method uses mean squared error
        # other methods are available, but not yet implemented
        sumArr = []
        for i in range(len(targetX)):
            sumArr.append((outputX[i] - targetX[i]) ** 2)
        self.errorArr = sumArr
        return 1 / len(targetX) * np.sum(sumArr)

    def forwardProp(self, input, weight, bias):
        # iterate through specified network (individual layers then individual nodes)
        nodes = []
        self.layerOutput = [input]
        # layer iteration
        for layer in range(len(self.layers) - 1):
            # node iteration
            for nodeNum in range(self.layers[layer + 1]):
                # node computation
                node = Node(inputs=input,
                            weights=weight,
                            biases=bias,
                            nodeNum=nodeNum,
                            actFunc=self.actFunc)
                # node computation based on input, weight and bias
                # weights are randomly generated for first step then computed based on
                # margin of error for the previous step
                result = node.activate(layer)
                nodes.append(result)
            self.layerOutput.append(nodes)
            input = self.layerOutput[-1]
            nodes = []
        return input

    def backProp(self, outputX, targetX, weight, bias):
        # partial derivation of error eval (outout function backprop)
        # partial derivation of sigmoid x2 (hidden layer function backprop
        # sum above func

        # output layer
        deltaArrW = self.setWeights(self.layers, 1)
        newWeights = self.setWeights(self.layers, 1)
        deltaArrB = self.setBias(self.layers, 1)
        newBiases = self.setBias(self.layers, 1)
        node = -1
        while node >= -len(newWeights[-1]):
            # weight computation of output layer
            for weightID in range(len(newWeights[-1][node])):
                tErrorOutO = outputX[node] - targetX[node]
                outNet = self.actFuncDerivative(outputX[node])
                netWeight = self.layerOutput[-2][weightID]

                deltaArrW[-1][node][weightID] = tErrorOutO * outNet

                tErrorWeight = tErrorOutO * outNet * netWeight
                newWeight = weight[-1][node][weightID] - (self.learningRate * tErrorWeight)
                newWeights[-1][node][weightID] = newWeight
            node -= 1

        # bias computation of output layer
        for biasID in range(len(newBiases[-1])):
            tErrorOutOB = outputX[biasID] - targetX[biasID]
            outNetB = self.actFuncDerivative(self.layerOutput[-1][biasID])
            netWeightB = 1

            deltaArrB[-1][biasID] = tErrorOutOB * outNetB

            tErrorBias = tErrorOutOB * outNetB * netWeightB
            newBias = bias[-1][biasID] - (self.learningRate * tErrorBias)
            newBiases[-1][biasID] = newBias

        # hidden layer
        layerH = -2
        # layer iteration
        while layerH >= -len(newWeights):
            nodeH = -1
            # node iteration
            while nodeH >= -len(newWeights[layerH]):
                # weight computation for hidden layers
                # weight iteration
                for weightIDH in range(len(newWeights[layerH][nodeH])):
                    deltaSum = []
                    for nxtLayerNodes in range(self.layers[layerH + 1]):
                        deltaSum.append(newWeights[layerH + 1][nxtLayerNodes][nodeH] *
                                        deltaArrW[layerH + 1][nxtLayerNodes][nodeH])

                    outNetH = self.actFuncDerivative(self.layerOutput[layerH][nodeH])
                    delta = np.sum(deltaSum) * outNetH
                    netWeightH = self.layerOutput[layerH - 1][weightIDH]
                    tErrorWeightH = delta * netWeightH

                    deltaArrW[layerH][nodeH][weightIDH] = delta

                    newWeightH = weight[layerH][nodeH][weightIDH] - (self.learningRate * tErrorWeightH)
                    newWeights[layerH][nodeH][weightIDH] = newWeightH
                nodeH -= 1

            # bias computation for hidden layers
            for biasIDH in range(len(newBiases[layerH])):
                deltaSumB = []
                for nxtLayerNodes in range(self.layers[layerH + 1]):
                    deltaSumB.append(newBiases[layerH + 1][nxtLayerNodes] *
                                     deltaArrB[layerH + 1][nxtLayerNodes])

                outNetHB = self.actFuncDerivative(self.layerOutput[layerH][biasIDH])
                deltaB = np.sum(deltaSumB) * outNetHB
                netWeightHB = 1
                tErrorWeightHB = deltaB * netWeightHB

                deltaArrB[layerH][biasIDH] = deltaB

                newBiasH = bias[layerH][biasIDH] - (self.learningRate * tErrorWeightHB)
                newBiases[layerH][biasIDH] = newBiasH

            layerH -= 1

        return newWeights, newBiases

    def predict(self, x, w, b):
        return self.forwardProp(x, w, b)

    def evalAccuracy(self, y, expec):
        netAcc = []
        for i in range(len(y)):
            if expec[i] == 0 or y[i] == 0:
                y[i] += 1
                expec[i] += 1
                if y[i] > expec[i]:
                    nodeAcc = (1 - (y[i] / expec[i])) + 1
                else:
                    nodeAcc = y[i] / expec[i]
                y[i] -= 1
                expec[i] -= 1
            else:
                if y[i] > expec[i]:
                    nodeAcc = (1 - (y[i] / expec[i])) + 1
                else:
                    nodeAcc = y[i] / expec[i]
            netAcc.append(nodeAcc)
        acc = np.average(netAcc) * 100
        return acc


class Activation:
    # activation functions used to compute individual nodes
    # other functions are available (as far as activation functions go), but not yet implemented
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoidDerivation(self, x):
        return self.sigmoid(x) * (1 - self.sigmoid(x))

    def softmax(self, x):
        # inactive
        pass

    def softmaxDerivation(self, x):
        # inactive
        pass

    def relu(self, x):
        # active, but without derivation, it becomes useless
        return np.maximum(x, 0)

    def reluDerivation(self, x):
        # inactive
        pass


myNetwork = Network(xSize=len(inputX),
                    ySize=len(expecOutput),
                    hiddenLayers=hiddenUnits,
                    learningRate=learningRate,
                    actFunc=Activation().sigmoid)

weight = myNetwork.setWeights(myNetwork.layers, 1)
bias = myNetwork.setBias(myNetwork.layers, 1)

totalStart = time.time()
start = time.time()

for step in range(steps):
    output, weight, bias = myNetwork.train(inputX, weight, bias, expecOutput)
    if step % 100 == 1:
        print("Step", step)
        print("Total Error:", myNetwork.errorSum)
        print("---- Time Taken for Step: %f ----" % (time.time() - start), "\n")
        start = time.time()

accuracy = myNetwork.evalAccuracy(output, expecOutput)

weightNum = 0
for firstLen in range(len(weight)):
    for secondLen in range(len(weight[firstLen])):
        for thirdLen in range(len(weight[firstLen][secondLen])):
            weightNum += 1

print("Number of Weights: ", weightNum)
print("Expected output:", expecOutput)
print("Network output:", output)
print("Network accuracy: %f%%" % accuracy)
print("---- Time Taken Overall: %f ----" % (time.time() - totalStart))