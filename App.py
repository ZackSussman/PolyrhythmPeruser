from cmu_112_graphics import *
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
        self.initializeAudio()

    def appStopped(self):
        self.outputStream.stop_stream()
        self.pyAudio.terminate()

    def initializeAudio(self):
        #------------------------------------------- consts
        framesPerBuffer = 2**10 #samples per buffer
        channels = 1
        rate = 48000 #samples per second
        dType = pyaudio.paInt16 #for pyaudio
        self.dtype = np.int16 #for numpy
        self.maxAmplitude = 32767 #paInt16
        #-------------------------------------------
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
        #------------------------------------------ initialize synth
        self.slowSynth = Synth.Synthesizer(520, rate, (2* np.pi, np.sin), framesPerBuffer, self.dtype, self.maxAmplitude/3)
        self.fastSynth = Synth.Synthesizer(520*(5/3), rate, (2* np.pi, np.sin), framesPerBuffer, self.dtype, self.maxAmplitude/3)
        self.countSynth = Synth.Synthesizer(420*(5/2), rate, (2* np.pi, np.sin), framesPerBuffer, self.dtype, self.maxAmplitude/15)
        #------------------------------------------


    def outputAudioStreamCallback(self, inputAudio, frameCount, timeInfo, status):
        slowSynthData = self.slowSynth.getAudioData()
        fastSynthData = self.fastSynth.getAudioData()
        countSynthData = self.countSynth.getAudioData()
        data = slowSynthData + fastSynthData + countSynthData
        return (data, pyaudio.paContinue)

    def inputAudioStreamCallback(self, inputAudio, frameCount, timeInfo, status):
        return (inputAudio, pyaudio.paContinue)

    def timerFired(self):
        if self.learnPolyrhythmScreen in self.currentScreens and self.learnPolyrhythmScreen.currentAnimationState == "animatePolyrhythm":
            if self.timeToDoAStep():
                self.learnPolyrhythmScreen.eventControl["animateStepActive"] = True
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
                    num1 = int(self.promptUserScreen.eventControl["typedInLeftBox"][1])
                    num2 = int(self.promptUserScreen.eventControl["typedInRightBox"][1])
                    self.promptUserScreen.currentAnimationState = "exitDown"
                    self.learnPolyrhythmScreen = handler.getLearnPolyrhythmScreen(self.width, self.height, num2, num1)
                    self.currentScreens.append(self.learnPolyrhythmScreen)
        if self.learnPolyrhythmScreen in self.currentScreens and self.learnPolyrhythmScreen.currentAnimationState in ["animateNormalPos", "animatePolyrhythm"]:
            if self.learnPolyrhythmScreen.eventControl["isMouseInsidePlayButton"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.handlePlayPause()
            if self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "gold"
            else:
                self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "black"
                    
            
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
            if not event.key.isnumeric() and event.key != "Delete" and event.key != "Space":
                return
            if self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] == "gold" and event.key != "Space":
                if event.key == "Delete":
                    self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] = self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1][:-1]
                    if self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] != "":
                        self.updateTempo()
                    return
                if len(self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1]) < 5:
                    self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] += event.key
                if self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] != "":
                    self.updateTempo()
            elif event.key == "Space":
                if self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] != "gold" and self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] != "":
                    self.handlePlayPause()

    def handlePlayPause(self):
        if self.learnPolyrhythmScreen.currentAnimationState == "animateNormalPos":
            self.learnPolyrhythmScreen.currentAnimationState = "animatePolyrhythm"
            self.updateTempo()
            self.polyrhythmStartTime = time.time()
            self.numClicksSinceStart = 0
        else:
            self.learnPolyrhythmScreen.currentAnimationState = "animateNormalPos"
            self.fastSynth.turnNoteOff()
            self.slowSynth.turnNoteOff()

    def updateTempo(self):
        tempo = int(self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1])
        if tempo != 0:
            timerFiresPerQuarterNote = int(self.promptUserScreen.eventControl["typedInLeftBox"][1])
            miliSecondsPerQuarterNote = (1/tempo)*(60)*(1000)
            self.timePerClick = miliSecondsPerQuarterNote/timerFiresPerQuarterNote

            
    #this gets called every time the animation steps. If we are at a time when a note should be played or turned off,
    #this function is what does that
    def updatePolyrhythmNotes(self):
 
        num1 = int(self.promptUserScreen.eventControl["typedInRightBox"][1])
        num2 = int(self.promptUserScreen.eventControl["typedInLeftBox"][1])
        currentNote = self.learnPolyrhythmScreen.eventControl["currentDotSelector"]
        #activate faster note
        if currentNote % num1 == (num1 - 1):
            self.fastSynth.createHit()

        #activate slowernote
        if currentNote % num2 == (num2 - 1):
            self.slowSynth.createHit()
        
        self.countSynth.createHit()



    #decide based on time data and tempo whether or not we need to step the polyrhythm animation
    def timeToDoAStep(self):
        elapsedTimeSinceStart = (time.time() - self.polyrhythmStartTime) * 1000 #miliseconds
        timeToBePast = self.numClicksSinceStart*self.timePerClick
        if elapsedTimeSinceStart > timeToBePast:
            self.numClicksSinceStart += 1
            self.updatePolyrhythmNotes()
            return True
        return False
            


    def redrawAll(self, canvas):
        for screen in self.currentScreens:
            screen.drawScreen(canvas)


appRunner = MainApp(width = 800, height = 800, mvcCheck = False)

