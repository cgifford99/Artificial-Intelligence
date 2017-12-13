import os
import urllib.request
import shutil
import zipfile
import sys
import time
import sqlite3
from sqlite3 import Error


def dbInsert(c, tag, word):
    c.execute("INSERT INTO pos_tags VALUES (?, ?);", (tag, word))


def importCorpus(data):  # download corpus and set for training
    if not os.path.exists(corpusPath + "\\BNC.zip"):
        print("Downloading corpus...")
        with urllib.request.urlopen('http://ota.ox.ac.uk/text/2554.zip') as response, open("BNC.zip", "wb") as outputFile:
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
    for i in range(len(os.listdir(docPath))):
        folderOne = os.listdir(docPath)[i]
        print("Parsing...", folderOne)
        connPOS.commit()

        for j in range(len(os.listdir("%s\\%s" % (docPath, folderOne)))):
            folderTwo = os.listdir("%s\\%s" % (docPath, folderOne))[j]

            for k in range(len(os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo)))):
                finalFile = os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo))[k]

                with open('%s\\%s\\%s\\%s' % (docPath, folderOne, folderTwo, finalFile), encoding="utf-8") as currentFile:
                    # lines = 1
                    # print(finalFile)
                    for line in currentFile:
                        parseLine(line, data)
                        # print(lines)
                        # lines += 1

"""    for k in range(len(os.listdir("%s\\%s\\%s" % (docPath, "a", "a1")))):
        finalFile = os.listdir("%s\\%s\\%s" % (docPath, "a", "a1"))[k]

        with open('%s\\%s\\%s\\%s' % (docPath, "a", "a1", finalFile), encoding="utf-8") as currentFile:
            # print(finalFile)
            for line in currentFile:
                parseLine(line, data)
                # print(lines)
"""


def parseLine(line, data):
    # use parsing techniques to extract POS tag and the words
    # print(line)
    global wordNum
    if line.find("<w ") == -1 or line.find("</w>") == -1:
        return
    else:
        wordInfo = line[line.find("<w ") + 3:line.find("</w>")]
        pos = wordInfo[wordInfo.find("c5=") + 4:wordInfo.find(" ") - 1]
        word = wordInfo[wordInfo.find(">") + 1:]
        if pos == '' or word == '':
            if line.find("<w ") != -1:
                line = line[:line.find("<w ")]
                parseLine(line, data)
            elif line.find("</w>"):
                line = line[:line.find("</w>")]
                parseLine(line, data)
        else:
            dbInsert(data, pos, word)
            countWords(wordCounts, pos, word)
            line = line[:line.find("<w ")] + line[line.find("</w>") + 4:]
            wordNum += 1
            parseLine(line, data)


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


def countWords(countList, pos, word):
    # select a word in pos_tags db
    # if word not in count_words db
        # insert into db
    # if word in count_words db
        # find row number of word
        # find current value of word count
        # +1 to current value
    # output: "'s ",
    # extra output: "n't ",
    # create a list of counts, then input list into database
    if ' ' in word:
        word = word[:word.find(' ')]
    word = word.lower()
    newWord = "%s[%s]" % (pos, word)
    if newWord not in countList:
        count = 1
        countList[newWord] = count
    else:
        newCount = countList[newWord]
        newCount += 1
        countList[newWord] = newCount


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
        print("Database created successfully!")
        curPOS = connPOS.cursor()
        curPOS.execute('''CREATE TABLE if not exists pos_tags(tags, words)''')
        # curPOS.execute('''CREATE TABLE if not exists counts(words, counts)''')
        # curPOS.execute('''SELECT pos_tags.words, counts.words, counts.counts FROM counts ''')
        # curPOS.execute('''BEGIN TRANSACTION''')
        wordCounts = {}
        wordNum = 0
        importCorpus(curPOS)
        print(wordNum)
        # for data in range(len(posData)):
        #    print(posData[data])
        # curPOS.execute('''END TRANSACTION''')
        connPOS.close()
        print("Done!")
        print("--- time taken: %f seconds ---" % (time.time() - start))