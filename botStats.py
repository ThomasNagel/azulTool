class botStats:
    WALL_WIDTH = 5
    DATAPOINT_AMOUNT_SCORE_INPUT = 2

    def __init__ (self, idNum):
        self.idNum = idNum

        #game referee data
        self.roundData = list()

        #game results storage
        self.scores = list()
        self.computationTime = list()
        self.numBlocksPlaced = list()

        self.computationTimeOut = False
        self.encounteredError = False

    def cleanUp(self):
        del self.roundData

    def processGameData(self, gameData):
        #self.inputList = [(gameData['outputs']['referee'][i], gameData['summaries'][i]) for i in range(len(gameData['outputs']['referee']))]
        inputList = [(gameData['outputs']['referee'][i], gameData['summaries'][i]) for i in range(len(gameData['outputs']['referee']))]
        
        for tup in inputList:
            if tup[1] == "Tiles are drawn from the bag and placed on the factory displays.\n":
                #new round
                self.roundData.append(list())

            elif "The final score is:" in tup[1]:
                self.roundData.append([tup]) 

            elif len(tup[0]) != 0 and f'${self.idNum}' in tup[1]:
                #new move
                self.roundData[-1].append(tup)

    def checkTimeOut(self):
        for round in self.roundData:
            for tup in round:
                for sentence in tup[1].split('.\n'):
                    if "took too long to compute their move." in sentence and f'${self.idNum}' in sentence:
                        self.computationTimeOut = True
                        
                        return True

    def getScores(self):
        for round in self.roundData:
            tup = round[-1]

            #Get the final score
            if len(tup[0]) == 0:
                #find the sentence with the scores
                for sentence in tup[1].split('.\n'):
                    if "The final score is:" in sentence:
                        scoreSentence = sentence.split(' ')

                if scoreSentence[7] == f'${self.idNum}':
                    self.scores.append(int(scoreSentence[4]))
                else:
                    self.scores.append(int(scoreSentence[9]))

                break

            lines = tup[0].replace('> ', '').split('\r\n')

            #Loop through lines to find line with the score
            prevLine = ["NoLine"]
            for line in lines:
                dataPoint = line.split(" ")

                if len(prevLine) == self.WALL_WIDTH and len(dataPoint) == self.DATAPOINT_AMOUNT_SCORE_INPUT:
                    self.scores.append(int(dataPoint[1]))
                    break

                prevLine = dataPoint
        
if __name__ == "__main__":
    #debugging only
    import json

    with open("runnerOut92.json", "r") as f:
        testData = json.load(f)

    bot = botStats(0)
    bot.processGameData(testData)
    bot.getScores()
    bot.cleanUp()
    print(bot.scores)
