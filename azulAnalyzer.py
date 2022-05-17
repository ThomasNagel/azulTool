import concurrent.futures
import json
import subprocess
import os

import botStats

from botStats import botStats

def runAzul(par):
    #Const
    WALL_WIDTH = 5
    DATAPOINT_AMOUNT_SCORE_INPUT = 2

    #extract parameters
    bot1Name = par[0]
    bot2Name = par[1]
    processId = par[2]

    #create bot data storage
    bot1 = botStats(0)
    bot2 = botStats(1)

    #create a file
    outputFileName = f'runnerOut{processId}.json'

    outFile = open(outputFileName, 'x')
    outFile.close()

    #create subprocess
    try:
        sp = subprocess.run(f'java -jar runner.jar {bot1Name} {bot2Name} -f {outputFileName}', shell=True, capture_output=True, text=True)
    except Exception as e:
        os.remove(outputFileName)
        print(e)
        exit()

    #load json data
    try:
        with open(outputFileName, 'r') as f:
            gameData = json.load(f)

        bot1.processGameData(gameData)
        bot1.getScores()
        bot1.cleanUp()

        bot2.processGameData(gameData)
        bot2.getScores()
        bot2.cleanUp()

        #delete file
        os.remove(outputFileName)
    
    except Exception as e:
        os.remove(outputFileName)
        print(e)
        exit()

    return (bot1, bot2)

def outputScore(results):
    avgScores = [0, 0]

    succesFullResults = 0
    for result in results:
        succesFullResults += 1

        bot1 = result[0]
        bot2 = result[1]

        avgScores[0] = avgScores[0] + bot1.scores[-1]
        avgScores[1] = avgScores[1] + bot2.scores[-2]

    avgScores[0] = avgScores[0] / succesFullResults
    avgScores[1] = avgScores[1] / succesFullResults

    print(f"Average Scores:\nBot1: {avgScores[0]}\nBot2: {avgScores[1]}")

def main():
    bot1 = input("Enter the filename of bot 1: ")
    bot2 = input("Enter the filename of bot 2: ")
    numGames = int(input("Enter the total number of games that should be played: "))

    #do some multiprocessing
    with concurrent.futures.ProcessPoolExecutor() as executor:
        parameters = [(bot1, bot2, n) for n in range(numGames)]
        results = executor.map(runAzul, parameters)

        outputScore(results)
            

if __name__ == "__main__":
    main()
    
