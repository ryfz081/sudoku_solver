import sys; args = sys.argv[1:] #comment this line out when testing
import time

# THIS FILE WILL SOLVE PUZZLES IN THE 'SudokuPuzzles.txt' FILE.
# EACH ROW IN THE FILE IS A PUZZLE TO BE SOLVED
# '.' REPRESENTS A BLANK SPACE IN THE SUDOKU, AND THE IT IS ROW BY ROW
# 
# TEXT FILE FORMAT:
# .17369825632158947958724316825437169791586432346912758289643571573291684164875293
# 
# VISUAL REPRESENTATION:
# | _ 1 7 | 3 6 9 | 8 2 5 |
# | 6 3 2 | 1 5 8 | 9 4 7 |
# | 9 5 8 | 7 2 4 | 3 1 6 |
# |-----------------------|
# | 8 2 5 | 4 3 7 | 1 6 9 |
# | 7 9 1 | 5 8 6 | 4 3 2 |
# | 3 4 6 | 9 1 2 | 7 5 8 |
# |-----------------------|
# | 2 8 9 | 6 4 3 | 5 7 1 |
# | 5 7 3 | 2 9 1 | 6 8 4 |
# | 1 6 4 | 8 7 5 | 2 9 3 |



def getDimensions(area):
    width = 1
    height = area
    i = 0
    while width < height:
        i += 1
        if area % i == 0:
            width = i
            height = area // width
    return width, height
#setup lookup Tables for speedup
def setGlobals(pzl): 
    global sideLength, listOfRowSets, listOfColSets, listOfBoxSets, allBoxesList, symbolSet, allPositions, constraintNeighborLookupTable, positionBoxesLookupDict
    sideLength = float(len(pzl))**0.5 #takes square root; finds the whole puzzle side dimensions
    sideLength = int(sideLength)

    #find the symbolset
    validChars = {"1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","G","0"}
    validCharsList = ["1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","G","0"]
    symbolSet = set([])
    for char in pzl:
        if char not in symbolSet and char != ".":
            symbolSet.add(char)
    validChars = validChars.difference(symbolSet)
    
    if len(symbolSet) < sideLength:
        for c in validCharsList:
            if c not in symbolSet and c in validChars and len(symbolSet) < sideLength:
                symbolSet.add(c)


    listOfRowSets = [[index for index in range(n*sideLength, (n+1)*sideLength)] for n in range(sideLength)]
    listOfColSets = [[index for index in range(n, sideLength*sideLength-sideLength+n+1, sideLength)] for n in range(sideLength)]

    boxWidth, boxHeight = getDimensions(sideLength)

    #using subBlock dimensions to find the contraintSets(of indices)
    #no comprehension cuz this is confusing 
    widthCounter = 0 

    subHeightCounter = 1
    whichBox = 0
    listOfBoxSets = [[] for i in range(sideLength)] #list of all boxSets that will be filled up

    for index in range(sideLength**2):
        if widthCounter%boxWidth == 0 and widthCounter != 0: #every time it iterates thru subblockwidth
            if widthCounter%sideLength == 0: #if it went thru an entire row(not subrow)
                
                whichBox = whichBox - boxHeight + 1

                if subHeightCounter%boxHeight == 0 and subHeightCounter != 0:
                    whichBox += boxHeight
                subHeightCounter += 1
            else: 
                whichBox += 1

        listOfBoxSets[whichBox].append(index) #change to append if using constraint list instead of constraint set
        
        widthCounter += 1
    #END OF BOXSET CALCULATIONS

    allBoxesList = listOfRowSets + listOfColSets + listOfBoxSets
    
    allPositions = set([])
    for i in range(sideLength*sideLength):
        allPositions.add(i)
    constraintNeighborLookupTable = {}
    positionBoxesLookupDict = {}
    for position in allPositions:
        constraintNeighborLookupTable[position] = findConstraintSets(position, positionBoxesLookupDict)

def solve(pzl, fileindex):
    validIndexMap = createIndexMap(pzl)
    startTime = time.time()
    maxBox = []
    validIndexMap = findSolution(validIndexMap, maxBox)
    solution = getSolution(validIndexMap)
    endTime = time.time()
    #print(fileindex," ", solution, " ", checkSum(solution), " %ss" %round(endTime - startTime, 6)) #added print method to bruteforce
    return solution

def isSolved(validIndexMap):
    # A puzzle is solved if each box is a permutation of the symbolSet.
    def isBoxSolved(box): 
        return set(''.join(validIndexMap[s]) for s in box) == symbolSet
    
    return validIndexMap is not False and all(isBoxSolved(box) for box in allBoxesList)

def checkSum(pzl):
    #find min char
    minChar = pzl[0]
    for char in pzl:
        if ord(char) < ord(minChar):
            minChar = char
    csum = 0
    for char in pzl:
        csum += ord(char) - ord(minChar)
    return csum

def getSolution(validIndexMap):
    if not validIndexMap or len(validIndexMap.keys()) == 0:
        return "No solution found"    
    
    return "".join([''.join(item) for item in validIndexMap.values()])

#creates index map(dataStruct) for finding the optimal position
def createIndexMap(pzl): 
    # choiceIndexMap= {i:findChoiceSet(pzl, i) for i in range(len(pzl)) if pzl[i] == "."}
    choiceIndexMap= {i:findChoiceSet(pzl, i) for i in range(len(pzl))}
    return choiceIndexMap

def findConstraintSets(index, positionBoxesLookupDict):
    rowSet, colSet, boxSet = set([]), set([]), set([])

    for cs in listOfColSets:
        if index in cs:
            colSet = cs
    for cs in listOfRowSets:
        if index in cs:
            rowSet = cs
    for cs in listOfBoxSets:
        if index in cs:
            boxSet = cs
            
    positionBoxesLookupDict.update({index: [colSet, rowSet, boxSet]})       
    return colSet+rowSet+boxSet

#find symbols for a given position(hole and pzl)
def findChoiceSet(pzl, index): 
    choiceSet = []
    if len(pzl[index]) == 1 and pzl[index] != ".":
        choiceSet.append(pzl[index])
        return ''.join(choiceSet) 
    else:
        for index in constraintNeighborLookupTable[index]: #set of neighbors
            if pzl[index] != ".":
                choiceSet.append(pzl[index])

    # return ''.join((symbolSet.difference(set(choiceSet))))
    result = ''.join([''.join(item) for item in symbolSet.difference(set(choiceSet))])
    return result

def findSolution(validIndexMap, maxBox):
    # Finding an optimal position, try all possible symbols in validIndexMap.
    if validIndexMap is False:
        return False
    if all(len(validIndexMap[pos]) == 1 for pos in allPositions): 
        return validIndexMap # the puzzle is solved
    ## Chose the unfilled hole position with the fewest possibilities: the fewest possible symbols within the 
    ## most filled box, keep filling this box until it is completed filled
    pos, maxBox = bruteForce(validIndexMap, maxBox)
    return selectPath(findSolution(updateIndexMap(validIndexMap.copy(), pos, symbol), maxBox) for symbol in validIndexMap[pos])

def bruteForce(validIndexMap, maxBox):   
    
    if len(maxBox) > 1:
        filledSum = 0
        for pos in maxBox:
            if len(validIndexMap[pos]) == 1:
                filledSum = filledSum + 1
                    
        if filledSum < sideLength:        
            cnt,pos = min((len(validIndexMap[pos]), pos) for pos in maxBox if len(validIndexMap[pos]) > 1) 
            return pos, maxBox
                
    boxFilledCountMap = {}    
    
    for boxIndex in range(len(listOfBoxSets)): 
        filledSum = 0
        for pos in listOfBoxSets[boxIndex]:
            if len(validIndexMap[pos]) == 1:
                filledSum = filledSum + 1
            
        if filledSum < sideLength:        
            boxFilledCountMap.update({boxIndex: filledSum})
    
    maxBoxIndex, count = sorted(boxFilledCountMap.items(), key=lambda x: x[1], reverse=True)[0]
        
    maxBox = listOfBoxSets[maxBoxIndex]  
    if len(maxBox) > 0:
        cnt,pos = min((len(validIndexMap[pos]), pos) for pos in maxBox if len(validIndexMap[pos]) > 1) 
        return pos, maxBox
    
    return maxBoxIndex, maxBox

def updateIndexMap(validIndexMap, pos, symbol):
    # remove all the other choices (except symbol) from validIndexMap[pos] and streamline.
    # return validIndexMap, except return False if a contradiction is found.
    removedSymbols = ''.join(validIndexMap[pos]).replace(symbol, '')
    if all(applyConstraints(validIndexMap, pos, removedSymbol) for removedSymbol in removedSymbols):
        return validIndexMap
    else:
        return False

# remove the symbol from all the neighbors for this position    
def applyConstraints(validIndexMap, pos, symbol):
    # apply the Constraints and streamline.
    if symbol not in validIndexMap[pos] or len(validIndexMap[pos]) == 1:
        return validIndexMap 
    
    # remove the specified symbol
    validIndexMap[pos] = validIndexMap[pos].replace(symbol,'')
    
    # Constraint 1: If a position is reduced to one symbol, then remove this symbol from its neighbors.
    if len(validIndexMap[pos]) == 0:       
        return False #Error: last value removed
    elif len(validIndexMap[pos]) == 1:
        validSymbol = validIndexMap[pos]
        if not all(applyConstraints(validIndexMap, neighbor, validSymbol) for neighbor in constraintNeighborLookupTable[pos]):
            return False
        
    # Constraint 2: If a box is reduced to only one position for this symbol, then set this symbol to  this position.
    for box in positionBoxesLookupDict[pos]:
        neighbors = [position for position in box if symbol in validIndexMap[position]]
        if len(neighbors) == 0:
            return False # error: no position for this value
        elif len(neighbors) == 1:
            # symbol is set to this box
            if not updateIndexMap(validIndexMap, neighbors[0], symbol):
                return False
            
    return validIndexMap    

def selectPath(paths):
    # Return path that is true for possibley solving the puzzle.
    for path in paths:
        if path: 
            return path
    return False


def makeGrid(inputStr):
    grid = []
    for i in range(9):
        temp = []
        for j in range (9):
            temp.append(inputStr[i*9+j])
        grid.append(temp)
    for i in grid:
        print(i)

def main():
    if True:
        with open("SudokuPuzzles.txt") as f1:
            list1 = [line.strip() for line in f1]
        startTime = time.time()
        fileIndex = 1
        for pzl in list1:
            #startTime = time.time()
            setGlobals(pzl)
            print('Puzzle',list1.index(pzl)+1) #wont work if two of same puzzle cuz .index()
            makeGrid(pzl)
            print('Puzzle',list1.index(pzl)+1, 'Solution')
            pzlMap1 = createIndexMap(pzl)
            solution = solve(pzl, fileIndex)
            makeGrid(solution)
            print("")
            fileIndex += 1

        endTime = time.time()    
        endTime = time.time()    
        print("Total time used: %ss" %round(endTime - startTime, 6))
main()

