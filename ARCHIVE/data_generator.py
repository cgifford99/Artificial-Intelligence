import tensorflow as tf
import os
import sys
import csv

class Data:
    currentUser = os.environ.get('USERNAME')

    dataUrl = "http://ota.ox.ac.uk/text/2554.zip"
    basePath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence' % currentUser
    dataPath = 'C:\\Users\\%s\\PycharmProjects\\artificial intelligence\\datasets\\2554\\download\\texts' % currentUser

    trainFiles = ["A0A.xml", "A0B.xml", "A0C.xml", "A0D.xml", "A0E.xml", "A0F.xml", "A0G.xml", "A0H.xml", "A0J.xml",
                  "A0K.xml", "A0L.xml", "A0M.xml", "A0N.xml", "A0P.xml", "A0R.xml", "A0S.xml", "A0T.xml", "A0U.xml",
                  "A0V.xml", "A0W.xml", "A0X.xml", "A0Y.xml"]
    # trainFiles = ["A0A.xml", "A0B.xml", "A0C.xml", "A0D.xml"]
    trainName = 'training.csv'

    testFiles = ["A00.xml", "A01.xml", "A02.xml", "A03.xml", "A04.xml", "A05.xml", "A06.xml", "A07.xml", "A08.xml"]
    # testFiles = ["A00.xml"]
    testName = 'testing.csv'

    parsedLine = []

    sentEnd = [".", "?", "!"]
    sentArr = []

    def pathExist(self, path):
        if not os.path.exists(path):
            try:
                print("Attempting to create path...")
                os.mkdir(path)
                print("Path %s created" % path)
                self.pathExist(self.dataPath)
            except FileNotFoundError:
                print("Error: Could not create path")
                path = os.path.dirname(path)
                self.pathExist(path)
        else:
            return True

    def getDataPath(self, url):
        # download file from url to basePath
        if self.pathExist(self.dataPath):
            return self.dataPath
        else:
            return tf.keras.utils.get_file(fname="BNC", origin=url, extract=True,
                                           cache_dir=self.basePath)  # does this return proper pathname?

    def getFiles(self, path, priorPaths):
        trainFile = []
        testFile = []
        for i in range(len(priorPaths)):
            for file in os.listdir(os.path.join(path, priorPaths[i][0], priorPaths[i])):
                if file[2].isalpha():
                    trainFile.append(file)
                elif file[2].isdigit():
                    testFile.append(file)

        return trainFile, testFile

    def parseCorpus(self, path, files, filePaths, dataFile):
        with open(os.path.join(self.basePath, dataFile), 'w+', newline='') as csvfile:
            _writer = csv.writer(csvfile)
            _writer.writerow(["featureTag-2", "featureTag-1", "featureTag1", "featureTag2", "labelTag"])
            for k in range(len(filePaths)):
                for fileName in files:
                    if int(fileName[1]) == k:
                        with open(os.path.join(path, filePaths[k][0], filePaths[k], fileName), encoding="utf-8") as file:
                            print(fileName)
                            for line in file:
                                self.parseLine(line)
                                if self.parsedLine:
                                    self.parsedLine.append(["none", "none"])
                                    self.parsedLine.append(["none", "none"])
                                    for i in range(len(self.parsedLine)):
                                        if self.parsedLine[i][1] != "none":
                                            currentTag = self.parsedLine[i][1]
                                            futureOneTag = self.parsedLine[i + 1][1]
                                            futureTwoTag = self.parsedLine[i + 2][1]
                                            prevTwoTag = self.parsedLine[i - 2][1]
                                            prevOneTag = self.parsedLine[i - 1][1]

                                            features = [prevTwoTag, prevOneTag, futureOneTag, futureTwoTag, currentTag]
                                            _writer.writerow(features)

                                    self.parsedLine = [["none", "none"], ["none", "none"]]

    def parseLine(self, line):
        # features = []
        if line.find("<") != -1 and line.find(">") != -1 and line.find("<") < line.find(">"):
            tagName = line[line.find("<"):line.find(">") + 1]
            if tagName.find("<w ") != -1:
                wordInfo = line[line.find("<w ") + 3:line.find("</w>")]
                currentPOS = wordInfo[wordInfo.find("c5=") + 4:wordInfo.find(" ") - 1]
                word = wordInfo[wordInfo.find(">") + 1:]
                if ' ' in word:
                    word = word[:-1]
                parsedWord = [word, currentPOS]
                self.parsedLine.append(parsedWord)
                line = line[:line.find("<w ")] + line[line.find("</w>") + 4:]
                self.parseLine(line)
            elif tagName.find("<c ") != -1:
                puncInfo = line[line.find("<c ") + 3:line.find("</c>")]
                punctuation = puncInfo[puncInfo.find(">") + 1:]
                puncPOS = puncInfo[puncInfo.find("c5=") + 4:puncInfo.find('>') - 1]
                parsedPunc = [punctuation, puncPOS]
                self.parsedLine.append(parsedPunc)
                line = line[:line.find("<c ")] + line[line.find("</c>") + 4:]
                self.parseLine(line)
            else:
                line = line[:line.find("<")] + line[line.find(">") + 1:]
                self.parseLine(line)
        else:
            return

    # What does our feature list look like?
    # n-2 tag feature
    # n-1 tag feature
    # n+1 tag feature
    # n+2 tag feature
    # n   tag label

    def generate(self):

        sys.setrecursionlimit(4000)

        if self.pathExist(self.basePath):
            print("Path exists!")

            if not self.pathExist(self.dataPath):
                self.dataPath = self.getDataPath(self.dataUrl)
                print(self.dataPath)

            print("Corpus downloaded")
            self.filePaths = ["A0"]
            self.trainFiles, self.testFiles = self.getFiles(self.dataPath, self.filePaths)

            self.parseCorpus(self.dataPath, self.trainFiles, self.filePaths, self.trainName)
            self.parseCorpus(self.dataPath, self.testFiles, self.filePaths, self.testName)



if __name__ == '__main__':
    Data().generate()