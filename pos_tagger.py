import os
import shutil
import sqlite3
from sqlite3 import Error
import sys
import time
import urllib.request
import zipfile

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
transitionProb = {}
emissionProb = {}
words = []
posRangeWord = []
posRangeSentence = []
pathProbArray = []
previousCellProbArray = []
cellProbArray = []
finalCellProb = []
maxFuncArgument = []
pathCellArray = []
finalPOS = []

previousPOS = "START"


# creating tables within database
def createDB():
    curPOS.execute('''CREATE TABLE if not exists pos_tags(tags, words)''')
    curPOS.execute('''CREATE TABLE if not exists wordPOSCounts(pos, count)''')
    curPOS.execute('''CREATE TABLE if not exists POSPOSCounts(pos, count)''')
    curPOS.execute('''CREATE TABLE if not exists POSCounts(pos, count)''')
    curPOS.execute('''CREATE TABLE if not exists transitionProb('currentPos, previousPos', probability)''')
    curPOS.execute('''CREATE TABLE if not exists emissionProb('word, currentPos', probability)''')


# downloads and unzips corpus if needed
def importCorpus():
    # download corpus and set for training
    if not os.path.exists(corpusPath + "\\BNC.zip"):
        print("Downloading corpus...")
        with urllib.request.urlopen('http://ota.ox.ac.uk/text/2554.zip') as response, open("BNC.zip",
                                                                                           "wb") as outputFile:
            shutil.copyfileobj(response, outputFile)
    else:
        print("Corpus exists. Will not download.")
    if not os.path.exists(corpusPath + "\\BNC"):
        print("Extracting corpus...")
        zipRef = zipfile.ZipFile(corpusPath + "\\BNC.zip", 'r')
        zipRef.extractall(corpusPath)
        zipRef.close()
        os.rename(corpusPath + "\\2554", corpusPath + "\\BNC")  # permission denied issues??
        print("Done!")
    else:
        print("Corpus previously unzipped. Will not continue.")


# parses corpus file-by-file, line-by-line
def parseCorpus():
    for dirOne in range(len(os.listdir(docPath))):
        folderOne = os.listdir(docPath)[dirOne]
        print("Parsing...", folderOne)

        for dirTwo in range(len(os.listdir("%s\\%s" % (docPath, folderOne)))):
            folderTwo = os.listdir("%s\\%s" % (docPath, folderOne))[dirTwo]

            for dirThree in range(len(os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo)))):
                finalFile = os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo))[dirThree]

                with open('%s\\%s\\%s\\%s' % (docPath, folderOne, folderTwo, finalFile),
                          encoding="utf-8") as currentFile:
                    for line in currentFile:
                        parseLine(line)


# parses individual lines in the current document
def parseLine(line):
    # use parsing techniques to extract POS tag and word
    global previousPOS
    if line.find("<w ") == -1 or line.find("</w>") == -1:
        if line.find("<c ") != -1 or line.find("<c ") != -1:
            previousPOS = "START"
        return
    else:
        wordInfo = line[line.find("<w ") + 3:line.find("</w>")]
        currentPOS = wordInfo[wordInfo.find("c5=") + 4:wordInfo.find(" ") - 1]
        word = wordInfo[wordInfo.find(">") + 1:]
        if currentPOS == '' or word == '':
            if line.find("<w ") != -1:
                line = line[:line.find("<w ")]
                parseLine(line)
            elif line.find("</w>"):
                line = line[:line.find("</w>")]
                parseLine(line)
        else:
            curPOS.execute("INSERT INTO pos_tags VALUES (?, ?);", (currentPOS, word))
            countData(wordPOSCounts, currentPOS, word)
            countData(POSPOSCounts, currentPOS, previousPOS)
            countData(POSCounts, currentPOS, "none")
            if previousPOS == "START":
                countData(POSCounts, previousPOS, "none")
            line = line[:line.find("<w ")] + line[line.find("</w>") + 4:]
            previousPOS = currentPOS
            parseLine(line)


def countData(countList, pos, word):
    if ' ' in word:
        word = word[:word.find(' ')]
    word = word.lower()
    newData = "%s(%s)" % (pos, word)
    if newData not in countList:
        count = 1
        countList[newData] = count
    else:
        newCount = countList[newData]
        newCount += 1
        countList[newData] = newCount


def insertDB(state):
    global curPOS
    if state == 0:
        for key in wordPOSCounts:
            count = wordPOSCounts[key]
            curPOS.execute('''INSERT INTO wordPOSCounts VALUES (?, ?)''', (key, count))
        for key in POSPOSCounts:
            count = POSPOSCounts[key]
            curPOS.execute('''INSERT INTO POSPOSCounts VALUES (?, ?)''', (key, count))
        for key in POSCounts:
            count = POSCounts[key]
            curPOS.execute('''INSERT INTO POSCounts VALUES (?, ?)''', (key, count))
    else:
        for key in transitionProb:
            prob = transitionProb[key]
            curPOS.execute('''INSERT INTO transitionProb VALUES (?, ?)''', (key, prob))
        for key in emissionProb:
            prob = emissionProb[key]
            curPOS.execute('''INSERT INTO emissionProb VALUES (?, ?)''', (key, prob))


def doesPathExist(path):
    if not os.path.exists(path):
        try:
            print("Attempting to create path...")
            os.mkdir(path)
            print("Path %s created" % path)
            doesPathExist(docPath)
        except FileNotFoundError:
            print("Error: Could not create path")
            path = os.path.dirname(path)
            doesPathExist(path)


def genEmissionProb(dictionary, data):
    curPOS.execute('''SELECT * FROM wordPOSCounts''')
    wordPOSData = curPOS.fetchall()
    for i in range(len(wordPOSData)):
        wordPOSResult = wordPOSData[i]
        wordPOSParsed = wordPOSResult[0][:wordPOSResult[0].find("(")] + "(none)"
        for j in range(len(data)):
            if wordPOSParsed == data[j][0]:
                POSResult = data[j][1]
                break
            else:
                POSResult = 0
        if POSResult == 0:
            print("POS not found")
            continue
        probResult = wordPOSResult[1] / POSResult
        dictionary[wordPOSResult[0]] = probResult


def genTransitionProb(dictionary, data):
    curPOS.execute('''SELECT * FROM POSPOSCounts''')
    POSPOSData = curPOS.fetchall()
    for i in range(len(POSPOSData)):
        POSPOSResult = POSPOSData[i]
        POSPOSParsed = (POSPOSResult[0][POSPOSResult[0].find("(") + 1:POSPOSResult[0].find(")")]).upper() + "(none)"
        for j in range(len(data)):
            if POSPOSParsed == data[j][0]:
                POSResult = data[j][1]
                break
            else:
                POSResult = 0
                continue
        probResult = POSPOSResult[1] / POSResult
        dictionary[POSPOSResult[0]] = probResult


def viterbi():
    global pathCellArray
    global maxFuncArgument
    global cellProbArray
    global pathProbArray
    for x in range(len(posRangeSentence)):
        for y in range(len(posRangeSentence[x])):
            formattedEmissionKey = "%s(%s)" % (posRangeSentence[x][y], words[x])
            for emissionKey in emissionProb:
                if formattedEmissionKey in emissionKey:
                    finalProbTwo = emissionProb[formattedEmissionKey]


            if x == 0:
                previousState = "start"
                formattedTransitionKey = "%s(%s)" % (posRangeSentence[x][y], previousState)
                finalProbOne = transitionProb[formattedTransitionKey]
                pathProbArray.append(finalProbOne * finalProbTwo)
            else:
                for prevY in range(len(posRangeSentence[x - 1])):
                    previousState = (posRangeSentence[x - 1][prevY])
                    formattedTransitionKey = "%s(%s)" % (posRangeSentence[x][y], previousState.lower())
                    for transitionKey in transitionProb:
                        if transitionKey == formattedTransitionKey:
                            finalProbOne = transitionProb[formattedTransitionKey]
                    pathCellArray.append(finalProbOne * finalProbTwo)
                pathProbArray.append(pathCellArray)
                pathCellArray = []

        if x == 0:
            finalCellProb.append(pathProbArray)
            previousCellProbArray = pathProbArray
            pathProbArray = []
        else:
            for a in range(len(pathProbArray)):
                for b in range(len(previousCellProbArray)):
                    argument1 = previousCellProbArray[b]
                    argument2 = pathProbArray[a][b]
                    maxFuncArgument.append(argument1 * argument2)
                cellProb = max(maxFuncArgument)
                cellProbArray.append(cellProb)
                maxFuncArgument = []
            previousCellProbArray = cellProbArray
            finalCellProb.append(cellProbArray)
            cellProbArray = []; pathProbArray = []


if __name__ == '__main__':
    start = time.time()
    print("Setting default directories...")

    # if path doesn't exist, create it
    doesPathExist(corpusPath)
    print("All paths exist!")

    # recursion limit too low for some documents within corpus; will return error otherwise
    sys.setrecursionlimit(4000)

    print("Creating database...")
    global connPOS
    try:
        connPOS = sqlite3.connect(corpusPath + "\\pos_training.db")
    except Error as e:
        print(e)
    finally:
        curPOS = connPOS.cursor()
        createDB()
        print("Database created successfully!")
        # importCorpus()
        # parseCorpus()
        print("Data created")
        # insertDB(0)

        curPOS.execute('''SELECT * FROM POSCounts''')
        POSData = curPOS.fetchall()

        print("Generating transition probability matrix...")
        genTransitionProb(transitionProb, POSData)
        print("Matrix created!")

        print("Generating emission probability matrix...")
        genEmissionProb(emissionProb, POSData)
        print("Matrix created!")

        # insertDB(1)

        currentSentence = input("Insert a sentence for part-of-speech tagging: ")
        words = currentSentence.lower().split()

        print("Calculating parts-of-speech....")
        for iterator in range(len(words)):
            for emissionKey in emissionProb:
                formattedWord = "(%s)" % words[iterator]
                if formattedWord in emissionKey:
                    emissionPOSKey = emissionKey[:emissionKey.find("(")]
                    posRangeWord.append(emissionPOSKey)
            posRangeSentence.append(posRangeWord)
            posRangeWord = []
        previousState = "start"
        viterbi()

        for a in range(len(finalCellProb)):
            maxVal = max(finalCellProb[a])
            maxIndex = finalCellProb[a].index(maxVal)
            finalPOS.append(posRangeSentence[a][maxIndex])

        print(finalPOS)
        connPOS.commit()
        connPOS.close()
        timeTaken = time.time() - start
        timeUnit = "seconds"
        if timeTaken >= 60:
            timeTaken /= 60
            timeUnit = "minutes"
        print("--- time taken: %f %s ---" % (timeTaken, timeUnit))