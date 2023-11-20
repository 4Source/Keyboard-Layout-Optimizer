# ### SETUP ###
# ~~~ libraries ~~~
using Plots
using Random
using Base.Threads
using BenchmarkTools
using Statistics
using JSON


# ~~~ data ~~~
bookPath = "myBook.txt"
layoutPath = "layout/qwerty.json"
genomePath = "genome/qwerty.json"

# ~~~ weights ~~~
distanceEffort = 1 # at 2 distance penalty is squared
doubleFingerEffort = 1
doubleHandEffort = 1 

fingerCPM = [223, 169, 225, 273, 343, 313, 259, 241] # how many clicks can you do in a minute
meanCPM = mean(fingerCPM)
stdCPM = std(fingerCPM)
zScoreCPM = -(fingerCPM .- meanCPM) ./ stdCPM # negative since higher is better
fingerEffort = zScoreCPM .- minimum(zScoreCPM)


rowCPM = [131, 166, 276, 192]
meanCPM = mean(rowCPM)
stdCPM = std(rowCPM)
zScoreCPM = -(rowCPM .- meanCPM) ./ stdCPM # negative since higher is better
rowEffort = zScoreCPM .- minimum(zScoreCPM)

effortWeighting = [0.7917, 1, 0, 0.4773, 0.00] # dist, finger, row. Also had room for other weightings but removed for simplicity

# ~~~ keyboard ~~~
# load Layout from 'layoutPath' (x, y, width, heigth, row, finger, home)
io = open(layoutPath, "r")
currentLayout = JSON.parse(io, dicttype=Dict, inttype=Float64)
close(io)
currentLayout = Dict(parse(Int,string(k))=>v  for (k,v) in pairs(currentLayout))

# comparisons 
# load genome from 'genomePath'
io = open(genomePath, "r")
baselineGenome = JSON.parse(io, dicttype=Dict, inttype=Float64)
close(io)
baselineGenome = Dict(parse(Int,string(k))=>v  for (k,v) in pairs(baselineGenome))

# alphabet
letterList = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "~",
    "-",
    "+",
    "[",
    "]",
    ";",
    "'",
    "<",
    ">",
    "?"
]

# map dictionary
keyMapDict = Dict(
    'a' => [1,0], 'A' => [1,1],
    'b' => [2,0], 'B' => [2,1],
    'c' => [3,0], 'C' => [3,1],
    'd' => [4,0], 'D' => [4,1],
    'e' => [5,0], 'E' => [5,1],
    'f' => [6,0], 'F' => [6,1],
    'g' => [7,0], 'G' => [7,1],
    'h' => [8,0], 'H' => [8,1],
    'i' => [9,0], 'I' => [9,1],
    'j' => [10,0], 'J' => [10,1],
    'k' => [11,0], 'K' => [11,1],
    'l' => [12,0], 'L' => [12,1],
    'm' => [13,0], 'M' => [13,1],
    'n' => [14,0], 'N' => [14,1],
    'o' => [15,0], 'O' => [15,1],
    'p' => [16,0], 'P' => [16,1],
    'q' => [17,0], 'Q' => [17,1],
    'r' => [18,0], 'R' => [18,1],
    's' => [19,0], 'S' => [19,1],
    't' => [20,0], 'T' => [20,1],
    'u' => [21,0], 'U' => [21,1],
    'v' => [22,0], 'V' => [22,1],
    'w' => [23,0], 'W' => [23,1],
    'x' => [24,0], 'X' => [24,1],
    'y' => [25,0], 'Y' => [25,1],
    'z' => [26,0], 'Z' => [26,1],
    '0' => [27,0], ')' => [27,1],
    '1' => [28,0], '!' => [28,1],
    '2' => [29,0], '@' => [29,1],
    '3' => [30,0], '#' => [30,1],
    '4' => [31,0], '$' => [31,1],
    '5' => [32,0], '%' => [32,1],
    '6' => [33,0], '^' => [33,1],
    '7' => [34,0], '&' => [34,1],
    '8' => [35,0], '*' => [35,1],
    '9' => [36,0], '(' => [36,1],
    '`' => [37,0], '~' => [37,1],
    '-' => [38,0], '_' => [38,1],
    '=' => [39,0], '+' => [39,1],
    '[' => [40,0], '{' => [40,1],
    ']' => [41,0], '}' => [41,1],
    ';' => [42,0], ':' => [42,1],
    ''' => [43,0], '"' => [43,1],
    ',' => [44,0], '<' => [44,1],
    '.' => [45,0], '>' => [45,1],
    '/' => [46,0], '?' => [46,1]
)

handList = [1, 1, 1, 1, 2, 2, 2, 2] # what finger is with which hand

# ### KEYBOARD FUNCTIONS ###
function createGenome()
    # setup
    myGenome = shuffle(letterList)

    # return
    return myGenome
end

function drawKeyboard(myGenome, id)
    plot()
    namedColours = ["yellow", "green", "blue", "red", "purple", "blue", "green", "yellow", "orange"]
    keyOffset = 0

    for i in 1:length(currentLayout)
        keyIndex = i + keyOffset
        while !haskey(currentLayout, keyIndex)
            keyIndex = keyIndex + 1
            keyOffset = keyOffset + 1
        end
        
        letter = get(myGenome, i, "NONE")# myGenome[i]
        x, y, width, heigth, row, finger, home = currentLayout[keyIndex]
        myColour = namedColours[Int(finger)]

        if home == 1.0
            plot!([x], [y], shape=:rect, fillalpha = 0.2, linecolor = nothing, color = myColour, label = "", markersize = 16.5, dpi = 100)
        end
        
        plot!([x - width/2, x + width/2, x + width/2, x - width/2, x - width/2], [y - heigth/2, y - heigth/2, y + heigth/2, y + heigth/2, y - heigth/2], color = myColour, fillalpha = 0.2, label = "", dpi = 100)
        
        annotate!(x, y, text(letter, :black, :center, 10))
    end
    
    plot!(aspect_ratio = 1, legend = false)
    savefig("image/$(id).png")

end

function countCharacters()
    char_count = Dict{Char, Int}()
    
    # Open the file for reading
    io = open(bookPath, "r")
    
    # Read each line from the file
    for line in eachline(io)
        for char in line
            char = uppercase(char)
            char_count[char] = get(char_count, char, 0) + 1
        end
    end
    
    # Close the file
    close(io)
    
    return char_count
end

# ### SAVE SCORE ###
function appendUpdates(updateLine)
    file = open("iterationScores.txt", "a")
    write(file, updateLine, "\n")
    close(file)
end

# ### OBJECTIVE FUNCTIONS ###
function determineKeypress(currentCharacter)
    # setup
    keyPress = "NONE"

    # proceed if valid key (e.g. we dont't care about spaces now)
    if haskey(keyMapDict, currentCharacter)
        keyPress, _ = keyMapDict[currentCharacter]
    end
   
    # return
    return keyPress
end

function doKeypress(myFingerList, myGenome, keyPress, oldFinger, oldHand)
    # setup
    # ~ get the key being pressed ~
    namedKey = letterList[keyPress]
    actualKey = findfirst(x -> x == namedKey, myGenome)

    # ~ get its location ~
    x, y, _, _, row, finger, home = currentLayout[actualKey]
    currentHand = handList[Int(finger)]
    
    # loop through fingers
    for fingerID in 1:8
        # load
        homeX, homeY, currentX, currentY, distanceCounter, objectiveCounter = myFingerList[fingerID,:]

        if fingerID == finger # move finger to key and include penalty
            # ~ distance
            distance = sqrt((x - currentX)^2 + (y - currentY)^2)

            distancePenalty = distance^distanceEffort # i.e. squared
            newDistance = distanceCounter + distance

            # ~ double finger ~
            doubleFingerPenalty = 0
            if finger != oldFinger && oldFinger != 0 && distance != 0
                doubleFingerPenalty = doubleFingerEffort
            end
            oldFinger = finger


            # ~ double hand ~
            doubleHandPenalty = 0
            if currentHand != oldHand && oldHand != 0
                doubleHandPenalty = doubleHandEffort
            end
            oldHand = currentHand

            # ~ finger
            fingerPenalty = fingerEffort[fingerID]

            # ~ row
            rowPenalty = rowEffort[Int(row)]

            # ~ combined weighting
            penalty = sum([distancePenalty, doubleFingerPenalty, doubleHandPenalty, fingerPenalty, rowPenalty] .* effortWeighting)
            newObjective = objectiveCounter + penalty

            # ~ save
            myFingerList[fingerID, 3] = x
            myFingerList[fingerID, 4] = y
            myFingerList[fingerID, 5] = newDistance
            myFingerList[fingerID, 6] = newObjective
        else # re-home unused finger
            myFingerList[fingerID, 3] = homeX
            myFingerList[fingerID, 4] = homeY
        end
    end

    # return
    return myFingerList, oldFinger, oldHand
end

function objectiveFunction(myGenome)
    # setup
    objective = 0
   
    # ~ create hand ~
    myFingerList = zeros(8, 6) # (homeX, homeY, currentX, currentY, distanceCounter, objectiveCounter)
    keyOffset = 0

    for i in 1:length(currentLayout)
        keyIndex = i + keyOffset
        while !haskey(currentLayout, keyIndex)
            keyIndex = keyIndex + 1
            keyOffset = keyOffset + 1
        end

        x, y, _, _, _, finger, home = currentLayout[keyIndex]

        if home == 1.0
            myFingerList[Int(finger), 1:4] = [x, y, x, y]
        end
    end
    
    # load text
    file = open(bookPath, "r")
    oldFinger = 0
    oldHand = 0

    try
        while !eof(file)
            currentCharacter = read(file, Char)

            # determine keypress
            keyPress = determineKeypress(currentCharacter)

            # do keypress
            if keyPress != "NONE"
                myFingerList, oldFinger, oldHand = doKeypress(myFingerList, myGenome, keyPress, oldFinger, oldHand)
            end
        end
    finally
        close(file)
    end

    # calculate objective
    objective = sum(myFingerList[:, 6])
    objective = (objective / QWERTYscore - 1) * 100

    # return
    return objective
end

function baselineObjectiveFunction(myGenome) # same as previous but for getting QWERTY baseline
    # setup
    objective = 0
   
    # ~ create hand ~
    myFingerList = zeros(8, 6) # (homeX, homeY, currentX, currentY, distanceCounter, objectiveCounter)
    keyOffset = 0
        
    for i in 1:length(currentLayout)
        keyIndex = i + keyOffset
        while !haskey(currentLayout, keyIndex)
            keyIndex = keyIndex + 1
            keyOffset = keyOffset + 1
        end

        x, y, _, _, _, finger, home = currentLayout[keyIndex]

        if home == 1.0
            myFingerList[Int(finger), 1:4] = [x, y, x, y]
        end
    end
    
    # load text
    file = open(bookPath, "r")
    oldFinger = 0
    oldHand = 0

    try
        while !eof(file)
            currentCharacter = read(file, Char)

            # determine keypress
            keyPress = determineKeypress(currentCharacter)

            # do keypress
            if keyPress != "NONE"
                myFingerList, oldFinger, oldHand = doKeypress(myFingerList, myGenome, keyPress, oldFinger, oldHand)
            end
        end
    finally
        close(file)
    end

    # calculate objective
    objective = sum(myFingerList[:, 6])
    objective = objective

    # return
    return objective
end

# ### SA OPTIMISER ###
function shuffleGenome(currentGenome, temperature)
    # setup
    noSwitches = Int(maximum([2, minimum([floor(temperature/100), 46])]))

    # positions of switched letterList
    switchedPositions = randperm(46)[1:noSwitches]
    newPositions = shuffle(copy(switchedPositions))

    # create new genome by shuffeling
    newGenome = copy(currentGenome)
    for i in 1:noSwitches
        og = switchedPositions[i]
        ne = newPositions[i]

        newGenome[og] = currentGenome[ne]
    end

    # return
    return newGenome

end


function runSA()
    println("Running code...")
    # baseline
    print("Calculating raw baseline: ")
    global QWERTYscore = baselineObjectiveFunction(baselineGenome) # yes its a global, fight me
    println(QWERTYscore)

    println("From here everything is reletive with + % worse and - % better than this baseline \n Note that best layout is being saved as a png at each step. Kill program when satisfied.")

    println("Temperature \t Best Score \t New Score")


    # setup
    currentGenome = createGenome()
    currentObjective = objectiveFunction(currentGenome)

    bestGenome = currentGenome
    bestObjective = currentObjective

    temperature  = 500
    epoch = 20
    coolingRate = 0.99
    num_iterations = 25000

    drawKeyboard(bestGenome, "iteration/0")

    # run SA
    staticCount = 0.0
    for iteration in 1:num_iterations
        # ~ create new genome ~
        newGenome = shuffleGenome(currentGenome, 2)

        # ~ asess ~
        newObjective = objectiveFunction(newGenome)
        delta = newObjective - currentObjective

        println(round(temperature, digits = 2), "\t", round(bestObjective, digits=2), "\t", round(newObjective, digits=2))

        

        
        if delta < 0
            currentGenome = copy(newGenome)
            currentObjective = newObjective

            updateLine = string(round(temperature, digits = 2), ", ",  iteration, ", ", round(bestObjective, digits=5), ", ", round(newObjective, digits=5))
            appendUpdates(updateLine)

            if newObjective < bestObjective
                bestGenome = newGenome
                bestObjective = newObjective

                #staticCount = 0.0

                println("(new best, png being saved)")
                

                drawKeyboard(bestGenome, "iteration/$(iteration)")
            end
        elseif exp(-delta/temperature) > rand()
            #print(" *")
            currentGenome = newGenome
            currentObjective = newObjective
        end

        #print("\n")


        staticCount += 1.0

        if staticCount > epoch
            staticCount = 0.0
            temperature = temperature * coolingRate

            if rand() < 0.5
                currentGenome = bestGenome
                currentObjective = bestObjective
            end
        end
    end

    # save
    drawKeyboard(bestGenome, "final")

    # return
    return bestGenome

end


# ### RUN ###
runSA()


# drawKeyboard(baselineGenome, "test")

