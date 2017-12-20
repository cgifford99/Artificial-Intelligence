import os
import shutil
import sqlite3
import sys
import time
import urllib.request
import zipfile
from sqlite3 import Error

# username extraction (for flexibility)
currentUser = os.environ.get('USERNAME')

# corpus document location
docPath = 'C:\\Users\\%s\\Documents\\artificial intelligence\\BNC\\download\\Texts' % currentUser

# planned corpus location
corpusPath = 'C:\\Users\\%s\\Documents\\artificial intelligence' % currentUser

# data dictionaries
wordPOSCounts = {}
POSPOSCounts = {}
POSCounts = {}
transitionProb = {}
emissionProb = {}

previousPOS = ""

# training variables
learningRate = 0.05
trainingEpochs = 1000


def importCorpus(data):
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
    # Document/directory iteration and file parsing
    for i in range(len(os.listdir(docPath))):
        folderOne = os.listdir(docPath)[i]
        print("Parsing...", folderOne)

        for j in range(len(os.listdir("%s\\%s" % (docPath, folderOne)))):
            folderTwo = os.listdir("%s\\%s" % (docPath, folderOne))[j]

            for k in range(len(os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo)))):
                finalFile = os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo))[k]

                with open('%s\\%s\\%s\\%s' % (docPath, folderOne, folderTwo, finalFile),
                          encoding="utf-8") as currentFile:
                    for line in currentFile:
                        parseLine(line, data)


'''
    # Specified file parsing for debugging
    for k in range(len(os.listdir("%s\\%s\\%s" % (docPath, "a", "a0")))):
        finalFile = os.listdir("%s\\%s\\%s" % (docPath, "a", "a0"))[k]
        with open('%s\\%s\\%s\\%s' % (docPath, "a", "a0", "a00.xml"), encoding="utf-8") as currentFile:
            # print(finalFile)
            for line in currentFile:
                parseLine(line, data)
                    # print(lines)
'''


def parseLine(line, data):
    # use parsing techniques to extract POS tag and the words
    global previousPOS
    if line.find("<w ") == -1 or line.find("</w>") == -1:
        # if line.find("<c ") == -1 or line.find("</c>") == -1:
        return
    else:
        wordInfo = line[line.find("<w ") + 3:line.find("</w>")]
        currentPOS = wordInfo[wordInfo.find("c5=") + 4:wordInfo.find(" ") - 1]
        # if line.find("<c ") == -1 or line.find("</c>") == -1:
        # punctuation = line[line.find("<c ") + 3:line.find("</c>")]
        word = wordInfo[wordInfo.find(">") + 1:]
        if currentPOS == '' or word == '':
            if line.find("<w ") != -1:
                line = line[:line.find("<w ")]
                parseLine(line, data)
            elif line.find("</w>"):
                line = line[:line.find("</w>")]
                parseLine(line, data)
        else:
            data.execute("INSERT INTO pos_tags VALUES (?, ?);", (currentPOS, word))
            countData(wordPOSCounts, currentPOS, word)
            countData(POSPOSCounts, currentPOS, previousPOS)
            countData(POSCounts, currentPOS, "none")
            line = line[:line.find("<w ")] + line[line.find("</w>") + 4:]
            previousPOS = currentPOS
            parseLine(line, data)


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


def insertDB():
    global curPOS
    """
    for key in wordPOSCounts:
        count = wordPOSCounts[key]
        curPOS.execute('''INSERT INTO wordPOSCounts VALUES (?, ?)''', (key, count))
    for key in POSPOSCounts:
        count = POSPOSCounts[key]
        curPOS.execute('''INSERT INTO POSPOSCounts VALUES (?, ?)''', (key, count))
    for key in POSCounts:
        count = POSCounts[key]
        curPOS.execute('''INSERT INTO POSCounts VALUES (?, ?)''', (key, count))
    """
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


def probabilityOf(var1, var2):
    # var1 is the current POS
    # var2 is the previous POS
    # figure out classes in python
    data = curPOS.fetchall()
    for i in range(len(data)):
        if "var1[var2]" in data:
            print("Found our data!")


if __name__ == '__main__':
    print("Creating training data...")
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
        curPOS.execute('''CREATE TABLE if not exists pos_tags(tags, words)''')
        curPOS.execute('''CREATE TABLE if not exists wordPOSCounts(pos, count)''')
        curPOS.execute('''CREATE TABLE if not exists POSPOSCounts(pos, count)''')
        curPOS.execute('''CREATE TABLE if not exists POSCounts(pos, count)''')
        curPOS.execute('''CREATE TABLE if not exists transitionProb('currentPos, previousPos', probability)''')
        curPOS.execute('''CREATE TABLE if not exists emissionProb('word, currentPos', probability)''')
        print("Database created successfully!")
        # importCorpus(curPOS)
        print("Data created")
        # Need to generate a POS(POS)----(current POS(previous POS))----probability matrix first
        print("Generating transition probability matrix...")
        curPOS.execute('''SELECT * FROM POSPOSCounts''')
        POSPOSData = curPOS.fetchall()
        curPOS.execute('''SELECT * FROM POSCounts''')
        POSData = curPOS.fetchall()
        for i in range(len(POSPOSData)):
            POSPOSResult = POSPOSData[i]
            POSPOSParsed = (POSPOSResult[0][POSPOSResult[0].find("(") + 1:POSPOSResult[0].find(")")]).upper() + "(none)"
            for j in range(len(POSData)):
                if POSPOSParsed == POSData[j][0]:
                    POSResult = POSData[j][1]
                    break
                else:
                    POSResult = 0
            # print("POSPOSResult: ", POSPOSResult)
            # print("POSPOSParsed: ", POSPOSParsed)
            if POSResult == 0:
                # print("POS not found")
                continue
            # print("POSResult: ", POSResult)
            probResult = POSPOSResult[1]/POSResult
            transitionProb[POSPOSResult[0]] = probResult
            # print("%d, %d = %f\n" % (POSPOSResult[1], POSResult, probResult))

        print("Matrix created!")
        # Then generate a POS(word)----(current POS(current word))----probability matrix first
        print("Generating emission probability matrix...")
        curPOS.execute('''SELECT * FROM wordPOSCounts''')
        wordPOSData = curPOS.fetchall()
        for i in range(len(wordPOSData)):
            wordPOSResult = wordPOSData[i]
            wordPOSParsed = wordPOSResult[0][:wordPOSResult[0].find("(")] + "(none)"
            for j in range(len(POSData)):
                if wordPOSParsed == POSData[j][0]:
                    POSResult = POSData[j][1]
                    break
                else:
                    POSResult = 0
            # print("wordPOSResult: ", wordPOSResult)
            # print("wordPOSParsed: ", wordPOSParsed)
            if POSResult == 0:
                print("POS not found")
                continue
            # print("POSResult: ", POSResult)
            probResult = wordPOSResult[1] / POSResult
            emissionProb[wordPOSResult[0]] = probResult
            # print("%d, %d = %f\n" % (wordPOSResult[1], POSResult, probResult))

        print("Matrix created!")
        insertDB()
        connPOS.commit()
        connPOS.close()
        timeTaken = time.time() - start
        timeUnit = "seconds"
        if timeTaken >= 60:
            timeTaken /= 60
            timeUnit = "minutes"
        print("--- time taken: %f %s ---" % (timeTaken, timeUnit))