import os
import shutil
import sqlite3
import sys
import time
import urllib.request
import zipfile
from sqlite3 import Error


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
    """
    # Specified file parsing for debugging
    for k in range(len(os.listdir("%s\\%s\\%s" % (docPath, "a", "a1")))):
        finalFile = os.listdir("%s\\%s\\%s" % (docPath, "a", "a1"))[k]

        with open('%s\\%s\\%s\\%s' % (docPath, "a", "a1", finalFile), encoding="utf-8") as currentFile:
            # print(finalFile)
            for line in currentFile:
                parseLine(line, data)
                # print(lines)
    """


def parseLine(line, data):
    # use parsing techniques to extract POS tag and the words
    global previousPOS
    if line.find("<w ") == -1 or line.find("</w>") == -1:
        return
    else:
        wordInfo = line[line.find("<w ") + 3:line.find("</w>")]
        currentPOS = wordInfo[wordInfo.find("c5=") + 4:wordInfo.find(" ") - 1]
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
            line = line[:line.find("<w ")] + line[line.find("</w>") + 4:]
            previousPOS = currentPOS
            parseLine(line, data)


def countData(countList, pos, word):
    if ' ' in word:
        word = word[:word.find(' ')]
    word = word.lower()
    newData = "%s[%s]" % (pos, word)
    if newData not in countList:
        count = 1
        countList[newData] = count
    else:
        newCount = countList[newData]
        newCount += 1
        countList[newData] = newCount


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


if __name__ == '__main__':
    start = time.time()
    print("Setting default directories...")
    # grabbing the username for more flexibility
    currentUser = os.environ.get('USERNAME')

    # if path doesn't exist, create it
    docPath = 'C:\\Users\\%s\\Documents\\artificial intelligence\\BNC\\download\\Texts' % currentUser
    doesPathExist(docPath)
    corpusPath = 'C:\\Users\\%s\\Documents\\artificial intelligence' % currentUser
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
        curPOS.execute('''CREATE TABLE if not exists wordPOSCounts(pos[word], count)''')
        curPOS.execute('''CREATE TABLE if not exists POSPOSCounts(pos[pos], count)''')
        print("Database created successfully!")
        wordPOSCounts = {}
        POSPOSCounts = {}
        previousPOS = ""
        importCorpus(curPOS)
        for key in wordPOSCounts:
            data = key
            count = wordPOSCounts[key]
            curPOS.execute('''INSERT INTO wordPOSCounts VALUES (?, ?)''', (data, count))
        for key in POSPOSCounts:
            data = key
            count = POSPOSCounts[key]
            curPOS.execute('''INSERT INTO POSPOSCounts VALUES (?, ?)''', (data, count))
        connPOS.commit()
        connPOS.close()
        print("Done!")
        print("--- time taken: %f seconds ---" % (time.time() - start))
