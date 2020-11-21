import math, random

#utility functions -------------------------
#taken from 112 course website
def rgbColorString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'
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

#a particular screen in my program
#this just makes everything more organized
#make sure you pass in the objects to draw in the order you want them drawn
#animation states is a dictionary, mapping names to different possible states
#eventControl is a dictionary of pairs
#each 'pair' has a function to tell the outcome of an event, and then the next is the information that should change under that occurence
class Screen:
    def __init__(self, objectsToDraw, defaultAnimationState = None, animationStates = None, eventControl = None, screenTopLeftX = 0, screenTopLeftY = 0):
        self.eventControl = eventControl
        self.objectsToDraw = objectsToDraw
        self.animationStates = animationStates
        self.currentAnimationState = defaultAnimationState
        self.topLeftX, self.topLeftY = screenTopLeftX, screenTopLeftY

    def doAnimationStep(self):
        self.animationStates[self.currentAnimationState](self)

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
        r = abs(int(255*(x/appWidth)))
        g = 255 - r
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
    titleScreen = Screen(completeObjectsToDraw, "animateNormalPos", 
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
    animationStates = {"entrance":animateEntrance, "animateNormalPos":animateNormalPos, "exitDown":exitDownAnimation}

    objectsToDraw = [drawBgColorObject, drawPromptTextObject, drawAgainstTextObject, drawTextBoxesAndTextObject, drawGoBoxAndTextObject]
    
    startingAnimationState = "entrance"

    screen = Screen(objectsToDraw, startingAnimationState, animationStates, eventControl, -1*appWidth)
    return screen

#num1 and num2 are the two numbers that will create the polyrhythm!
def getLearnPolyrhythmScreen(appWidth, appHeight, num1, num2):

    def drawBgColor(canvas, x, y, screen):
        canvas.create_rectangle(x, y, x + appWidth, y + appHeight, fill = "black")
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
                circleColor = 'darkred'
                if (num2*row + col) % num1 == 0:
                    circleColor = 'darkgreen'
                if col == 0:
                    circleColor = 'darkblue'
                    if row == 0: circleColor = 'turquoise'
                
                if screen.eventControl["currentDotSelector"] == num2*row + col:
                    newJumpIn = 3*jumpIn/8
                    canvas.create_oval(xCoord + newJumpIn, yCoord + newJumpIn, xCoord + gridSize - newJumpIn, yCoord + gridSize - newJumpIn, outline = "white" )
                canvas.create_oval(xCoord + jumpIn, yCoord + jumpIn, xCoord + gridSize - jumpIn, yCoord + gridSize - jumpIn,
                fill = circleColor, outline = "black")
    drawNoteGridObject = ObjectToDraw(0, 0, drawNoteGrid)

    def animatePolyrhythm(screen):
        if screen.eventControl["animateStepActive"]:
            screen.eventControl["currentDotSelector"] += 1
            if screen.eventControl["currentDotSelector"] == num1*num2:
                screen.eventControl["currentDotSelector"] = 0
            screen.eventControl["animateStepActive"] = False

    def animateEnterDown(screen):
        moveSpeed = 20
        screen.topLeftY += moveSpeed
        if screen.topLeftY > 0:
            screen.topLeftY = 0
            screen.currentAnimationState = "animateNormalPos"
    

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

    def animateNormalPos(screen):
        pass

    eventControl = {"isMouseInsidePlayButton":[isMouseInsidePlayButton, "green"], "currentDotSelector":0, "mouseInsideTempoBox":[mouseInsideTempoBox, "black"], "typedInsideTempoBox":[None, "120"], "animateStepActive":False}
    

    animationState = {"enterDown":animateEnterDown, "animateNormalPos":animateNormalPos, "animatePolyrhythm":animatePolyrhythm}

    drawingObjects = [drawBgColorObject, drawNoteGridObject, drawPlayButtonObject, drawBlackTriangleObject, drawBlackSquareObject, drawTempoTextBoxObject]



    screen = Screen(drawingObjects, "enterDown", animationState, eventControl, 0, -1*appHeight)
    return screen    

