import os
import time
import sqlite3
from sqlite3 import Error

# username extraction (for flexibility)
currentUser = os.environ.get('USERNAME')

# corpus document location
docPath = 'C:\\Users\\%s\\Documents\\artificial intelligence\\BNC\\download\\Texts' % currentUser

# planned corpus location
corpusPath = 'C:\\Users\\%s\\Documents\\artificial intelligence' % currentUser

# data dictionaries/arrays
wordPOSCounts = {}
POSPOSCounts = {}
POSCounts = {}
transProb = {}
emisProb = {}
words = []
wordTagRange = []
sentTagRange = []
pathProbArray = []
prevCellProbArr = []
cellProbArray = []
finalCellProb = []
maxFuncArg = []
pathCellArray = []
tagSeq = []


def reformatArr(array, dictionary):
    for i in range(len(array)):
        dictionary[array[i][0]] = array[i][1]


def viterbi():
    global pathCellArray
    global maxFuncArg
    global cellProbArray
    global pathProbArray
    global finalCellProb
    for x in range(len(sentTagRange)):
        for y in range(len(sentTagRange[x])):
            formEmissionKey = "%s(%s)" % (sentTagRange[x][y], words[x])
            for emissionKey in emisProb:
                if formEmissionKey in emissionKey:
                    finalProbTwo = emisProb[formEmissionKey]


            if x == 0:
                previousState = "start"
                formTransKey = "%s(%s)" % (sentTagRange[x][y], previousState)
                finalProbOne = transProb[formTransKey]
                pathProbArray.append(finalProbOne * finalProbTwo)
            else:
                for prevY in range(len(sentTagRange[x - 1])):
                    previousState = (sentTagRange[x - 1][prevY])
                    formTransKey = "%s(%s)" % (sentTagRange[x][y], previousState.lower())
                    for transKey in transProb:
                        if transKey == formTransKey:
                            finalProbOne = transProb[formTransKey]
                    pathCellArray.append(finalProbOne * finalProbTwo)
                pathProbArray.append(pathCellArray)
                pathCellArray = []

        if x == 0:
            finalCellProb.append(pathProbArray)
            prevCellProbArr = pathProbArray
            pathProbArray = []
        else:
            for a in range(len(pathProbArray)):
                for b in range(len(prevCellProbArr)):
                    arg1 = prevCellProbArr[b]
                    arg2 = pathProbArray[a][b]
                    maxFuncArg.append(arg1 * arg2)
                cellProb = max(maxFuncArg)
                cellProbArray.append(cellProb)
                maxFuncArg = []
            prevCellProbArr = cellProbArray
            finalCellProb.append(cellProbArray)
            cellProbArray = []; pathProbArray = []


if __name__ == '__main__':
    start = time.time()

    global conn
    try:
        conn = sqlite3.connect(corpusPath + "\\pos_training.db")
    except Error as e:
        print(e)
    finally:
        cur = conn.cursor()
        cur.execute("SELECT * FROM transitionProb")
        transProbArr = cur.fetchall()
        reformatArr(transProbArr, transProb)

        cur.execute("SELECT * FROM emissionProb")
        emisProbArr = cur.fetchall()
        reformatArr(emisProbArr, emisProb)

    currentSentence = input("Insert a sentence for part-of-speech tagging: ")
    words = currentSentence.lower().split()

    print("Calculating parts-of-speech....")
    for iterator in range(len(words)):
        for emissionKey in emisProb:
            formWord = "(%s)" % words[iterator]
            if formWord in emissionKey:
                emissionPOSKey = emissionKey[:emissionKey.find("(")]
                wordTagRange.append(emissionPOSKey)
        sentTagRange.append(wordTagRange)
        wordTagRange = []
    previousState = "start"
    print(sentTagRange)
    viterbi()

    for a in range(len(finalCellProb)):
        maxVal = max(finalCellProb[a])
        maxIndex = finalCellProb[a].index(maxVal)
        tagSeq.append(sentTagRange[a][maxIndex])

    print(tagSeq)
    timeTaken = time.time() - start
    timeUnit = "seconds"
    if timeTaken >= 60:
        timeTaken /= 60
        timeUnit = "minutes"
    print("--- time taken: %f %s ---" % (timeTaken, timeUnit))