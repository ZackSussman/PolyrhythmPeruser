from cmu_112_graphics import *
import AppHandler as handler

def appStarted(app):
    app.titleScreen = handler.getTitleScreen(app.width, app.height)
    app.currentScreens = [app.titleScreen]
    app.promptUserScreen = handler.getPromptUserScreen(app.width, app.height)
    app.learnPolyrhythmScreen = None #initialize to None because we don't know what the polyrhythm is yet
    
def timerFired(app):
    for screen in app.currentScreens:
        screen.doAnimationStep()
    if app.currentScreens[-1].currentAnimationState == "animateNormalPos":
        app.currentScreens = [app.currentScreens[-1]]

def mouseMoved(app, event):
    if app.titleScreen in app.currentScreens and app.titleScreen.currentAnimationState == "animateNormalPos":
        if app.titleScreen.eventControl["isMouseInsideBeginBox"][0](event.x, event.y, app.titleScreen):
            app.titleScreen.eventControl["isMouseInsideBeginBox"][1] = "yellow"
        else:
            app.titleScreen.eventControl["isMouseInsideBeginBox"][1] = "gold"
    if app.promptUserScreen in app.currentScreens and app.promptUserScreen.currentAnimationState == "animateNormalPos":
        if app.promptUserScreen.eventControl["mouseInsideGoBox"][0](event.x, event.y, app.promptUserScreen):
            app.promptUserScreen.eventControl["mouseInsideGoBox"][1] = "yellow"
        else:
            app.promptUserScreen.eventControl["mouseInsideGoBox"][1] = "gold"
    if app.learnPolyrhythmScreen in app.currentScreens and app.learnPolyrhythmScreen.currentAnimationState in  ["animateNormalPos", "animatePolyrhythm"]:
        if app.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][0](event.x, event.y, app.learnPolyrhythmScreen):
            app.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][1] = "limegreen"
        else:
            app.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][1] = "green"

def mousePressed(app, event):
    if app.titleScreen in app.currentScreens and app.titleScreen.currentAnimationState == "animateNormalPos":
        if app.titleScreen.eventControl["isMouseInsideBeginBox"][0](event.x, event.y, app.titleScreen):
            app.titleScreen.currentAnimationState = "exit"
            app.currentScreens.append(app.promptUserScreen)
    if app.promptUserScreen in app.currentScreens and app.promptUserScreen.currentAnimationState == "animateNormalPos":
        if app.promptUserScreen.eventControl["mouseClickedInLeftBox"][0](event.x, event.y, app.promptUserScreen):
            if app.promptUserScreen.currentAnimationState == "animateNormalPos":
                app.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] = "gold"
        else:
            app.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] = "black"
        if app.promptUserScreen.eventControl["mouseClickedInRightBox"][0](event.x, event.y, app.promptUserScreen):
            if app.promptUserScreen.currentAnimationState == "animateNormalPos":
                app.promptUserScreen.eventControl["mouseClickedInRightBox"][1] = "gold"
        else:
            app.promptUserScreen.eventControl["mouseClickedInRightBox"][1] = "black"
        if app.promptUserScreen.eventControl["mouseInsideGoBox"][0](event.x, event.y, app.promptUserScreen):
            if app.promptUserScreen.eventControl["typedInLeftBox"][1] != "" and app.promptUserScreen.eventControl["typedInRightBox"][1] != "":
                num1 = int(app.promptUserScreen.eventControl["typedInLeftBox"][1])
                num2 = int(app.promptUserScreen.eventControl["typedInRightBox"][1])
                app.promptUserScreen.currentAnimationState = "exitDown"
                app.learnPolyrhythmScreen = handler.getLearnPolyrhythmScreen(app.width, app.height, num2, num1)
                app.currentScreens.append(app.learnPolyrhythmScreen)
    if app.learnPolyrhythmScreen in app.currentScreens and app.learnPolyrhythmScreen.currentAnimationState in ["animateNormalPos", "animatePolyrhythm"]:
        if app.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][0](event.x, event.y, app.learnPolyrhythmScreen):
            if app.learnPolyrhythmScreen.currentAnimationState == "animateNormalPos":
                app.learnPolyrhythmScreen.currentAnimationState = "animatePolyrhythm"
            else:
                app.learnPolyrhythmScreen.currentAnimationState = "animateNormalPos"
        if app.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][0](event.x, event.y, app.learnPolyrhythmScreen):
            app.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "gold"
        else:
            app.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "black"
                
        
def keyPressed(app, event):
    if app.promptUserScreen in app.currentScreens:
        if not event.key.isnumeric() and event.key != "Delete":
            return
        if app.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] == "gold":
            if event.key == "Delete":
                app.promptUserScreen.eventControl["typedInLeftBox"][1] = app.promptUserScreen.eventControl["typedInLeftBox"][1][:-1]
                return
            if len(app.promptUserScreen.eventControl["typedInLeftBox"][1]) < 5:
                app.promptUserScreen.eventControl["typedInLeftBox"][1] += event.key
        elif app.promptUserScreen.eventControl["mouseClickedInRightBox"][1] == "gold":
            if event.key == "Delete":
                app.promptUserScreen.eventControl["typedInRightBox"][1] = app.promptUserScreen.eventControl["typedInRightBox"][1][:-1]
                return
            if len(app.promptUserScreen.eventControl["typedInRightBox"][1]) < 5:
                app.promptUserScreen.eventControl["typedInRightBox"][1] += event.key
    if app.learnPolyrhythmScreen in app.currentScreens:
        if not event.key.isnumeric() and event.key != "Delete":
            return
        if app.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] == "gold":
            if event.key == "Delete":
                app.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] = app.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1][:-1]
                return
            if len(app.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1]) < 5:
                app.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] += event.key
            
            if app.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] != "":
                tempo = int(app.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1])
                timerFiresPerQuarterNote = int(app.promptUserScreen.eventControl["typedInLeftBox"][1])
                miliSecondsPerQuarterNote = (1/tempo)*(60)*(1000)
                app.timerDelay = int(miliSecondsPerQuarterNote/timerFiresPerQuarterNote)
            

def redrawAll(app, canvas):
    for screen in app.currentScreens:
        screen.drawScreen(canvas)

runApp(width = 800, height = 800)

