import os
import time
import sys
import re
import sqlite3

# Alright, this program works flawlessly with 1 sentence that I know of. Otherwise it crashes ;)
# I am leaving the program to die unfortunately as I have no desire to continue working on it until I learn more about viterbi
# - CG 2/11/19

# planned corpus location
corpusPath = os.path.dirname(sys.argv[0])
print(corpusPath)

# corpus document location
docPath = os.path.join(corpusPath, '\\BNC\\download\\Texts')

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
    matchNotFound = True
    for x in range(len(sentTagRange)):
        for y in range(len(sentTagRange[x])):
            formEmissionKey = "%s(%s)" % (sentTagRange[x][y], words[x])
            for emissionKey in emisProb:
                if formEmissionKey in emissionKey:
                    finalProbTwo = emisProb[formEmissionKey]
                    matchNotFound = True
                    break
                else:
                    matchNotFound = False
            if not matchNotFound:
                print("I cannot recognize the word: %s" % words[x])
                finalCellProb.append("UNC")
                break

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
            cellProbArray = []
            pathProbArray = []


if __name__ == '__main__':
    start = time.time()

    global conn
    try:
        conn = sqlite3.connect(corpusPath + "\\pos_training.db")
    except sqlite3.Error as e:
        print(e)
    finally:
        cur = conn.cursor()
        cur.execute("SELECT * FROM transitionProb")
        transProbArr = cur.fetchall()
        reformatArr(transProbArr, transProb)

        cur.execute("SELECT * FROM emissionProb")
        emisProbArr = cur.fetchall()
        reformatArr(emisProbArr, emisProb)

    sentence = input("Insert a sentence for part-of-speech tagging: ")
    words = re.findall(r"[\w']+|[!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]", sentence)

    print("Calculating parts-of-speech....")
    for index in range(len(words)):
        words[index] = words[index].lower()
        for emissionKey in emisProb:
            formWord = "(%s)" % words[index]
            if formWord in emissionKey:
                emissionPOSKey = emissionKey[:emissionKey.find("(")]
                wordTagRange.append(emissionPOSKey)
        if not wordTagRange:
            wordTagRange.append("UNC")
        sentTagRange.append(wordTagRange)
        wordTagRange = []
    previousState = "start"
    viterbi()

    for index in range(len(finalCellProb)):
        maxVal = max(finalCellProb[index])
        maxIndex = finalCellProb[index].index(maxVal)
        tagSeq.append(sentTagRange[index][maxIndex])

    tagSent = ''
    for index in range(len(tagSeq)):
        tagWord = "%s[%s] " % (words[index], tagSeq[index])
        tagSent += tagWord
    print(tagSent)
    timeTaken = time.time() - start
    convertedTime = time.strftime("%H:%M:%S", time.gmtime(timeTaken))
    print("--- Time taken: %s ---\n" % convertedTime)
    input("Hit enter to close the window...")
