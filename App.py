from cmu_112_graphics import *
import AppHandler as handler

def appStarted(app):
    app.titleScreen = handler.getTitleScreen(app.width, app.height)
    app.currentScreens = [app.titleScreen]
    app.promptUserScreen = handler.getPromptUserScreen(app.width, app.height)

def timerFired(app):
    if len(app.currentScreens) > 1:
        x = 2 + 2
    for screen in app.currentScreens:
        screen.doAnimationStep()

def mouseMoved(app, event):
    if app.titleScreen.eventControl["isMouseInsideBeginBox"][0](event.x, event.y, app.titleScreen):
        app.titleScreen.eventControl["isMouseInsideBeginBox"][1] = "yellow"
    else:
        app.titleScreen.eventControl["isMouseInsideBeginBox"][1] = "gold"

def mousePressed(app, event):
    if app.titleScreen in app.currentScreens:
        if app.titleScreen.eventControl["isMouseInsideBeginBox"][0](event.x, event.y, app.titleScreen):
            app.titleScreen.currentAnimationState = "exit"
            app.currentScreens.append(app.promptUserScreen)
    if app.promptUserScreen in app.currentScreens:
        if app.promptUserScreen.eventControl["mouseClickedInLeftBox"][0](event.x, event.y, app.promptUserScreen):
            app.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] = "gold"
        else:
            app.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] = "black"
        if app.promptUserScreen.eventControl["mouseClickedInRightBox"][0](event.x, event.y, app.promptUserScreen):
            app.promptUserScreen.eventControl["mouseClickedInRightBox"][1] = "gold"
        else:
            app.promptUserScreen.eventControl["mouseClickedInRightBox"][1] = "black"
        
    

def keyPressed(app, event):
    if app.promptUserScreen in app.currentScreens:
        if not event.key.isnumeric() and event.key != "Delete":
            return
        if app.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] == "gold":
            if event.key == "Delete":
                app.promptUserScreen.eventControl["typedInLeftBox"][1] = app.promptUserScreen.eventControl["typedInLeftBox"][1][:-1]
                return
            app.promptUserScreen.eventControl["typedInLeftBox"][1] += event.key
        elif app.promptUserScreen.eventControl["mouseClickedInRightBox"][1] == "gold":
            if event.key == "Delete":
                app.promptUserScreen.eventControl["typedInRightBox"][1] = app.promptUserScreen.eventControl["typedInRightBox"][1][:-1]
                return
            app.promptUserScreen.eventControl["typedInRightBox"][1] += event.key

def redrawAll(app, canvas):
    for screen in app.currentScreens:
        screen.drawScreen(canvas)

runApp(width = 800, height = 800)

