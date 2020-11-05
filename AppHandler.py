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
    titleScreen = Screen(completeObjectsToDraw, "pause", 
                        {"pause":animateNormalPos, "exit":animateExitTitleSlide},
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
        
    eventControl = {"mouseClickedInLeftBox":[clickedInLeftBox, "black"],
                    "mouseClickedInRightBox":[clickedInRightBox, "black"],
                    "typedInLeftBox":[None, ""],
                    "typedInRightBox":[None, ""]}


    screen = Screen([drawBgColorObject, drawPromptTextObject, drawAgainstTextObject, drawTextBoxesAndTextObject], "entrance", {"entrance":animateEntrance, "animateNormalPos":animateNormalPos}, eventControl, -1*appWidth)
    return screen

