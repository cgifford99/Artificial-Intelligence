import numpy as np

""" For future reference. It's awesome, but extremely difficult with what little knowledge I have
possibleStates = ["sunny", "rainy", "cloudy", "windy", "snowy", "foggy"]
obsrvs = ["temperature", "humidity", "dew_point", "barometric_pressure", "wind_speed"]
obsrvsLikelihood = 
"""

possibleStates = ["sunny", "cloudy", "stormy"]
weatherCond = ["sunny", "cloudy", "rainy"]
observsLikelihood = np.array([[0.8, 0.1, 0.1],
                              [0.2, 0.6, 0.2],
                              [0.1, 0.1, 0.8]])
weatherProb = np.array([[],
                        [],
                        []])
initialStateProb = [0.3, 0.6, 0.1]
weatherProbConvert = np.array([])
# Percentage of clouds covering the sky
observs = np.random.uniform()