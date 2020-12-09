import math, random, numpy as np

#utility functions -------------------------

#taken from 112 course website------------
def rgbColorString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

#modified tolerance
def almostEqual(x, y):
    return abs(x - y) < 0.02 #time per buffer

#-------------------------------------

def inverseRgbColorString(colorString):
    colorString = colorString[1:]
    rString = colorString[:2]
    gString = colorString[2:4]
    bString = colorString[4:]
    return int(rString, 16), int(gString, 16), int(bString, 16) #https://stackoverflow.com/questions/209513/convert-hex-string-to-int-in-python

#takes in a list of colors and returns the average brightness
#this measures how well the user is doing! 
def getAverageBrightness(colors):
    values = [inverseRgbColorString(color) for color in colors]
    n = 0
    total = 0
    for color in values:
        if color[0] == 0: #only consider notes that aren't red (the notes the user is trying to play)
            if color[1] == 0:
                total += color[2]
            else:
                total += color[1]
            n += 1
    if n == 0:
        return 1
    return total/n
#---------------------------------------


#a particular object on a screen in my program
class ObjectToDraw:
    #drawfunction is a function which draws the object centered at (x, y)
    def __repr__(self):
        return str((self.x, self.y))
    
    def __init__(self,  defaultX, defaultY , drawFunction):
        self.x = defaultX
        self.y = defaultY
        self.drawFunction = drawFunction
    
    def drawObject(self, canvas, x, y, screen):
        self.drawFunction(canvas, x, y, screen)


#used to create boxes that appear with text in them that display how to use different elements of the program
class HelpTextBox(ObjectToDraw):

    #amount of time user has to keep mouse steady over an object for a help box to appear
    helpDisplayActivationTime = 1.5

    #pointX and pointY is the coordinate of the part of the help box such that a small spike points there, this demonstrates which compoment the helper box is referring to
    def __init__(self, defaultX, defaultY, topLeftX, topLeftY, bottomRightX, bottomRightY, text, index): #index is the position of this particular instance of the box helper in the box helper list
        self.x = defaultX
        self.y = defaultY
        self.topLeftX = topLeftX
        self.topLeftY = topLeftY
        self.bottomRightY = bottomRightY
        self.bottomRightX = bottomRightX
        self.text = text
        self.createDrawFunction()
        self.index = index
    
    def createDrawFunction(self):    
        def drawHelpTextBox(canvas, x, y, screen):
            if screen.currentAnimationState != "animateNormalPos":
                screen.eventControl["helpBoxes"][self.index][1] = 0
                return
            if screen.eventControl["helpBoxes"][self.index][1] < HelpTextBox.helpDisplayActivationTime:
                return
            charactersPer80Pixels = 12
            eightyPixelsPerLine = (self.bottomRightX - self.topLeftX)/(80)
            charactersPerLine = int(charactersPer80Pixels*eightyPixelsPerLine) - 1 #safety measure to ensure characters don't clip at the edges
            textsToMake = []
            start = 0
            while start < len(self.text):
                charactersPerLine = int(charactersPer80Pixels*eightyPixelsPerLine)
                if start + charactersPerLine >= len(self.text):
                    charactersPerLine = len(self.text) - start
                consideredText = self.text[start:start + charactersPerLine]
                if consideredText == "":
                    break
                if start + charactersPerLine == len(self.text): #end case
                    textsToMake.append(consideredText)
                    break
                while consideredText[-1] != " " and self.text[start + charactersPerLine] != " ":
                    consideredText = consideredText[:-1]
                    charactersPerLine -= 1
                    if consideredText == "":
                        break
                textsToMake.append(consideredText)
                start += charactersPerLine
            canvas.create_rectangle(self.topLeftX + x, self.topLeftY + y, self.bottomRightX + x, self.bottomRightY + y, fill = "white")
            margin = (self.bottomRightY - self.topLeftY)/5
            textHeight = ((self.bottomRightY - self.topLeftY - 2*margin)/(len(textsToMake))) #not zero
            y = self.topLeftY + 1.5*margin
            for line in textsToMake:
                canvas.create_text((self.topLeftX + x + self.bottomRightX)/2, y, text = line, font = "Arial 16")
                y += textHeight
        self.drawFunction = drawHelpTextBox



#a particular screen in my program
#this just makes everything more organized
#make sure you pass in the objects to draw in the order you want them drawn
#animation states is a dictionary, mapping names to different possible states
#eventControl is a dictionary of pairs
#each 'pair' has a function to tell the outcome of an event, and then the next is the information that should change under that occurence
class Screen:
    def __init__(self, name, objectsToDraw, defaultAnimationState = None, animationStates = None, eventControl = None, screenTopLeftX = 0, screenTopLeftY = 0):
        self.name = name
        self.eventControl = eventControl
        self.objectsToDraw = objectsToDraw
        self.animationStates = animationStates
        self.currentAnimationState = defaultAnimationState
        self.topLeftX, self.topLeftY = screenTopLeftX, screenTopLeftY

    def doAnimationStep(self):
        self.animationStates[self.currentAnimationState](self)

    def __repr__(self):
        return self.name

    def drawScreen(self, canvas):
        for objectToDraw in self.objectsToDraw:
            adjustedX = objectToDraw.x + self.topLeftX
            adjustedY = objectToDraw.y + self.topLeftY
            objectToDraw.drawObject(canvas, adjustedX, adjustedY, self)


def getTitleScreen(appWidth, appHeight):
    moveDown = appHeight/10
    def drawTitle(canvas, x, y, screen):
        canvas.create_text(x, y, text = "Polyrhythm Peruser", font = "Arial 48 bold")
    drawTitleObject = ObjectToDraw(appWidth/2, appHeight/3 + moveDown, drawTitle)
    def drawName(canvas, x, y, screen):
        canvas.create_text(x, y, text = "Created by Zack Sussman", font = "Arial 22 bold")
    drawNameObject = ObjectToDraw(appWidth/2, 6*appHeight/15 + moveDown, drawName)
    def drawBgColor(canvas, x, y, screen):
        canvas.create_rectangle(x, y, x + appWidth, y + appHeight, fill = "darkgreen")
    drawBgColorObject = ObjectToDraw(0, 0, drawBgColor)
    def drawBeginBox(canvas, x, y, screen):
        halfBoxLength = (appWidth/4)*3/4
        halfBoxHeight = (appHeight/15)*3/4
        canvas.create_rectangle(x - halfBoxLength, y - halfBoxHeight + moveDown,
                                x + halfBoxLength, y + halfBoxHeight + moveDown,
                                fill = screen.eventControl["isMouseInsideBeginBox"][1])
    drawBeginBoxObject = ObjectToDraw(appWidth/2, appHeight/2, drawBeginBox)
    def isMouseInsideBeginBox(x, y, screen):
        leftBound = screen.topLeftX + appWidth/2 - (appWidth/4)*3/4
        upBound = screen.topLeftY + appHeight/2 - (appHeight/15)*3/4 + moveDown
        rightBound = screen.topLeftX + appWidth/2 + (appWidth/4)*3/4
        downBound = screen.topLeftY + appHeight/2 + (appHeight/15)*3/4 + moveDown
        if x < leftBound or x > rightBound:
            return False
        if y < upBound or y > downBound:
            return False
        return True
    def drawBeginText(canvas, x, y, screen):
        canvas.create_text(x, y, text = "Begin", font = "Arial 32 bold")
    drawBeginTextObject = ObjectToDraw(appWidth/2, appHeight/2 + moveDown, drawBeginText)
    def drawMiniSquare(canvas, x, y, screen):
        if x > appWidth or y > appHeight or x < 0 or y < 0:
            return
        g = abs(int(255*(.5 - x/appWidth)))
        r = abs(int(255 - g/3))
        b = int((255/2)*(1 + math.cos(2*math.pi*y/appHeight)))
        canvas.create_rectangle(x - 14, y - 14, x + 14, y + 14, fill = "black")
        canvas.create_rectangle(x - 10, y - 10, x + 10, y + 10, fill = rgbColorString(r, g, b)) 
    drawMiniSquareObject = ObjectToDraw(appWidth/2 + 10, appHeight/2, drawMiniSquare)
    drawMiniSquareObjects = [drawMiniSquareObject]
    def animateMiniSquares(screen):
        for miniSquareObject in screen.objectsToDraw:
            if miniSquareObject.drawFunction != drawMiniSquare:
                continue #only want to animate miniSquareObjects
            y = miniSquareObject.y - appHeight/2
            x = miniSquareObject.x - appWidth/2
            angle = math.sqrt(x**2 + y**2)/30
            angle += .1
            miniSquareObject.x = appWidth/2 + 30*angle*math.cos(angle)
            miniSquareObject.y = appHeight/2 - 30*angle*math.sin(angle)
        if random.randint(4, 20) == 20:
            screen.objectsToDraw.insert(len(screen.objectsToDraw) - 4, ObjectToDraw(appWidth/2, appHeight/2, drawMiniSquare))
    def animateNormalPos(screen):
        animateMiniSquares(screen)
    def animateExitTitleSlide(screen):
        for spinnySquare in screen.objectsToDraw[1:-4]:
            screen.objectsToDraw.remove(spinnySquare)
        animateMiniSquares(screen)
        moveSpeed = 20
        screen.topLeftX += moveSpeed
    completeObjectsToDraw = [drawBgColorObject] + drawMiniSquareObjects + [drawTitleObject] + [drawNameObject] + [drawBeginBoxObject] + [drawBeginTextObject]
    titleScreen = Screen("Title Screen", completeObjectsToDraw, "animateNormalPos", 
                        {"animateNormalPos":animateNormalPos, "exit":animateExitTitleSlide},
                        {"isMouseInsideBeginBox":[isMouseInsideBeginBox, "gold"]})
    return titleScreen

def getPromptUserScreen(appWidth, appHeight):
    def drawBgColor(canvas, x, y, screen):
        canvas.create_rectangle(x, y, x + appWidth, y + appHeight, fill = "darkgreen")
    drawBgColorObject = ObjectToDraw(0, 0, drawBgColor)
    
    def animateEntrance(screen):
        moveSpeed = 20
        screen.topLeftX += moveSpeed
        if screen.topLeftX > 0:
            screen.topLeftX = 0
            screen.currentAnimationState = "animateNormalPos"

    def animateUpEntrance(screen):
        moveSpeed = 20
        screen.topLeftY -= moveSpeed
        if screen.topLeftY  <= 0:
            screen.topLeftY = 0
            screen.currentAnimationState = "animateNormalPos"

    def animateNormalPos(screen):
        pass

    def drawPromptText(canvas, x, y, screen):
        canvas.create_text(x, y, text = "Enter a polyrhythm you wish to learn.", font = "Arial 32")
    drawPromptTextObject = ObjectToDraw(appWidth/2, appHeight/3, drawPromptText)

    def drawAgainstText(canvas, x, y, screen):
        canvas.create_text(x, y, text = "against", font = "Arial 32")
    drawAgainstTextObject = ObjectToDraw(appWidth/2, appHeight/2, drawAgainstText)

    def drawTextBoxesAndText(canvas, x, y, screen):
        halfTextBoxLength = appWidth/18
        textBoxOffset = appWidth/6
        #left textbox and text -------------------------------
        canvas.create_rectangle(x - halfTextBoxLength - textBoxOffset, 
                                y - halfTextBoxLength,
                                x + halfTextBoxLength - textBoxOffset,
                                y + halfTextBoxLength,
                                fill = screen.eventControl["mouseClickedInLeftBox"][1])
        whitePartHalfLength = halfTextBoxLength*9/10
        canvas.create_rectangle(x - whitePartHalfLength - textBoxOffset,
                                y - whitePartHalfLength,
                                x + whitePartHalfLength - textBoxOffset,
                                y + whitePartHalfLength,
                                fill = "white")
        canvas.create_text(x - textBoxOffset, y, 
                            text = screen.eventControl["typedInLeftBox"][1],
                            font = "Arial 25 bold")
        #---------------------------------------------------
        #right textbox and text ------------------------------
        canvas.create_rectangle(x - halfTextBoxLength + textBoxOffset, 
                                y - halfTextBoxLength,
                                x + halfTextBoxLength + textBoxOffset,
                                y + halfTextBoxLength,
                                fill = screen.eventControl["mouseClickedInRightBox"][1])
        whitePartHalfLength = halfTextBoxLength*9/10
        canvas.create_rectangle(x - whitePartHalfLength + textBoxOffset,
                                y - whitePartHalfLength,
                                x + whitePartHalfLength + textBoxOffset,
                                y + whitePartHalfLength,
                                fill = "white")
        canvas.create_text(x + textBoxOffset, y, 
                            text = screen.eventControl["typedInRightBox"][1],
                            font = "Arial 25 bold")
        #---------------------------------------------------
    
    drawTextBoxesAndTextObject = ObjectToDraw(appWidth/2, appHeight/2, drawTextBoxesAndText)

    def clickedInLeftBox(x, y, screen):
        halfLength = (appWidth/18)*9/10
        tbOffset = appWidth/6
        leftBorder = appWidth/2 - tbOffset - halfLength
        rightBorder = appWidth/2 - tbOffset + halfLength
        upBorder = appHeight/2 - halfLength
        downBorder = appHeight/2 + halfLength
        if x < leftBorder or x > rightBorder:
            return False
        if y > downBorder or y < upBorder:
            return False
        return True
    
    def clickedInRightBox(x, y, screen):
        halfLength = (appWidth/10)*9/10
        tbOffset = appWidth/8
        leftBorder = appWidth/2 + tbOffset - halfLength
        rightBorder = appWidth/2 + tbOffset + halfLength
        upBorder = appHeight/2 - halfLength
        downBorder = appHeight/2 + halfLength
        if x < leftBorder or x > rightBorder:
            return False
        if y > downBorder or y < upBorder:
            return False
        return True
    
    def drawGoBoxAndText(canvas, x, y, screen):
        moveDown = appHeight/7
        halfBoxLength = (appWidth/15)*3/4
        halfBoxHeight = (appHeight/20)*3/4
        canvas.create_rectangle(x - halfBoxLength, y - halfBoxHeight + moveDown,
                                x + halfBoxLength, y + halfBoxHeight + moveDown,
                                fill = screen.eventControl["mouseInsideGoBox"][1])
        canvas.create_text(x, y + moveDown, text = "Go", font = "Arial 25 bold")
    drawGoBoxAndTextObject = ObjectToDraw(appWidth/2, appHeight/2, drawGoBoxAndText)

    def isMouseInsideGoBox(x, y, screen):
        moveDown = appHeight/7
        halfBoxLength = (appWidth/15)*3/4
        halfBoxHeight = (appHeight/20)*3/4
        leftBound = appWidth/2 - halfBoxLength
        rightBound = appWidth/2 + halfBoxLength
        upBound = appHeight/2 + moveDown - halfBoxHeight
        downBound = appHeight/2 + moveDown + halfBoxHeight
        if x < leftBound or x > rightBound:
            return False
        if y > downBound or y < upBound:
            return False
        return True

    def exitDownAnimation(screen):
        moveSpeed = 20
        screen.topLeftY += moveSpeed

    eventControl = {"mouseClickedInLeftBox":[clickedInLeftBox, "black"],
                    "mouseClickedInRightBox":[clickedInRightBox, "black"],
                    "typedInLeftBox":[None, ""],
                    "typedInRightBox":[None, ""],
                    "mouseInsideGoBox":[isMouseInsideGoBox, "gold"]}
    animationStates = {"entrance":animateEntrance, "animateNormalPos":animateNormalPos, "exitDown":exitDownAnimation, "enterUp":animateUpEntrance}

    objectsToDraw = [drawBgColorObject, drawPromptTextObject, drawAgainstTextObject, drawTextBoxesAndTextObject, drawGoBoxAndTextObject]
    
    startingAnimationState = "entrance"

    screen = Screen("Prompt User Screen", objectsToDraw, startingAnimationState, animationStates, eventControl, -1*appWidth)
    return screen

#num1 and num2 are the two numbers that will create the polyrhythm!
def getLearnPolyrhythmScreen(appWidth, appHeight, num1, num2):

    def drawBgColor(canvas, x, y, screen):
        canvas.create_rectangle(x, y, x + appWidth, y + appHeight, fill = screen.eventControl["bgColor"])
    drawBgColorObject = ObjectToDraw(0, 0, drawBgColor)

    def drawPlayButton(canvas, x, y, screen):
        halfLength = appWidth/22
        halfHeight = (appHeight/17)/2
        initialY = appHeight*(5/6 + 1)/2
        canvas.create_rectangle(x + appWidth/2 - halfLength, y + initialY - halfHeight,
                                x + appWidth/2 + halfLength, y + initialY + halfHeight,
                                fill = screen.eventControl["isMouseInsidePlayButton"][1])
    drawPlayButtonObject = ObjectToDraw(0, 0, drawPlayButton)

    def isMouseInsidePlayButton(x, y, screen):
        halfLength = appWidth/22
        halfHeight = (appHeight/17)/2
        initialY = appHeight*(5/6 + 1)/2
        if x < screen.topLeftX + appWidth/2 - halfLength or x > screen.topLeftX + appWidth/2 + halfLength:
            return False
        if y < screen.topLeftY + initialY - halfHeight or y > screen.topLeftY + initialY + halfHeight:
            return False
        return True
    
    playButtonHelper = HelpTextBox(0, 0, appWidth/10, 2*appHeight/3, 9*appWidth/10,  appHeight*(5/6 + 1)/2 - (appHeight/17)/2 - appHeight/10, "Use the keys t and n to play along with the green and blue dots! You can use the space bar or press the play button to start it. The cursor will glow brighter the more accurate you are. Explore the settings to change the pitches of the notes as well as the keys you use to play.", 1)

    def drawBlueToggleBox(canvas, x, y, screen):
        topMargin = appHeight/30
        sideMargin = appWidth/10 + 1.5*appWidth/20 #right next to blue button
        sideLength = appWidth/20
        canvas.create_rectangle(x + appWidth - sideMargin - sideLength, 
                                y + topMargin,
                                x + appWidth - sideMargin,
                                y + topMargin + sideLength,
                                fill = screen.eventControl["isMouseInsideBlueToggleBox"][1],
                                outline = "white")
    def drawGreenToggleBox(canvas, x, y, screen):
        topMargin = appHeight/30
        sideMargin = appWidth/10
        sideLength = appWidth/20
        canvas.create_rectangle(x + appWidth - sideMargin - sideLength, 
                                y + topMargin,
                                x + appWidth - sideMargin,
                                y + topMargin + sideLength,
                                fill = screen.eventControl["isMouseInsideGreenToggleBox"][1],
                                outline = "white")
    drawBlueToggleBoxObj = ObjectToDraw(0, 0, drawBlueToggleBox)   
    drawGreenToggleBoxObj = ObjectToDraw(0, 0, drawGreenToggleBox)  

    def isMouseInsideBlueToggleBox(x, y, screen):
        topMargin = appHeight/30
        sideMargin = appWidth/10 + 1.5*appWidth/20 #right next to blue button
        sideLength = appWidth/20
        xCond = x > appWidth - sideMargin - sideLength and x < appWidth - sideMargin
        yCond = y > topMargin and y < topMargin + sideLength
        return xCond and yCond
    def isMouseInsideGreenToggleBox(x, y, screen):
        topMargin = appHeight/30
        sideMargin = appWidth/10
        sideLength = appWidth/20
        xCond = x > appWidth - sideMargin - sideLength and x < appWidth - sideMargin
        yCond = y > topMargin and y < topMargin + sideLength
        return xCond and yCond

    blueGreenTextBoxHelper = HelpTextBox(0, 0, appWidth/2, appHeight/30 + appWidth/20, appWidth - (appWidth/10 + 1.5*appWidth/20), appHeight/30 + 4*appWidth/20 ,"Use the green and blue buttons to toggle whether or note you see, hear and play, the green pulses or blue pulses respectively!", 3)

    def drawBlackTriangle(canvas, x, y, screen):
        if screen.currentAnimationState == "animatePolyrhythm":
            return
        halfLength = appWidth/22
        halfHeight = (appHeight/17)/2
        initialY = appHeight*(5/6 + 1)/2
        topLeftX = x + appWidth/2 - halfLength
        topLeftY =  y + initialY - halfHeight
        bottomRightX = x + appWidth/2 + halfLength
        bottomRightY = y + initialY + halfHeight
        distFromLeft = halfLength/2
        distFromRight = halfLength/2
        upDownMargin = appWidth/20
        canvas.create_polygon(topLeftX + distFromLeft, topLeftY + upDownMargin, 
                              topLeftX + distFromLeft, bottomRightY - upDownMargin,
                              bottomRightX - distFromRight, (topLeftY + bottomRightY)/2, 
                              fill = "black")
    drawBlackTriangleObject = ObjectToDraw(0, 0, drawBlackTriangle)

    def drawBlackSquare(canvas, x, y, screen):
        if screen.currentAnimationState != "animatePolyrhythm":
            return
        halfLength = appWidth/22
        halfHeight = (appHeight/17)/2
        initialY = appHeight*(5/6 + 1)/2
        topLeftX = x + appWidth/2 - halfLength
        topLeftY =  y + initialY - halfHeight
        bottomRightX = x + appWidth/2 + halfLength
        bottomRightY = y + initialY + halfHeight
        distFromLeft = halfLength/2
        distFromRight = halfLength/2
        upDownMargin = appWidth/20
        canvas.create_rectangle(topLeftX + distFromLeft, topLeftY + upDownMargin,
                                bottomRightX - distFromRight, bottomRightY - upDownMargin, fill = "black")
    drawBlackSquareObject = ObjectToDraw(0, 0, drawBlackSquare)


    def drawMarker(canvas, x, y, screen, gridSize, xShift, yShift, row, col, changeInX, color):
        compareChangeInX = changeInX
        changeInX *= gridSize
        topMargin = appHeight/10
        sideMargin = appWidth/10
        xCoord = x + sideMargin + gridSize*col + xShift
        yCoord = y + topMargin + gridSize*row + yShift
        jumpIn = gridSize*7/10
        if not (col == num2 - 1 and compareChangeInX > .5):
            canvas.create_oval(xCoord + changeInX + jumpIn, yCoord + jumpIn, xCoord + gridSize + changeInX - jumpIn, yCoord + gridSize - jumpIn, outline = color, width = gridSize/23)
        elif row != num1 - 1:
            xCoord = x + sideMargin + xShift - gridSize
            yCoord += gridSize
            canvas.create_oval(xCoord + changeInX + jumpIn,jumpIn + yCoord, xCoord - jumpIn + gridSize + changeInX, yCoord - jumpIn + gridSize, outline = color, width = gridSize/23)
        else:
            xCoord = x + sideMargin + xShift - gridSize
            yCoord = y + topMargin + yShift
            canvas.create_oval(xCoord +jumpIn + changeInX, jumpIn +yCoord, xCoord - jumpIn + gridSize + changeInX, yCoord - jumpIn + gridSize, outline = color, width = gridSize/23)

    def drawNoteGrid(canvas, x, y, screen):
        topMargin = appHeight/10
        bottomMargin = appHeight/6
        sideMargin = appWidth/10
        totalGridHeight = appHeight - topMargin - bottomMargin
        totalGridWidth = appWidth - 2*sideMargin
        gridSize = (totalGridHeight)/num1 if num1 >= num2 else totalGridWidth/num2
        canvas.create_rectangle(x + sideMargin, y + topMargin, 
                                x + sideMargin + totalGridWidth,
                                y + topMargin + totalGridHeight,
                                fill = "black", 
                                outline = "white")
        xShift = (totalGridWidth - num2*gridSize)/2
        yShift = (totalGridHeight - num1*gridSize)/2
        for row in range(num1):
            for col in range(num2):
                xCoord = x + sideMargin + gridSize*col + xShift
                yCoord = y + topMargin + gridSize*row + yShift
                jumpIn = gridSize*7/10

                color = screen.eventControl["dotColors"][num2*row + col]
                #greenDeactivated and blueDeactivated are True only if the current dot NORMALLY would be colored that respective color, but shouldn't be on this pass
                greenDeactivated = inverseRgbColorString(color)[1] != 0 and inverseRgbColorString(screen.eventControl["isMouseInsideGreenToggleBox"][1]) == (0, 50, 0)
                blueDeactivated = inverseRgbColorString(color)[2] != 0 and inverseRgbColorString(screen.eventControl["isMouseInsideBlueToggleBox"][1]) == (0, 0, 50)
                needBothDots = ((num2*row + col) % num1 == 0) and ((num2*row + col)%num2 == 0)
                if ((greenDeactivated or blueDeactivated) and not (needBothDots)) or (greenDeactivated and blueDeactivated):
                    color = rgbColorString(140, 0, 0)
                if (needBothDots) and not blueDeactivated and greenDeactivated:
                    color = rgbColorString(0, 0, inverseRgbColorString(screen.eventControl["dotColors"][num2*row + col])[2])
                elif needBothDots and (not greenDeactivated) and blueDeactivated:
                    color = rgbColorString(0, inverseRgbColorString(screen.eventControl["dotColors"][num2*row + col])[1], 0)
                screen.eventControl["dotColorsForAccuracy"][num2*row + col] = color
                canvas.create_oval(xCoord + jumpIn, yCoord + jumpIn, xCoord + gridSize - jumpIn, yCoord + gridSize - jumpIn,
                fill = color, outline = "black")

                moveOverBy = screen.eventControl["dotPositionFractionalPart"]
                #assert(moveOverBy < 1)
                #move over by is fractional relative to the gridSize
                changeInX = gridSize*moveOverBy
                brightness = getAverageBrightness(screen.eventControl["dotColors"])/255
                selectorColor = rgbColorString(int(brightness*144), int(brightness*238), int(brightness*144)) #numbers for TKinter's lightgreen
                newJumpIn = (3*jumpIn/8)*screen.eventControl["selectorSqueezeSize"]
                if (screen.eventControl["currentDotSelector"] == num2*row + col - 1 and col != 0):
                    canvas.create_oval(xCoord - gridSize + newJumpIn + changeInX, yCoord + newJumpIn, xCoord - newJumpIn + changeInX, yCoord + gridSize - newJumpIn, outline = selectorColor, width = gridSize/23)
                elif screen.eventControl["currentDotSelector"] == num2*row + col and (col == num2 - 1) and moveOverBy <= .5:
                    canvas.create_oval(xCoord + newJumpIn + changeInX, yCoord + newJumpIn, xCoord + gridSize - newJumpIn + changeInX, yCoord + gridSize - newJumpIn, outline = selectorColor, width = gridSize/23)
                elif screen.eventControl["currentDotSelector"] == num2*row + col and (col == num2 - 1) and moveOverBy > .5:
                    xCoord = x + sideMargin + xShift - gridSize
                    if row == num1 - 1:
                        yCoord = y + topMargin + yShift
                    else:
                        yCoord += gridSize
                    canvas.create_oval(xCoord + newJumpIn + changeInX, yCoord + newJumpIn, xCoord + gridSize - newJumpIn + changeInX, yCoord + gridSize - newJumpIn, outline = selectorColor, width = gridSize/23)
        i = 0
        while i < len(screen.eventControl["playedPositions"]):
            played = screen.eventControl["playedPositions"][i]
            drawMarker(canvas, x, y, screen, gridSize, xShift, yShift, played[0], played[1], played[2], rgbColorString(played[3][0], played[3][1], played[3][2]))
            played[3] = (int(.9*played[3][0]), int(.9*played[3][1]), int(.9*played[3][2]))
            screen.eventControl["playedPositions"][i] = played
            if .9*played[3][0] < 20:
                screen.eventControl["playedPositions"].pop(i)
                i -= 1
            i += 1

    drawNoteGridObject = ObjectToDraw(0, 0, drawNoteGrid)

    def updateSelectorSquezeSize(screen):
        if screen.eventControl["selectorSqueezeSize"] == 1:
            return
        screen.eventControl["selectorSqueezeSize"] += .02
        if screen.eventControl["selectorSqueezeSize"] >= 1:
            screen.eventControl["selectorSqueezeSize"] = 1

    def animatePolyrhythm(screen):
        updateSelectorSquezeSize(screen)
        animateGearRotation(screen)
        updateVolumeBarHeight(screen)

    def animateEnterDown(screen):
        moveSpeed = 20
        screen.topLeftY += moveSpeed
        if screen.topLeftY > 0:
            screen.topLeftY = 0
            screen.currentAnimationState = "animateNormalPos"
    

    def isMouseInsideBackButton(x, y, screen):
        rightMargin = appWidth/50
        headPokeOut = appWidth/50
        insideWidth = appWidth/30

        topMargin = appHeight/27
        headHeight = appHeight/24
        tailHeight = appHeight/20

        halfHeadWidth = headPokeOut + insideWidth/2

        if y <= appHeight - topMargin - headHeight: #rectangle case, on bottom edge is still inside!
            yInBounds = y > appHeight - topMargin - headHeight - tailHeight
            xInBounds = x > appWidth - rightMargin - headPokeOut - insideWidth and x < appWidth - rightMargin - headPokeOut
            return yInBounds and xInBounds
        else: #triangle case
            if x < appWidth - rightMargin - halfHeadWidth: #bound by the line y =  (tailHeight/halfHeadWidth)(x - (appWidth - rightMargin - halfHeadWidth)) + appHeight - topMargin
                return y < (tailHeight/halfHeadWidth)*(x - (appWidth - rightMargin - halfHeadWidth)) + appHeight - topMargin
            else: #bound by a line y =  -(tailHeight/halfHeadWidth)(x - (appWidth - rightMargin - halfHeadWidth)) + appHeight - topMargin
                return y < -(tailHeight/halfHeadWidth)*(x - (appWidth - rightMargin - halfHeadWidth)) + appHeight - topMargin
    
    backButtonHelper = HelpTextBox(0, 0, appWidth - appWidth/50 - appWidth/3, appHeight - appHeight/20 - appHeight/6,appWidth -  appWidth/50 , appHeight - appHeight/20 , "Use this button to go back and change the polyrhythm under study.", 4)


    def drawBackButton(canvas, x, y, screen):
        rightMargin = appWidth/50
        headPokeOut = appWidth/50
        insideWidth = appWidth/30

        topMargin = appHeight/27
        headHeight = appHeight/24
        tailHeight = appHeight/20

        canvas.create_polygon(x + appWidth - rightMargin - headPokeOut - insideWidth, y + appHeight - topMargin - headHeight - tailHeight, 
                                x + appWidth - rightMargin - headPokeOut, y + appHeight - topMargin - headHeight - tailHeight,
                                x + appWidth - rightMargin - headPokeOut, y + appHeight - topMargin - headHeight,
                                x + appWidth - rightMargin, y + appHeight - topMargin - headHeight,
                                x + appWidth - rightMargin - headPokeOut - insideWidth/2, y + appHeight - topMargin,
                                x + appWidth - rightMargin - headPokeOut - insideWidth - headPokeOut, y + appHeight - topMargin - headHeight,
                                x + appWidth - rightMargin - headPokeOut - insideWidth, y + appHeight - topMargin - headHeight,
                                fill = screen.eventControl["mouseInsideBackButton"][1], outline = "white")
    
    drawBackButtonObject = ObjectToDraw(0, 0, drawBackButton)


    def animateGearRotation(screen):
        if screen.eventControl["gearRotationAnimation"][1] and screen.eventControl["gearRotationAnimation"][0] + .3 <= np.pi:
            screen.eventControl["gearRotationAnimation"][0] += .3
        if (not screen.eventControl["gearRotationAnimation"][1]) and screen.eventControl["gearRotationAnimation"][0] - .3 >= 0:
            screen.eventControl["gearRotationAnimation"][0] -= .3

    def isMouseOverSettingsButton(x, y, screen):
        distanceFromBackButton = appWidth/15
        rightMargin = appWidth/50 + appWidth/50 + appWidth/30 + distanceFromBackButton
        outerRadius = appWidth/15
        topMargin = appHeight/50
        jumpIn = outerRadius*6/11
        actualRadius = outerRadius - jumpIn
        circleCenterX = appWidth - rightMargin - outerRadius
        circleCenterY = appHeight - topMargin - outerRadius
        distance = np.sqrt((x - circleCenterX)**2 + (y - circleCenterY)**2)
        return distance <= actualRadius



    def drawSettingsButton(canvas, x, y, screen):
        distanceFromBackButton = appWidth/15
        rightMargin = appWidth/50 + appWidth/50 + appWidth/30 + distanceFromBackButton
        outerRadius = appWidth/15

        topMargin = appHeight/50

        jumpIn = outerRadius*6/11
        nextJumpIn = outerRadius*3/4
        circleCenterX = x + appWidth - rightMargin - outerRadius
        circleCenterY = y + appHeight - topMargin - outerRadius

        canvas.create_oval(x + appWidth - rightMargin - 2*outerRadius + jumpIn,y + appHeight - topMargin - 2*outerRadius + jumpIn,
                           x + appWidth - rightMargin - jumpIn,y + appHeight - topMargin - jumpIn, outline = 'white', width = appWidth/100)

        numSpikes = 6
        spikeRadius = outerRadius - jumpIn
        for i in range(numSpikes):
            angle = i * (2*np.pi/(numSpikes)) + screen.eventControl["gearRotationAnimation"][0]
            
            secondaryAngle = (i + .5)*(2*np.pi)/numSpikes - .4*screen.eventControl["gearRotationAnimation"][0]
            canvas.create_line(circleCenterX + spikeRadius*np.cos(secondaryAngle), circleCenterY - spikeRadius*np.sin(secondaryAngle),
                                circleCenterX + 2*spikeRadius*np.cos(secondaryAngle), circleCenterY - 2*spikeRadius*np.sin(secondaryAngle), fill=  screen.eventControl["bgColor"], width = appWidth/100)
            
            canvas.create_line(circleCenterX, circleCenterY, 
                            circleCenterX + spikeRadius*np.cos(angle), circleCenterY - spikeRadius*np.sin(angle), fill = "white", width = appWidth/220)
            
        canvas.create_oval(x + appWidth - rightMargin - 2*outerRadius + nextJumpIn,y + appHeight - topMargin - 2*outerRadius + nextJumpIn,
                           x + appWidth - rightMargin - nextJumpIn,y + appHeight - topMargin - nextJumpIn, fill = 'white', outline = 'black', width = appWidth/240)

    settingsObject = ObjectToDraw(0, 0, drawSettingsButton)

    def drawVolumeBar(canvas, x, y, screen):
        volumeHeight = screen.eventControl["getVolumeHeight"][0]
        rectWidth = 40
        rectHeight = appWidth/8
        canvas.create_rectangle(x + appWidth/2 - rectWidth/2,y + appHeight/2 + rectHeight/2 - volumeHeight,
                                x + appWidth/2 + rectWidth/2,y +  appHeight/2 + rectHeight/2, fill = "green")
        canvas.create_line(x + appWidth/2 - rectWidth/2 - 20, y + appHeight/2 + rectHeight/2,
                                x + appWidth/2 + rectWidth/2 + 20, y + appHeight/2 + rectHeight/2, fill = "white")

    drawVolumeBarObject = ObjectToDraw(9*appWidth/10 + (appWidth/10 - 40)/2 - appWidth/2 + appWidth/40, 5*appHeight/408, drawVolumeBar)

    def drawTempoTextBox(canvas, x, y, screen):
        leftMargin = appWidth/20
        bottomMargin = appHeight/20
        boxLength = appWidth/9
        boxHeight = appHeight/18
        canvas.create_rectangle(x + leftMargin, y + appHeight - boxHeight - bottomMargin ,
                                x + leftMargin + boxLength, y + appWidth - bottomMargin, fill = "white")
        canvas.create_rectangle(x + leftMargin, y + appHeight - boxHeight - bottomMargin ,
                                x + leftMargin + boxLength, y + appWidth - bottomMargin, outline = screen.eventControl["mouseInsideTempoBox"][1])
        canvas.create_text(x + leftMargin + boxLength/2, y +  appWidth - (bottomMargin + boxHeight)*12/10, text = "Tempo", font = "Arial 16 bold", fill = "white")
        canvas.create_text(x + leftMargin + boxLength/2, y + appWidth - (bottomMargin) + -1*boxHeight/2, text = screen.eventControl["typedInsideTempoBox"][1], font = "Arial 22 bold")
    
    drawTempoTextBoxObject = ObjectToDraw(0, 0, drawTempoTextBox)

    def mouseInsideTempoBox(x, y, screen):
        leftMargin = appWidth/20
        bottomMargin = appHeight/20
        boxLength = appWidth/9
        boxHeight = appHeight/18
        if x > leftMargin and x < leftMargin + boxLength and y > appHeight - boxHeight - bottomMargin and y < appHeight - bottomMargin:
            return True
        return False
    
    tempoButtonHelper = HelpTextBox(0, 0, appWidth/20, appHeight*2/3, 4*appWidth/7, appHeight - appWidth/9 - appHeight/18, "Click in this box and type the desired quarter note pulse, which is the amount of time it takes the dot to move one row! Also explore the automated tempo mode in the app settings.", 2)

    #for all animations to use in this screen
    def updateVolumeBarHeight(screen):
        maxAmplitude = 32767/3 #we like it to be higher for even small volume inputs 
        #it's a better user experience (so we multiply the actual max by 3)
        rectHeight = appHeight/18
        screen.eventControl["getVolumeHeight"][0] = 2.5*np.abs((screen.eventControl["getVolumeHeight"][1]/(maxAmplitude))*rectHeight)

    def animateNormalPos(screen):
        updateVolumeBarHeight(screen)
        updateSelectorSquezeSize(screen)
        animateGearRotation(screen)

    def animateExitUp(screen):
        moveSpeed = 20
        screen.topLeftY -= moveSpeed
        if screen.topLeftY + appHeight < 0:
            screen.currentAnimationState = "animateNormalPos"
    
    def drawStreakCount(canvas, x, y, screen):
        if screen.eventControl["drawStreaks"]:
            upMargin = appHeight/20
            canvas.create_text(x + appWidth/2, y +upMargin, text = "streak: " + str(screen.eventControl["streak"]) + "  |  best streak: " + str(screen.eventControl["bestStreak"]), fill = "white", font = "Arial 22")
    drawStreakCountObject = ObjectToDraw(0, 0, drawStreakCount)


    def drawTapTempoBox(canvas, x, y, screen):
        leftMargin = appWidth/30
        upMargin = appHeight/25
        boxSideLength = appWidth/20
        canvas.create_text(x + leftMargin + boxSideLength/2 , y + upMargin/2, text = "Tap Tempo", fill = "white", font = "Arial 16")
        canvas.create_rectangle(x + leftMargin, y + upMargin, x + leftMargin + boxSideLength, y + upMargin + boxSideLength,
                                fill = screen.eventControl["isMouseInsideTapTempoBox"][1], outline = "black")
    drawTapTempoObject = ObjectToDraw(0, 0, drawTapTempoBox)


    tapTempoHelper = HelpTextBox(0 , 0, appWidth/30, appHeight/25, appWidth/30 + 3*appWidth/10, appHeight/25 + 2*appWidth/15, "Repeatedly tap what you wish to be the quarter note, which is however long it takes the dot to move one row!", 0)


    def isMouseInsideTapTempoBox(x, y, screen):
        leftMargin = appWidth/30
        upMargin = appHeight/25
        boxSideLength = appWidth/20
        return x > leftMargin and y > upMargin and x < leftMargin + boxSideLength and y < upMargin + boxSideLength


    defaultDotColors = [rgbColorString(140, 0, 0)] * (num1*num2)

    for x in range(num1*num2):
        if x % num2 == 0 and x % num1 == 0:
            defaultDotColors[x] = rgbColorString(0, 76, 76)
        elif x % num1 == 0:
            defaultDotColors[x] = rgbColorString(0, 76, 0)
        elif x % num2 == 0:
            defaultDotColors[x] = rgbColorString(0, 0, 76)

    dotColorsForAccuracy = defaultDotColors + []

    playedPositions = [] #contains tuples of (row, col, xMoveOver)
    
    def greenOrBlueToggleBox(x, y, screen):
        return isMouseInsideGreenToggleBox(x, y, screen) or isMouseInsideBlueToggleBox(x, y, screen)

    #helpBoxes has three things per help box, the function that checks for mouse position, the time the mouse has satisfied that function, and whether or not the mouse has last satisfied that function
    helpBoxes = [[isMouseInsideTapTempoBox, 0, False], [isMouseInsidePlayButton, 0, False], [mouseInsideTempoBox, 0, False], [greenOrBlueToggleBox, 0, False], [isMouseInsideBackButton, 0, False]]

    eventControl = {"isMouseInsidePlayButton":[isMouseInsidePlayButton, "green"], "currentDotSelector":0, "mouseInsideTempoBox":[mouseInsideTempoBox, "black"], "typedInsideTempoBox":[None, "120"], "animateStepActive":False, "getVolumeHeight":[0, 0], "dotColors": defaultDotColors, "dotColorsForAccuracy":dotColorsForAccuracy, "selectorSqueezeSize":1, "mouseInsideBackButton":[isMouseInsideBackButton,"darkred"], "gearRotationAnimation":[0, False, isMouseOverSettingsButton], "streak":0, "bestStreak":0, "drawStreaks":False, "isMouseInsideTapTempoBox":[isMouseInsideTapTempoBox, "yellow"], "isMouseInsideBlueToggleBox":[isMouseInsideBlueToggleBox, rgbColorString(0, 0, 180)], "isMouseInsideGreenToggleBox":[isMouseInsideGreenToggleBox, rgbColorString(0, 180, 0)], "dotPositionFractionalPart":0, "playedPositions":playedPositions, "bgColor":rgbColorString(0, 0, 0), "helpBoxes":helpBoxes}
    

    animationState = {"enterDown":animateEnterDown, "animateNormalPos":animateNormalPos, "animatePolyrhythm":animatePolyrhythm, "exitUp":animateExitUp}

    drawingObjects = [drawBgColorObject, drawNoteGridObject, drawPlayButtonObject, drawBlackTriangleObject, drawBlackSquareObject, drawTempoTextBoxObject, drawVolumeBarObject, drawBackButtonObject, settingsObject, drawStreakCountObject, drawTapTempoObject, drawGreenToggleBoxObj, drawBlueToggleBoxObj, tapTempoHelper, playButtonHelper, tempoButtonHelper, blueGreenTextBoxHelper, backButtonHelper]



    screen = Screen("Learn Polyrhythm Screen",drawingObjects, "enterDown", animationState, eventControl, 0, -1*appHeight)
    return screen    




def getSettingsScreen(appWidth, appHeight):
    
    def drawBackground(canvas, x, y, screen):
        canvas.create_rectangle(x, y, x + appWidth, y + appHeight, fill =  rgbColorString(30, 0, 30))
    bgDrawObject = ObjectToDraw(0, 0, drawBackground)

    def drawApplyButton(canvas, x, y, screen):
        width = appWidth/4
        height = appHeight/20
        upMargin = appHeight/14
        canvas.create_rectangle(x + appWidth/2 - width/2,y + appHeight - upMargin - height/2,
                                x + appWidth/2 + width/2,y + appHeight - upMargin + height/2, 
                                fill = screen.eventControl["applyButtonInfo"][1])
        canvas.create_text(x + appWidth/2, y + appHeight - upMargin, text = "Done", font = "Arial 22 bold")
    drawApplyButtonObject = ObjectToDraw(0, 0, drawApplyButton)

    def isMouseOverApplyButton(mouseX, mouseY, screen):
        width = appWidth/4
        height = appHeight/20
        upMargin = appHeight/14
        return mouseX > appWidth/2 - width/2 and mouseX < appWidth/2 + width/2 and mouseY > appHeight - upMargin - height/2 and mouseY < appHeight - upMargin + height/2


    def drawPreferencesTitle(canvas, x, y, screen):
        upMargin = appHeight/14
        canvas.create_text(x + appWidth/2, y + upMargin, text = "Preferences", font = "Arial 32 bold", fill = "white")
    drawPreferencesTitleObject = ObjectToDraw(0, 0, drawPreferencesTitle)    
    

    class Slider:
        def __init__(self, minimum, maximum, defaultVal):
            self.min = minimum
            self.max = maximum
            self.dotX = defaultVal #proportion
            self.value = defaultVal #val
            self.ovalRadius = appWidth/120
            self.overrideDotX = False #upon initialization we compute it this way but the override means the mouse dragging will directly set the dotX
        
        def drawSlider(self, canvas, start, stop, hardMax, hardMin): #slider cannot go past the hardMax and hardMin
            if not self.overrideDotX:
                dotPos = (self.dotX*(stop[0] - start[0]) + start[0] , start[1]) #kinda dumb but we are assuming a constant y value 
            else:
                if self.dotX < hardMin: self.dotX = hardMin
                if self.dotX > hardMax: self.dotX = hardMax
                dotPos = (self.dotX, start[1])
                self.value = ((self.dotX - start[0])/(stop[0] - start[0]))*(self.max - self.min) + self.min
            canvas.create_line(start[0], start[1], stop[0], stop[1], fill = "gold", width = appWidth/160)
            canvas.create_line(start[0], start[1], dotPos[0], dotPos[1], fill = "white", width = appWidth/160)
            canvas.create_oval(dotPos[0] - self.ovalRadius, dotPos[1] - self.ovalRadius,
                                dotPos[0] + self.ovalRadius, dotPos[1] + self.ovalRadius, fill = "gold", outline = "black")
            

    #it's too painful to not write it this way
    class PreferencesGrid:
        def __init__(self):
            self.rows = [] #will be a 2d list
            #each row in the list represents a different setting and each collumn in that row is a different 'option' for that setting, the actual data it stores are just strings of what each option is
            self.sideMargin = appWidth/20
            self.upMargin = appHeight/7
            self.downMargin = appHeight/7
            self.userInputRows = [] #tells the grid which rows the user interacts with by clicking and then typing inside, rather than having the row display a list of options

            #-------------- these are both updated via App.py 
            self.selected = [] #a 1d list, each entry represents one row of self.rows, and is the index of the one which should be highlighted, (displaying the current option that is enabled)
            self.hovered = [] #just two numbers, the row and col of the box the user has their mouse over. 

            self.sliders = [] #store the slider instances

        #here is a tricky method to write
        #given the mouse position, return the row and index of self.rows of the box the mouse is inside!
        def getSettingForMousePosition(self, mouseX, mouseY):
            totalGridHeight = appHeight - self.upMargin - self.downMargin
            deltaY = totalGridHeight/len(self.rows)
            totalGridLength = appWidth - 2*self.sideMargin
            titleWidth = totalGridLength/5
            if mouseX < self.sideMargin + titleWidth or mouseX > self.sideMargin + totalGridLength:
                return None
            rowIndex = int(((mouseY - self.upMargin) // deltaY))
            if rowIndex < 0 or rowIndex >= len(self.rows): #note in the grid
                return None
            deltaX = (totalGridLength - titleWidth)/(len(self.rows[rowIndex]) - 1)
            if mouseX < self.sideMargin + titleWidth:
                return (rowIndex, 0)
            colIndex = (mouseX - self.sideMargin - titleWidth) // deltaX
            return (rowIndex, colIndex)


        #a row consits of a text describing what the options change, and then the list of the text of the various options
        def addRow(self, descriptionText, options, currentSelected = None, slider = None):
            #assert(currentSelected == None or type(currentSelected) == int)

            if slider == None:
                self.rows.append([descriptionText] + options)
                if currentSelected == None: #currentSelected is None upon initialization of a row if and only if that row is a user input row
                    self.selected.append(currentSelected)
                    self.userInputRows.append(len(self.rows) - 1)
                else:
                    self.selected.append(currentSelected + 1) #+1 because the index is relative to our new array which has the name appended at the beginning
            else: #then slider is a Slider instance
                self.rows.append([descriptionText, ""]) #use "" to signal that we have a slider to place
                self.sliders.append(slider)
                self.selected.append(None)


        def drawGrid(self, canvas, xOffset, yOffset, screen):
            if len(self.rows) == 0:
                return
            y = yOffset + self.upMargin
            totalGridHeight = appHeight - self.upMargin - self.downMargin
            deltaY = totalGridHeight/len(self.rows)
            totalGridLength = appWidth - 2*self.sideMargin
            titleWidth = totalGridLength/5
            saveY = y
            sliderIndex = 0
            selectedIndex = 0
            for row in self.rows:
                if len(row) == 0:
                    continue
                drewTitle = False
                deltaX = (totalGridLength - titleWidth)/(len(row)-1)
                x = xOffset + self.sideMargin
                entryIndex = 0
                for entry in row:
                    fillColor = "black"
                    textColor = "white"
                    outlineColor = "white"
                    if entry == "": #slider!
                        slider = self.sliders[sliderIndex]
                        sliderY = y + deltaY/2
                        startX = x + deltaX/10
                        stopX = x + 9*deltaX/10 
                        canvas.create_rectangle(x, y, x + deltaX, y + deltaY, outline = "white", fill = "black")
                        slider.drawSlider(canvas, [startX, sliderY], [stopX, sliderY], stopX, startX)
                        canvas.create_text((stopX + x + deltaX)/2, sliderY, text = str(slider.max), font = "arial 12", fill = "white")
                        canvas.create_text((x + deltaX/20), sliderY, text = str(slider.min), font = "arial 12", fill = "white")
                        sliderIndex += 1
                        entryIndex += 1
                        continue
                    elif self.selected[selectedIndex] == entryIndex:
                        fillColor = "gold"
                        textColor = "black"
                    userInputData = screen.eventControl["justClickedInUserInput"]
                    if userInputData != None and userInputData[0] == selectedIndex and userInputData[1] == entryIndex - 1:
                        fillColor = "blue"
                    if drewTitle:
                        canvas.create_rectangle(x, y, x + deltaX, y + deltaY, outline = outlineColor, fill = fillColor)
                        canvas.create_text(x + deltaX/2, y + deltaY/2, text = entry, fill = textColor)
                        x += deltaX
                    elif entry != "": #not slider
                        canvas.create_rectangle(x, y, x + titleWidth, y + deltaY, outline = outlineColor, fill = fillColor)
                        canvas.create_text(x + titleWidth/2, y + deltaY/2, text = entry, fill = textColor)
                        x += titleWidth
                        drewTitle = True
                    entryIndex += 1
                y += deltaY
                selectedIndex += 1


            #line to divide the options from the titles of the options
            canvas.create_line(xOffset + self.sideMargin + titleWidth, saveY, 
                                xOffset + self.sideMargin + titleWidth, saveY + totalGridHeight, fill = "white", width = appHeight/150)

            if screen.currentAnimationState == "animateNormalPos" and len(self.hovered) > 1 and (self.selected[self.hovered[0]] == None or self.selected[self.hovered[0]] - 1 != self.hovered[1]): #the -1 is confusing but the reason it's there is because selected indecies are relative to the title, but hovered indecies are relative to the first non-title. yes there are also other confusing things about this if statement my b.
                deltaX = (totalGridLength - titleWidth)/(len(self.rows[self.hovered[0]]) - 1)
                deltaY = totalGridHeight/len(self.rows)
                x = self.hovered[1]*deltaX + self.sideMargin + titleWidth
                y = self.hovered[0]*deltaY + self.upMargin
                canvas.create_rectangle(x, y, x + deltaX, y + deltaY, outline = "gold")

        
    grid = PreferencesGrid()
    buttons = ["t", "n"]
    tempoFollowMode = ["On", "Off"]
    enableStreaks = ["On", "Off"]
    continuousLabel = ["On", "Off"]
    slowNotePitch = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    slowNoteOctave = ["1", "2", "3", "4", "5", "6", "7", "8"]
    slowNoteOscillators = ["sin", "triangle", "saw", "square"]
    fastNotePitch = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    fastNoteOctave = ["1", "2", "3", "4", "5", "6", "7", "8"]
    fastNoteOscillators = ["sin", "triangle", "saw", "square"]
    tempoNotePitch = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    tempoNoteOctave = ["1", "2", "3", "4", "5", "6", "7", "8"]
    tempoNoteOscillators = ["sin", "triangle", "saw", "square"]
    userInput1Pitch = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    userInput1Octave = ["1", "2", "3", "4", "5", "6", "7", "8"]
    userInput1Oscillators = ["sin", "triangle", "saw", "square"]
    userInput2Pitch = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    userInput2Octave = ["1", "2", "3", "4", "5", "6", "7", "8"]
    userInput2Oscillators = ["sin", "triangle", "saw", "square"]
    
    grid.addRow("controller options", buttons)
    grid.addRow("tempo follow mode", tempoFollowMode, 1)
    grid.addRow("enable streaks", enableStreaks, 0)
    grid.addRow("continuous label", continuousLabel, 0)
    grid.addRow("blue note pitch", slowNotePitch, 3)
    grid.addRow("blue note octave", slowNoteOctave, 2)
    grid.addRow("blue note oscillator", slowNoteOscillators, 1)
    grid.addRow("green note pitch", fastNotePitch, 7)
    grid.addRow("green note octave", fastNoteOctave, 2)
    grid.addRow("green note oscillator", slowNoteOscillators, 1)
    grid.addRow("red note pitch", tempoNotePitch, 0)
    grid.addRow("red note octave", tempoNoteOctave, 2)
    grid.addRow("red note oscillator", slowNoteOscillators, 1)
    grid.addRow("user input 1 pitch", userInput1Pitch, 10)
    grid.addRow("user input 1 octave", userInput1Octave, 2) 
    grid.addRow("user input 1 oscillator", userInput1Oscillators, 1)
    grid.addRow("user input 2 pitch", userInput2Pitch, 2)
    grid.addRow("user input 2 octave", userInput2Octave, 3) 
    grid.addRow("user input 2 oscillator", userInput2Oscillators, 1)
    grid.addRow("hover for instructions", ["On", "Off"], 0)
    grid.addRow("green note volume", None, None, Slider(0, 1, 1))
    grid.addRow("blue note volume",None, None, Slider(0, 1, 1))
    grid.addRow("red note volume", None, None, Slider(0, 1, 1))
    grid.addRow("user input 1 volume", None, None, Slider(0, 1, 1))
    grid.addRow("user input 2 volume", None, None, Slider(0, 1, 1))
    

    def drawPreferencesGrid(canvas, x, y, screen):
        grid.drawGrid(canvas, x, y, screen)
    drawPreferencesGridObject = ObjectToDraw(0, 0, drawPreferencesGrid)


    def animateEnterDown(screen):
        moveSpeed = 20
        screen.topLeftY -= moveSpeed
        if screen.topLeftY <= 0:
            screen.topLeftY = 0
            screen.currentAnimationState = "animateNormalPos"

    def animateExitDown(screen):
        moveSpeed = 20
        screen.topLeftY += moveSpeed
        if screen.topLeftY >= appHeight:
            screen.currentAnimationState = "animateNormalPos"
    
    def animateNormalPos(screen):
        pass

    animationState = {"enterDown":animateEnterDown, "animateNormalPos":animateNormalPos, "exitDown":animateExitDown}

    eventControl = {"settings":grid, "applyButtonInfo":[isMouseOverApplyButton, "white"], "justClickedInUserInput":None} #this is None if no click, but is the (row, col) of the controller option if it was clicked 

    screen = Screen("Settings Screen",[bgDrawObject, drawApplyButtonObject, drawPreferencesTitleObject, drawPreferencesGridObject], "enterDown", animationState, eventControl, 0, appHeight)

    return screen
