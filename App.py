from cmu_112_graphics import * #cmu 112 graphics taken from the course website
import AppHandler as handler
import time
import Synth
import pyaudio, numpy as np

class MainApp(App):
    def appStarted(self):
        self.titleScreen = handler.getTitleScreen(self.width, self.height)
        self.currentScreens = [self.titleScreen]
        self.promptUserScreen = handler.getPromptUserScreen(self.width, self.height)
        self.learnPolyrhythmScreen = None #initialize to None because we don't know what the polyrhythm is yet
        
        
        self.polyrhythmStartTime = None #polyrhythm hasn't started yet
        self.numClicksSinceStart = 0 #haven't started yet

        #-----the following variables are used to keep track of polyrhythm data along with user input

        self.rhythmIndex = 0 #the number of subPulses that we have had so far
        self.timePerSubPulse = None #we can't compute this yet but it will be updated
        #the subpulse time is the time per miniclick that should be felt underneath the polyrhythm, being played by countSynth

        self.timeSinceStart = 0 #keeps track of the elapsed time over which the polyrhythm has been playing since the first press of the play button
        self.timeAtLastNote = 0 #the time at which the most recent note was struck

        
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
        self.fastSynth = Synth.Synthesizer(520*(5/3), rate, (2* np.pi, np.sin), framesPerBuffer, self.dtype, self.maxAmplitude/3)
        self.countSynth = Synth.Synthesizer(420*(5/2), rate, (2* np.pi, np.sin), framesPerBuffer, self.dtype, self.maxAmplitude/15)
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
                self.countSynth.createHit()
                self.rhythmIndex += 1
                self.learnPolyrhythmScreen.eventControl["animateStepActive"] = True
                if self.rhythmIndex % num1 == 0:
                    self.slowSynth.createHit()
                if self.rhythmIndex % num2 == 0:
                    self.fastSynth.createHit()
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
                    self.learnPolyrhythmScreen = handler.getLearnPolyrhythmScreen(self.width, self.height, num2, num1)
                    self.promptUserScreen.currentAnimationState = "exitDown"
                    self.currentScreens.append(self.learnPolyrhythmScreen)
                    self.handleTempoChange() #this can also initialize tempo related variables

        if self.learnPolyrhythmScreen in self.currentScreens and self.learnPolyrhythmScreen.currentAnimationState in ["animateNormalPos", "animatePolyrhythm"]:
            if self.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.handlePlayPause()
            if self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "gold"
            else:
                self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "black"
                self.handleTempoChange()
                    
            
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
            if self.learnPolyrhythmScreen.currentAnimationState == "animatePolyrhythm":
                self.handleUserDrumming(event.key)
    
    def handleUserDrumming(self, input):
        pass

        


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

