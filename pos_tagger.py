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

def importCorpus(): # download corpus and set for training
    # with open("parseData.txt", "w", encoding="utf-8") as parseData:
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
            os.rename(corpusPath + "\\2554", corpusPath + "\\BNC") # permission denied issues??
            print("Done!")
        else:
            print("Corpus already unzipped. Will not continue.")

        for i in range(len(os.listdir(docPath))):
            print("Parsing...")
            folderOne = os.listdir(docPath)[i]

            for j in range (len(os.listdir("%s\\%s" % (docPath, folderOne)))):
                folderTwo = os.listdir("%s\\%s" % (docPath, folderOne))[j]

                for k in range (len(os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo)))):
                    finalFile = os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo))[k]
                    conn.commit()

                    with open('%s\\%s\\%s\\%s' % (docPath, folderOne, folderTwo, finalFile), encoding="utf-8") as currentFile:
                        # parseData.write(finalFile + "\n")
                        print(finalFile)
                        # lines = 0
                        for line in currentFile:
                            # lines += 1
                            # parseData.write("%d\n" % lines)
                            parseFile(line)


def parseFile(line):
    # use parsing techniques to extract POS tag and the words
    if line.find("<w ") == -1 or line.find("</w>") == -1:
        return
    else:
        wordInfo = line[line.find("<w ") + 3:line.find("</w>")]
        pos = wordInfo[wordInfo.find("c5=") + 4:wordInfo.find(" ") - 1]
        word = wordInfo[wordInfo.find(">") + 1:]
        dbInsert(c, pos, word)
        line = line[:line.find("<w ")] + line[line.find("</w>") + 4:]
        parseFile(line)

def doesPathExist(path):
    if not os.path.exists(path):
        try:
            print("Attempting to create path...")
            os.mkdir(path)
            print("Path %s created" % path)
            doesPathExist(docPath)
        except:
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
    global conn
    try:
        conn = sqlite3.connect(corpusPath + "\\pos_training.db")
    except Error as e:
        print(e)
    finally:
        c = conn.cursor()
        c.execute('''CREATE TABLE if not exists pos_tags(tags, words)''')
        importCorpus()
        conn.close()
        print("Done!")
        print("--- time taken: %f seconds ---" % (time.time() - start))