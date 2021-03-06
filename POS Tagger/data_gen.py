import sqlite3
from sqlite3 import Error
import sys
import os
import urllib.request
import zipfile
import time

# TBH This program actually works very well. Good job - CG 2/11/19

# planned corpus location
corpusPath = os.path.dirname(sys.argv[0])
print(corpusPath)

# corpus document location
docPath = os.path.join(corpusPath, 'BNC/download/Texts')

# data dictionaries/arrays
wordPOSCounts = {}
POSPOSCounts = {}
POSCounts = {}
transitionProb = {}
emissionProb = {}

previousPOS = "START"

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


# creating tables within database
def createDB():
    # curPOS.execute('''CREATE TABLE if not exists pos_tags(tags, words)''')
    curPOS.execute('''CREATE TABLE if not exists wordPOSCounts(pos, count)''')
    curPOS.execute('''CREATE TABLE if not exists POSPOSCounts(pos, count)''')
    curPOS.execute('''CREATE TABLE if not exists POSCounts(pos, count)''')
    curPOS.execute('''CREATE TABLE if not exists transitionProb('currentPos, previousPos', probability)''')
    curPOS.execute('''CREATE TABLE if not exists emissionProb('word, currentPos', probability)''')


def insertDB():
    for key in wordPOSCounts:
        count = wordPOSCounts[key]
        curPOS.execute('''INSERT INTO wordPOSCounts VALUES (?, ?)''', (key, count))
    for key in POSPOSCounts:
        count = POSPOSCounts[key]
        curPOS.execute('''INSERT INTO POSPOSCounts VALUES (?, ?)''', (key, count))
    for key in POSCounts:
        count = POSCounts[key]
        curPOS.execute('''INSERT INTO POSCounts VALUES (?, ?)''', (key, count))
    for key in transitionProb:
        prob = transitionProb[key]
        curPOS.execute('''INSERT INTO transitionProb VALUES (?, ?)''', (key, prob))
    for key in emissionProb:
        prob = emissionProb[key]
        curPOS.execute('''INSERT INTO emissionProb VALUES (?, ?)''', (key, prob))


# downloads and unzips corpus if needed
def importCorpus():
    # download corpus and set for training
    if not os.path.exists(corpusPath + "\\BNC.zip") or not os.path.exists(docPath + "\\K\\KS\\KSW.xml"):
        urllib.request.urlretrieve('http://ota.ox.ac.uk/text/2554.zip', "BNC.zip", reporthook)
    else:
        print("Corpus exists. Will not download.")
    if not os.path.exists(corpusPath + "\\BNC"):
        print("\nExtracting corpus...")
        zipRef = zipfile.ZipFile(corpusPath + "\\BNC.zip", 'r')
        zipInfo = zipRef.getinfo(zipRef.filename)
        print(zipInfo)
        zipRef.extractall(corpusPath)
        zipRef.close()
        os.rename(corpusPath + "\\2554", corpusPath + "\\BNC") # permission denied issues?? 2/11/19 UPDATE: Nah
        print("Done!")
    else:
        print("Corpus previously unzipped. Will not continue.")


# Thanks to https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
def reporthook(count, blockSize, totalSize):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * blockSize)
    speed = int(progress_size / (1024 * duration + 0.000001))
    percent = min(int(count*blockSize*100/totalSize),100)
    sys.stdout.write("\r%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

def parseCorpus():
    print(docPath)
    for dirPath, dirNames, fileNames in os.walk(docPath):
            for fileName in fileNames:
                sys.stdout.write("\rParsing file %s" % fileName)
                sys.stdout.flush()
                with open(os.path.join(dirPath, fileName), encoding="utf-8") as file:
                    for line in file:
                        parseLine(line)
                    file.close()

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
            # curPOS.execute("INSERT INTO pos_tags VALUES (?, ?);", (currentPOS, word))
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


def genEmissionProb(dictionary, posData):
    for i in wordPOSCounts:
        wordPOSCount = wordPOSCounts[i]
        wordPOSFormatted = (i[:i.find("(")]).upper() + "(none)"
        for j in posData:
            if wordPOSFormatted == j:
                POSResult = posData[j]
                break
            else:
                POSResult = 0
                continue
        probResult = wordPOSCount / POSResult
        dictionary[i] = probResult


def genTransitionProb(dictionary, posData):
    for i in POSPOSCounts:
        POSPOSCount = POSPOSCounts[i]
        POSPOSFormatted = (i[i.find("(") + 1:i.find(")")]).upper() + "(none)"
        for j in posData:
            if POSPOSFormatted == j:
                POSResult = posData[j]
                break
            else:
                POSResult = 0
                continue
        probResult = POSPOSCount / POSResult
        dictionary[i] = probResult



if __name__ == '__main__':
    start = time.time()

    # if path doesn't exist, create it
    print("Setting default directories...")
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
        importCorpus()
        parseCorpus()

        print("\nGenerating transition probability matrix...")
        genTransitionProb(transitionProb, POSCounts)
        print("Matrix created!")

        print("Generating emission probability matrix...")
        genEmissionProb(emissionProb, POSCounts)
        print("Matrix created!")

        insertDB()
        connPOS.commit()
        connPOS.close()
        print("Data created")
        timeTaken = time.time() - start
        convertedTime = time.strftime("%H:%M:%S", time.gmtime(timeTaken))
        print("--- Time taken: %s ---" % convertedTime)