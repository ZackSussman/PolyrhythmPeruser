from cmu_112_graphics import * #cmu 112 graphics taken from the course website
import AppUI as ui
import Synth
import pyaudio, numpy as np

class MainApp(App):
    def appStarted(self):
        self.titleScreen = ui.getTitleScreen(self.width, self.height)
        self.currentScreens = [self.titleScreen]
        self.promptUserScreen = ui.getPromptUserScreen(self.width, self.height)
        self.preferencesScreen = ui.getSettingsScreen(self.width, self.height)
        self.learnPolyrhythmScreen = None #initialize to None because we don't know what the polyrhythm is yet
        
        self.polyrhythmStartTime = None #polyrhythm hasn't started yet
        self.numClicksSinceStart = 0 #haven't started yet

        #-----the following variables are used to keep track of polyrhythm data along with user input

        self.rhythmIndex = 0 #the index of the next note to be played
        self.timePerSubPulse = None #we can't compute this yet but it will be updated
        #the subpulse time is the time per miniclick that should be felt underneath the polyrhythm, being played by countSynth

        self.timeSinceStart = 0 #keeps track of the elapsed time over which the polyrhythm has been playing since the first press of the play button
        self.timeAtLastNote = 0 #the time at which the most recent note was struck

        self.hasUserTappedNote = False #tells us whether or not to listen to user input for the current note to be played
        
        self.justDetectedAMiddlePoint = False #set this to true when we detect a midpoint. This way when we stop decteding it we know when was the FIRST time we stopped detecting it. 

        self.initializeAudio()
        self.initializeVolumeBarParameters()
    
    def initializeVolumeBarParameters(self):
        self.faderSpeed = .9
        self.hitTolerance = self.maxAmplitude/100

    def appStopped(self):
        self.outputStream.stop_stream()
        self.pyAudio.terminate()

    def initializeAudio(self):
        #------------------------------------------- consts
        framesPerBuffer = 2**6 #samples per buffer
        channels = 1
        rate = 48000 #samples per second
        dType = pyaudio.paInt16 #for pyaudio
        self.dtype = np.int16 #for numpy
        self.maxAmplitude = 32767 #paInt16
        self.timePerBuffer = framesPerBuffer/rate 
        #-------------------------------------------

        #------------------------------------------ initialize synth
        self.slowSynth = Synth.Synthesizer(520, rate, (2* np.pi, np.sin), framesPerBuffer, self.dtype, self.maxAmplitude/3)
        self.fastSynth = Synth.Synthesizer(520*(3/2), rate, (2* np.pi, np.sin), framesPerBuffer, self.dtype, self.maxAmplitude/3)
        self.countSynth = Synth.Synthesizer(520*(6/15), rate, (2* np.pi, np.sin), framesPerBuffer, self.dtype, self.maxAmplitude/15)
        #------------------------------------------


        self.pyAudio = pyaudio.PyAudio()
        #---------------------------------------- setup output stream
        self.outputStream = self.pyAudio.open(
                format = dType,
                channels = channels,
                rate = rate,
                output = True,
                frames_per_buffer = framesPerBuffer,
                stream_callback = self.outputAudioStreamCallback
            )
        self.outputStream.start_stream()
        #----------------------------------------
        #---------------------------------------- setup input stream
        self.inputStream = self.pyAudio.open(
            format = dType,
            channels = channels,
            rate = rate,
            input = True,
            frames_per_buffer = framesPerBuffer,
            stream_callback = self.inputAudioStreamCallback
        )
        self.inputStream.start_stream()
        #------------------------------------------
       


    def outputAudioStreamCallback(self, inputAudio, frameCount, timeInfo, status):
        if self.learnPolyrhythmScreen in self.currentScreens and self.learnPolyrhythmScreen.currentAnimationState == 'animatePolyrhythm':
            num1, num2 = self.getPolyrhythm()
            if self.timeSinceStart >= self.timeAtLastNote + self.timePerSubPulse:
                self.timeAtLastNote = self.timeSinceStart
               
                if self.rhythmIndex != 0: #if we do this from the start the dot will always be one move ahead
                    self.learnPolyrhythmScreen.eventControl["animateStepActive"] = True
                
                self.countSynth.createHit()
                if self.rhythmIndex % num2 == 0:
                    self.fastSynth.createHit()
                if self.rhythmIndex % num1 == 0:
                    self.slowSynth.createHit()

                self.rhythmIndex += 1
            
            #the way we test for a switchover causes it to be True way too many times so this mechanism ensures we only get a single call
            if self.testForSwitchoverToNewNote():
                self.justDetectedAMiddlePoint = True
            elif self.justDetectedAMiddlePoint:
                if self.hasUserTappedNote == False: #they completely missed the note!
                    self.updateNoteColor(self.timePerSubPulse, self.getPastRhythmClick())
                self.hasUserTappedNote = False
                self.justDetectedAMiddlePoint = False



            self.timeSinceStart += self.timePerBuffer


        slowSynthData = self.slowSynth.getAudioData()
        fastSynthData = self.fastSynth.getAudioData()
        countSynthData = self.countSynth.getAudioData()
        data = slowSynthData + fastSynthData + countSynthData
        return (data, pyaudio.paContinue)    
        

    

    def inputAudioStreamCallback(self, inputAudio, frameCount, timeInfo, status):
        if self.learnPolyrhythmScreen in self.currentScreens:
            newAudioInData = np.frombuffer(inputAudio, dtype = self.dtype)
            lastMaxValue = self.learnPolyrhythmScreen.eventControl["getVolumeHeight"][1]
            volumeScale = np.max(newAudioInData)
            if volumeScale - lastMaxValue > self.hitTolerance:
                lastMaxValue = volumeScale
            else:
                lastMaxValue = self.faderSpeed*(lastMaxValue)
            self.learnPolyrhythmScreen.eventControl["getVolumeHeight"][1] = lastMaxValue
        return (inputAudio, pyaudio.paContinue)

    def timerFired(self):
        for screen in self.currentScreens:
            screen.doAnimationStep()
        if self.currentScreens[-1].currentAnimationState == "animateNormalPos":
            self.currentScreens = [self.currentScreens[-1]]

    def mouseMoved(self, event):
        if self.titleScreen in self.currentScreens and self.titleScreen.currentAnimationState == "animateNormalPos":
            if self.titleScreen.eventControl["isMouseInsideBeginBox"][0](event.x, event.y, self.titleScreen):
                self.titleScreen.eventControl["isMouseInsideBeginBox"][1] = "yellow"
            else:
                self.titleScreen.eventControl["isMouseInsideBeginBox"][1] = "gold"
        if self.promptUserScreen in self.currentScreens and self.promptUserScreen.currentAnimationState == "animateNormalPos":
            if self.promptUserScreen.eventControl["mouseInsideGoBox"][0](event.x, event.y, self.promptUserScreen):
                self.promptUserScreen.eventControl["mouseInsideGoBox"][1] = "yellow"
            else:
                self.promptUserScreen.eventControl["mouseInsideGoBox"][1] = "gold"
        if self.learnPolyrhythmScreen in self.currentScreens and self.learnPolyrhythmScreen.currentAnimationState in  ["animateNormalPos", "animatePolyrhythm"]:
            if self.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][1] = "limegreen"
            else:
                self.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][1] = "green"
            if self.learnPolyrhythmScreen.eventControl["mouseInsideBackButton"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.learnPolyrhythmScreen.eventControl["mouseInsideBackButton"][1] = "red"
            else:
                self.learnPolyrhythmScreen.eventControl["mouseInsideBackButton"][1] = "darkred"
            
            if self.learnPolyrhythmScreen.eventControl["gearRotationAnimation"][2](event.x, event.y, self.learnPolyrhythmScreen):
                self.learnPolyrhythmScreen.eventControl["gearRotationAnimation"][1] = True
            else:
                self.learnPolyrhythmScreen.eventControl["gearRotationAnimation"][1] = False
        if self.preferencesScreen in self.currentScreens and self.preferencesScreen.currentAnimationState == "animateNormalPos":
            grid = self.preferencesScreen.eventControl["settings"]
            result = grid.getSettingForMousePosition(event.x, event.y)
            if result != None:
                grid.hovered = [result[0], result[1]]
            else:
                grid.hovered = []
            if self.preferencesScreen.eventControl["applyButtonInfo"][0](event.x, event.y, self.preferencesScreen):
                self.preferencesScreen.eventControl["applyButtonInfo"][1] = "gold"
            else:
                self.preferencesScreen.eventControl["applyButtonInfo"][1] = "white"
            
            

    def mousePressed(self, event):
        if self.titleScreen in self.currentScreens and self.titleScreen.currentAnimationState == "animateNormalPos":
            if self.titleScreen.eventControl["isMouseInsideBeginBox"][0](event.x, event.y, self.titleScreen):
                self.titleScreen.currentAnimationState = "exit"
                self.currentScreens.append(self.promptUserScreen)
        if self.promptUserScreen in self.currentScreens and self.promptUserScreen.currentAnimationState == "animateNormalPos":
            if self.promptUserScreen.eventControl["mouseClickedInLeftBox"][0](event.x, event.y, self.promptUserScreen):
                if self.promptUserScreen.currentAnimationState == "animateNormalPos":
                    self.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] = "gold"
            else:
                self.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] = "black"
            if self.promptUserScreen.eventControl["mouseClickedInRightBox"][0](event.x, event.y, self.promptUserScreen):
                if self.promptUserScreen.currentAnimationState == "animateNormalPos":
                    self.promptUserScreen.eventControl["mouseClickedInRightBox"][1] = "gold"
            else:
                self.promptUserScreen.eventControl["mouseClickedInRightBox"][1] = "black"
            if self.promptUserScreen.eventControl["mouseInsideGoBox"][0](event.x, event.y, self.promptUserScreen):
                if self.promptUserScreen.eventControl["typedInLeftBox"][1] != "" and self.promptUserScreen.eventControl["typedInRightBox"][1] != "":
                    num1, num2 = self.getPolyrhythm()
                    if num1 != 0 and num2 != 0:
                        self.learnPolyrhythmScreen = ui.getLearnPolyrhythmScreen(self.width, self.height, num2, num1)
                        self.promptUserScreen.currentAnimationState = "exitDown"
                        self.currentScreens.append(self.learnPolyrhythmScreen)
                        self.handleTempoChange() #this can also initialize tempo related variables
        if self.learnPolyrhythmScreen in self.currentScreens:
            if self.learnPolyrhythmScreen.eventControl["mouseInsideBackButton"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.learnPolyrhythmScreen.currentAnimationState = "exitUp"
                self.resetPolyrhythmAttributes() #reset everything polyrhythm related to prepare for a new rhythm
                self.currentScreens.append(self.promptUserScreen)
                self.promptUserScreen.topLeftY = self.height
                self.promptUserScreen.currentAnimationState = "enterUp"
                self.learnPolyrhythmScreen.eventControl["mouseInsideBackButton"][1] = "darkred"
        if self.learnPolyrhythmScreen in self.currentScreens and self.learnPolyrhythmScreen.currentAnimationState in ["animateNormalPos", "animatePolyrhythm"]:
            if self.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.handlePlayPause()
            if self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "gold"
            else:
                self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "black"
                self.handleTempoChange()
            if self.learnPolyrhythmScreen.eventControl["gearRotationAnimation"][2](event.x, event.y, self.learnPolyrhythmScreen):
                self.currentScreens.append(self.preferencesScreen)
                self.preferencesScreen.currentAnimationState = "enterDown"
                self.learnPolyrhythmScreen.currentAnimationState = "exitUp"
                self.resetPolyrhythmAttributes()
        if self.preferencesScreen in self.currentScreens and self.preferencesScreen.currentAnimationState == "animateNormalPos":
            grid = self.preferencesScreen.eventControl["settings"]
            result = grid.getSettingForMousePosition(event.x, event.y)
            if result != None:
                if grid.selected[result[0]] != None:
                    grid.selected[result[0]] = result[1] + 1
            if self.preferencesScreen.eventControl["applyButtonInfo"][0](event.x, event.y, self.preferencesScreen):
                self.preferencesScreen.currentAnimationState = "exitDown"
                self.currentScreens.append(self.learnPolyrhythmScreen)
                self.learnPolyrhythmScreen.currentAnimationState = "enterDown"
                
    
    def resetPolyrhythmAttributes(self):
        self.timeSinceStart = 0
        self.rhythmIndex = 0
        self.timeAtLastNote = 0
        self.slowSynth.turnNoteOff()
        self.fastSynth.turnNoteOff()
        self.countSynth.turnNoteOff()
        self.hasUserTappedNote = False
        self.justDetectedAMiddlePoint = False 

    def keyPressed(self, event):
        if self.promptUserScreen in self.currentScreens:
            if not event.key.isnumeric() and event.key != "Delete":
                return
            if self.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] == "gold":
                if event.key == "Delete":
                    self.promptUserScreen.eventControl["typedInLeftBox"][1] = self.promptUserScreen.eventControl["typedInLeftBox"][1][:-1]
                    return
                if len(self.promptUserScreen.eventControl["typedInLeftBox"][1]) < 5:
                    self.promptUserScreen.eventControl["typedInLeftBox"][1] += event.key
            elif self.promptUserScreen.eventControl["mouseClickedInRightBox"][1] == "gold":
                if event.key == "Delete":
                    self.promptUserScreen.eventControl["typedInRightBox"][1] = self.promptUserScreen.eventControl["typedInRightBox"][1][:-1]
                    return
                if len(self.promptUserScreen.eventControl["typedInRightBox"][1]) < 5:
                    self.promptUserScreen.eventControl["typedInRightBox"][1] += event.key
        if self.learnPolyrhythmScreen in self.currentScreens:
            if not event.key.isnumeric() and event.key != "Delete" and event.key != "Space" and event.key != 'n' and event.key != 't' and event.key != 'Enter':
                return
            if self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] == "gold" and event.key != "Space" and event.key != "Enter":
                if event.key == "Delete":
                    self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] = self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1][:-1]
                    return
                if len(self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1]) < 5:
                    self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] += event.key
            elif event.key == "Space":
                if self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] != "gold" and self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] != "":
                    self.handlePlayPause()
            if self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] != "" and event.key == "Enter" and self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] == "gold":
                self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "black"
                self.handleTempoChange()
            if self.learnPolyrhythmScreen.currentAnimationState == "animatePolyrhythm" and event.key != "Space" and event.key != "Enter" :
                self.handleUserDrumming(event.key)
    
    #simply test to see if it is time to reset the state of whether the user tried to press the note
    def testForSwitchoverToNewNote(self):
        num1, num2 = self.getPolyrhythm()
        timeToPastClick = self.timeSinceStart - self.timeAtLastNote #at this note, rhythmIndex was the current rhythmIndex - 1
        timeToNextClick = self.timeAtLastNote + self.timePerSubPulse - self.timeSinceStart #at this note, rhythmIndex will be the current rhythmIndex

        pastRhythmClick = self.getPastRhythmClick()
        nextRhythmClick = self.getNextRhythmClick()



        timeToPastRhythmClick = timeToPastClick + self.timePerSubPulse*(self.rhythmIndex - 1 - pastRhythmClick)
        timeToNextRhythmClick = timeToNextClick + self.timePerSubPulse*(nextRhythmClick - self.rhythmIndex)

        return ui.almostEqual(timeToPastRhythmClick, timeToNextRhythmClick)

    def handleUserDrumming(self, input):
        self.learnPolyrhythmScreen.eventControl["selectorSqueezeSize"] = .75
        num1, num2 = self.getPolyrhythm()
        timeToPastClick = self.timeSinceStart - self.timeAtLastNote #at this note, rhythmIndex was the current rhythmIndex - 1
        timeToNextClick = self.timeAtLastNote + self.timePerSubPulse - self.timeSinceStart #at this note, rhythmIndex will be the current rhythmIndex
        pastRhythmClick = self.getPastRhythmClick() #get the index of the last sub pulse which was played as part of the polyrhythm
        nextRhythmClick = self.getNextRhythmClick() #get the index of the next sub pulse which was played as part of the polyrhythm
        timeToPastRhythmClick = timeToPastClick + self.timePerSubPulse*(self.rhythmIndex - 1 - pastRhythmClick)
        timeToNextRhythmClick = timeToNextClick + self.timePerSubPulse*(nextRhythmClick - self.rhythmIndex)
        timeToUse = None
        indexToUse = None
        if timeToNextRhythmClick < timeToPastRhythmClick:
            timeToUse = timeToNextRhythmClick
            indexToUse = nextRhythmClick
        else:
            timeToUse = timeToPastRhythmClick
            indexToUse = pastRhythmClick
        if not self.hasUserTappedNote:
            self.hasUserTappedNote = True
            self.updateNoteColor(timeToUse, indexToUse)





    #return the index of the last note which was played
    def getPastRhythmClick(self):
        num1, num2 = self.getPolyrhythm()
        start = self.rhythmIndex - 1
        while start % num1 != 0 and start % num2 != 0:
            start -= 1
        return start

    #return the index of the next note which will be played
    def getNextRhythmClick(self):
        num1, num2 = self.getPolyrhythm()
        start = self.rhythmIndex
        while start % num1 != 0 and start % num2 != 0:
            start += 1
        return start

 



    def updateNoteColor(self, time, noteIndex):
        time -= 10*self.timePerBuffer #account for latency
        self.hasUserTappedNote = True
        num1, num2 = self.getPolyrhythm()
        assert(noteIndex % num1 == 0 or noteIndex % num2 == 0)
        time = abs(time)

        colorValue = None
        if time > self.timePerSubPulse/2: time = self.timePerSubPulse/2
        if self.timePerSubPulse >  0.08: #this value was found through testing 
            #in the worst case here the user must tap .125/4 seconds of the beat to hear feedback
            #we convert the time to a color value from 0 to 255, the maximum time is half the sub pulse time
            #multiply by .3 so it can never go completly black
            colorValue = int(255*(1 - .7*((time/(self.timePerSubPulse/2))**3)))
        else:
            #the beat is VERY fast so we ease up a bit on the algorithm for computing brightness to allow for more lax feedback
            colorValue = int(255*(1 - .7*((time/(self.timePerSubPulse/2))**5)))


        noteIndex %= (num1*num2)
        currentColor = ui.inverseRgbColorString(self.learnPolyrhythmScreen.eventControl["dotColors"][noteIndex])
        if currentColor[1] == 0: #then the color looks like (0, 0, x)
            currentColor = (0, 0, colorValue)
        elif currentColor[2] == 0: #then the color looks like (0, x, 0)
            currentColor = (0, colorValue, 0)
        else: #color looks like (0, x, x)
            currentColor = (0, colorValue, colorValue)
        self.learnPolyrhythmScreen.eventControl["dotColors"][noteIndex] = ui.rgbColorString(currentColor[0], currentColor[1], currentColor[2])






    #called whenever the play or paused button (same button) is pressed
    #manage the events of turning off and on the sound and animation
    def handlePlayPause(self):
        if self.learnPolyrhythmScreen.currentAnimationState == "animateNormalPos":
            self.learnPolyrhythmScreen.currentAnimationState = "animatePolyrhythm"
        else:
            self.learnPolyrhythmScreen.currentAnimationState = "animateNormalPos"
            self.fastSynth.turnNoteOff()
            self.slowSynth.turnNoteOff()



    #----------------------------------- these methods handle updates to variables when a tempo change happens
    def handleTempoChange(self):
        self.updateTimePerSubPulse()

    def updateTimePerSubPulse(self):
        tempo = int(self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1])
        if tempo != 0:
            num2, num1 = self.getPolyrhythm()
            #num1 is the slower note, and we want its pulse to match the quarter note, which is given by the tempo
            timePerQuarterNote = (1/tempo)*(60)
            timePerSlowNote = timePerQuarterNote
            #the rhythm consits of the slow note happening num1 times and the fast note happening num2 times
            #the total number of mini clicks in the whole duration is num1*num2
            #so we must have num1*num2*(miniClick time) = num1*(timePerSlowNote)
            #this is how we find the miniClick time
            self.timePerSubPulse = timePerSlowNote/num2

    #---------------------------------------------------------------------------


    #get the current polyrhythm
    def getPolyrhythm(self):
        num1 = int(self.promptUserScreen.eventControl["typedInRightBox"][1])
        num2 = int(self.promptUserScreen.eventControl["typedInLeftBox"][1])
        return num1, num2
            


    def redrawAll(self, canvas):
        for screen in self.currentScreens:
            screen.drawScreen(canvas)


appRunner = MainApp(width = 800, height = 800, mvcCheck = False)

