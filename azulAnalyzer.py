import concurrent.futures
import json
import subprocess
import os

import botStats

def runAzul(par):
    #extract parameters
    bot1Name = par[0]
    bot2Name = par[1]
    processId = par[2]

    #create bot data storage
    bot1 = botStats.botStats(0)
    bot2 = botStats.botStats(1)

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
    with open(outputFileName, 'r') as f:
        gameData = json.load(f)

    #delete file
    try:
        os.remove(outputFileName)
    except:
        print(f"Process could not remove {outputFileName}")

    #check for errors
    errorFound = True
    for outLine in gameData['outputs']['referee']:
        if outLine != "":
            errorFound = False
            break

    if errorFound:
        bot1.encounteredError = True
        bot2.encounteredError = True

        for i in range(2):
            for err in gameData['errors'][str(i)]:
                if err != None:
                    print(f"Error in {processId}, {err}")

                    break
        
        return (bot1, bot2)

    #extract data from json format
    bot1.processGameData(gameData)
    if not bot1.checkTimeOut():
        bot1.getScores()
    bot1.cleanUp()

    bot2.processGameData(gameData)
    if not bot2.checkTimeOut():
        bot2.getScores()
    bot2.cleanUp()

    return (bot1, bot2)

def outputScore(results):
    avgScores = [0, 0]

    succesFullResults = 0
    for result in results:
        bot1 = result[0]
        bot2 = result[1]

        #Check if something went wrong when running runner.jar
        if bot1.encounteredError or bot2.encounteredError or bot1.computationTimeOut or bot2.computationTimeOut:
            continue

        try:
            avgScores[0] = avgScores[0] + bot1.scores[-1]
            avgScores[1] = avgScores[1] + bot2.scores[-1]
        except Exception as e:
            print(e)
            print(bot1.scores, bot2.scores)
            print(succesFullResults)
        
        succesFullResults += 1

    avgScores[0] = avgScores[0] / succesFullResults
    avgScores[1] = avgScores[1] / succesFullResults

    print(f"Average Scores:\nBot1: {avgScores[0]}\nBot2: {avgScores[1]}\nSuccesses: {succesFullResults}")

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
    
