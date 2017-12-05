import os
import urllib.request
import shutil
import zipfile
import sqlite3
from sqlite3 import Error
# this works, but unless you have 1TB of RAM, it doesn't....don't try, I'm fixing it.....

""" create database
def dbConnect(dbFile):
    try:
        conn = sqlite3.connect(dbFile)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        conn.close()
"""

def importCorpus(): # download corpus and set for training
    if os.path.exists(corpusPath + "\\BNC.zip") != True:
        print("Downloading corpus...")
        with urllib.request.urlopen('http://ota.ox.ac.uk/text/2554.zip') as response, open("BNC.zip", "wb") as outputFile:
            shutil.copyfileobj(response, outputFile)
    else:
        print("Path exists. Will not download.")
    if os.path.exists(corpusPath + "\\BNC") != True:
        print("Extracting corpus...")
        zipRef = zipfile.ZipFile(corpusPath + "\\BNC.zip", 'r')
        zipRef.extractall(corpusPath)
        zipRef.close()
        os.rename(corpusPath + "\\2554", corpusPath + "\\BNC")
        print("Done!")
    else:
        print("File extracted. Will not extract.")

    for i in range(len(os.listdir(docPath))):
        print("Parsing...")
        folderOne = os.listdir(docPath)[i]

        for j in range (len(os.listdir("%s\\%s" % (docPath, folderOne)))):
            folderTwo = os.listdir("%s\\%s" % (docPath, folderOne))[j]

            for k in range (len(os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo)))):
                finalFile = os.listdir("%s\\%s\\%s" % (docPath, folderOne, folderTwo))[k]

                with open('%s\\%s\\%s\\%s' % (docPath, folderOne, folderTwo, finalFile), encoding="utf-8") as currentFile:
                    with open("parseData.txt", "w", encoding="utf-8") as parseData:
                        for line in currentFile:
                            parseFile(line, parseData)


def parseFile(line, parseData):
    # use parsing techniques to extract POS tag and the words
    if line.find("<w ") == -1:
        return
    else:
        wordInfo = line[line.find("<w ") + 3:line.find("</w>")]
        pos = wordInfo[wordInfo.find("c5=") + 4:wordInfo.find(" ") - 1]
        word = wordInfo[wordInfo.find(">") + 1:]
        parseData.write(pos)
        parseData.write(word + "\n")
        line = line[:line.find("<w ")] + line[line.find("</w>")+4:]
        parseFile(line, parseData)

if __name__ == '__main__':
    print("Setting default directories...")
    currentUser = os.environ.get('USERNAME')
    docPath = 'C:\\Users\\%s\\Documents\\artificial intelligence\\BNC\\download\\Texts' % currentUser
    corpusPath = 'C:\\Users\\%s\\Documents\\artificial intelligence' % currentUser
    # dbConnect(corpusPath + "\\%s" % dbFile) yo future me, you're making a database to put words and their pos into. Cool. Have a good day
    importCorpus()
    print("Done!")