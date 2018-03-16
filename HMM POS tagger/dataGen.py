import os, urllib, shutil, zipfile, string, re, parser
from urllib import request
from string import punctuation

class Word(object):

    punctuation = string.punctuation

    def __init__(self, currentWord, currentTag, previousWord, previousTag):
        self.currentWord = currentWord
        self.currentTag = currentTag
        self.previousWord = previousWord
        if self.previousWord in punctuation:
            self.previousTag = "START"
        else:
            self.previousTag = previousTag

class Corpus:

    def __init__(self):
        self.corpPath = 'C:\\Users\\%s\\Documents\\artificial intelligence' % self.getUser()
        self.docPath = self.corpPath + "\\BNC\\download\\Texts"
        self.pathCheck(self.corpPath)
        self.pathCheck(self.docPath)
        self.currentUser = self.getUser()

    @staticmethod
    def getUser():
        user = os.environ.get('USERNAME')
        return user

    def pathCheck(self, path):
        if not os.path.exists(path):
            try:
                print("Attempting to create path...")
                os.mkdir(path)
                print("Path %s created" % path)
                self.pathCheck(path)
            except FileNotFoundError:
                print("Error: Directory not found. Recursion initiated")
                path = os.path.dirname(path)
                self.pathCheck(path)

    def __import__(self):
        print("Downloading corpus...")
        with urllib.request.urlopen('http://ota.ox.ac.uk/text/2554.zip') as response, open("BNC.zip","wb") as outputFile:
            shutil.copyfileobj(response, outputFile)
        print("Extracting corpus...")
        zipRef = zipfile.ZipFile(self.corpPath + "\\BNC.zip", 'r')
        zipRef.extractall(self.corpPath)
        zipRef.close()
        os.rename(self.corpPath + "\\2554", self.corpPath + "\\BNC")  # permission denied issues??
        print("Done!")

    def iterDocs(self):
        for dirPath, dirNames, fileNames in os.walk(self.docPath):
            if fileNames:
                for fileName in fileNames:
                    # print("FileName", fileName)
                    with open(os.path.join(dirPath, fileName), encoding="utf-8") as file:
                        for line in file:
                            self.parse(line)

    def parse(self, line):
        tags = ["<w ", "</w>", "<c ", "</c>"]
        if -1 == map(line.find, tags):
            return
        else:
            re.search(r"/a/")




    """
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
                countData(wordPOSCounts, currentPOS, word)
                countData(POSPOSCounts, currentPOS, previousPOS)
                countData(POSCounts, currentPOS, "none")
                if previousPOS == "START":
                    countData(POSCounts, previousPOS, "none")
                line = line[:line.find("<w ")] + line[line.find("</w>") + 4:]
                previousPOS = currentPOS
                parseLine(line)
    """


    def createData(self):
        try:
            self.parse(self.iterDocs())
        except FileNotFoundError:
            print("Error: Files not found.")
            self.__import__()
            self.createData()

Corpus().createData()