from cmu_112_graphics import * #cmu 112 graphics taken from the course website
import AppUI as ui
import Synth
import pyaudio, numpy as np
import time


#---------------------------------------------------------------- App.y helper functions
#I knew this already but here is a good reference for understanding what's going on here http://newt.phys.unsw.edu.au/jw/notes.html#:~:text=In%20electronic%20music%2C%20pitch%20is,the%20pitch%20of%20A4)%3A
def getFrequencyFromMidiNote(letter, octave):
    standardA4Frequency = 440
    #69 is the standard midi number for A4 but I could have done this algorithm for any starting number for any starting octave for any standard frequency
    octave4Notes = {"A":69, "A#":70, "B":71, "C":72, "C#":73, "D":74, "D#":75, "E":76, "F":77, "F#":78, "G":79, "G#":80}
    midiNoteNumber = octave4Notes[letter] + 12*(int(octave) - 4)
    return standardA4Frequency*(2**(((midiNoteNumber - 69))/12))

#-------------------------------------------------------------------


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
        self.engageDecreaseTempo = False
        self.engageIncreaseTempo = False
        self.rhythmIndexSinceLastActivatedTempoChange = 0
        #--------------------------------------------

        #-------------------------- for streaks
        self.madeMistakeSinceThisCycle = False
        #---------------------------

        #------------------ for tap tempo
        self.tapTimes = []
        self.tapTempoTimer = 0
        #-------------------

        self.tempo = None #initialize to None here
        #store this as the actual tempo variable...this variable can be a float so that we can have more precision with our tempos
        #the disiplayed tempo is just the rounded int of this

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
        rate = 16000 #samples per second
        dType = pyaudio.paInt16 #for pyaudio
        self.dtype = np.int16 #for numpy
        self.maxAmplitude = 32767 #paInt16
        self.timePerBuffer = framesPerBuffer/rate 
        #-------------------------------------------

        #------------------------------------------ initialize synth
        wavetable = Synth.triangle()
        self.slowSynth = Synth.Synthesizer(520, rate, (wavetable[0], wavetable[1]), framesPerBuffer, self.dtype, self.maxAmplitude/12)
        self.fastSynth = Synth.Synthesizer(520*(3/2), rate, (wavetable[0], wavetable[1]), framesPerBuffer, self.dtype, self.maxAmplitude/12) #http://compoasso.free.fr/primelistweb/page/prime/liste_online_en.php
        self.countSynth = Synth.Synthesizer(520*(6/15), rate, (wavetable[0], wavetable[1]), framesPerBuffer, self.dtype, self.maxAmplitude/30)
        self.userSlowSynth = Synth.Synthesizer(520, rate, (wavetable[0], wavetable[1]), framesPerBuffer, self.dtype, self.maxAmplitude/12)
        self.userFastSynth = Synth.Synthesizer(520*(3/2), rate, (wavetable[0], wavetable[1]), framesPerBuffer, self.dtype, self.maxAmplitude/12)
        #------------------------------------------

        #https://people.csail.mit.edu/hubert/pyaudio/docs/ <---- learned to set up pyaudio streams primarily from this site

        self.pyAudio = pyaudio.PyAudio()
        #---------------------------------------- setup output stream
        self.outputStream = self.pyAudio.open(
                format = dType,
                channels = channels,
                rate = rate,
                output = True,                frames_per_buffer = framesPerBuffer,
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
        start = time.time()
        if self.tapTimes == []:
            self.tapTempoTimer = 0
        else:
            self.tapTempoTimer += self.timePerBuffer
        self.handleAnimationEvents()
        slowSynthData = self.slowSynth.getAudioData()
        fastSynthData = self.fastSynth.getAudioData()
        countSynthData = self.countSynth.getAudioData()
        userSlowSynthData = self.userSlowSynth.getAudioData()
        userFastSynthData = self.userFastSynth.getAudioData()
        data = countSynthData + userSlowSynthData + userFastSynthData
        if self.learnPolyrhythmScreen in self.currentScreens:
            greenDeactivated = ui.inverseRgbColorString(self.learnPolyrhythmScreen.eventControl["isMouseInsideGreenToggleBox"][1]) == (0, 50, 0)
            blueDeactivated =  ui.inverseRgbColorString(self.learnPolyrhythmScreen.eventControl["isMouseInsideBlueToggleBox"][1]) == (0, 0, 50)
            if not greenDeactivated: 
                data += fastSynthData
            if not blueDeactivated:
                data += slowSynthData
        self.timeSinceStart += self.timePerBuffer
        if (time.time() - start) > self.timePerBuffer*3/4:
            print(time.time() - start)
        assert(time.time() - start < self.timePerBuffer)
        return (data, pyaudio.paContinue)
        
    #there are a lot of things I need to do every sub pulse so organizing it this way just makes it cleaner
    def handleEventsPerSubPulse(self, num1, num2):
        self.timeAtLastNote = self.timeSinceStart
        if self.rhythmIndex != 0 and self.learnPolyrhythmScreen.currentAnimationState == "animatePolyrhythm": #if we do this from the start the dot will always be one move ahead
            self.learnPolyrhythmScreen.eventControl["currentDotSelector"] += 1
            if self.learnPolyrhythmScreen.eventControl["currentDotSelector"] == num1*num2:
                self.learnPolyrhythmScreen.eventControl["currentDotSelector"] = 0
        self.countSynth.createHit()
        if self.engageIncreaseTempo:
            self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] = str(int(self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1]) + 1)
            if self.rhythmIndex >= 10 + self.rhythmIndexSinceLastActivatedTempoChange: # only increase by 10 bpm at a time
                self.engageIncreaseTempo = False
                self.rhythmIndexSinceLastActivatedTempoChange = self.rhythmIndex
            self.handleTempoChange()
        elif self.engageDecreaseTempo:
            self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] = str(int(self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1]) - 1)
            if self.rhythmIndex >= 10 + self.rhythmIndexSinceLastActivatedTempoChange: #so that we only decrease by 10 bpm at a time
                self.engageDecreaseTempo = False
                self.rhythmIndexSinceLastActivatedTempoChange = self.rhythmIndex
            self.handleTempoChange()
        if self.rhythmIndex % num2 == 0:
            self.fastSynth.createHit()
        if self.rhythmIndex % num1 == 0:
            self.slowSynth.createHit()
        

        if self.rhythmIndex % (num1 * num2) == (num1*num2) - 1:  #end of a cycle
            accuracy = ui.getAverageBrightness(self.learnPolyrhythmScreen.eventControl["dotColorsForAccuracy"])/255
            self.learnPolyrhythmScreen.eventControl["playedPositions"] = []
            if accuracy < .93:
                self.madeMistakeSinceThisCycle = True
                self.learnPolyrhythmScreen.eventControl["streak"] = 0
            elif not self.madeMistakeSinceThisCycle:
                self.learnPolyrhythmScreen.eventControl["streak"] += 1
                if self.learnPolyrhythmScreen.eventControl["streak"] > self.learnPolyrhythmScreen.eventControl["bestStreak"]:
                    self.learnPolyrhythmScreen.eventControl["bestStreak"] = self.learnPolyrhythmScreen.eventControl["streak"]
            else:
                self.madeMistakeSinceThisCycle = False
                self.learnPolyrhythmScreen.eventControl["streak"] += 1
                if self.learnPolyrhythmScreen.eventControl["streak"] > self.learnPolyrhythmScreen.eventControl["bestStreak"]:
                    self.learnPolyrhythmScreen.eventControl["bestStreak"] = self.learnPolyrhythmScreen.eventControl["streak"]

        self.rhythmIndex += 1
        

    def inputAudioStreamCallback(self, inputAudio, frameCount, timeInfo, status):
        if self.learnPolyrhythmScreen in self.currentScreens:
            newAudioInData = np.frombuffer(inputAudio, dtype = self.dtype) #https://www.youtube.com/watch?v=at2NppqIZok&t=542s <--- here is a good start for getting a feel for processing input data with pyaudio
            lastMaxValue = self.learnPolyrhythmScreen.eventControl["getVolumeHeight"][1]
            volumeScale = np.max(newAudioInData)
            if volumeScale - lastMaxValue > self.hitTolerance:
                lastMaxValue = volumeScale
            else:
                lastMaxValue = self.faderSpeed*(lastMaxValue)
            self.learnPolyrhythmScreen.eventControl["getVolumeHeight"][1] = lastMaxValue
        return (inputAudio, pyaudio.paContinue)

    #all animation methods are inside the screen classes, but this method must get called by timer fired to 
    #take care of things that the audio callback funciton WAS taking care of, but we had to move it here because
    #the audio callback was taking too long
    def handleAnimationEvents(self):
        if self.learnPolyrhythmScreen in self.currentScreens and self.learnPolyrhythmScreen.currentAnimationState == 'animatePolyrhythm':
            num1, num2 = self.getPolyrhythm()
            grid = self.preferencesScreen.eventControl["settings"]
            if self.timeSinceStart >= self.timeAtLastNote + self.timePerSubPulse:
                self.handleEventsPerSubPulse(num1, num2)
            if grid.rows[3][int(grid.selected[3])] == "On" and self.rhythmIndex != 0:
                self.learnPolyrhythmScreen.eventControl["dotPositionFractionalPart"] = (self.timeSinceStart - self.timeAtLastNote)/self.timePerSubPulse
            else:
                self.learnPolyrhythmScreen.eventControl["dotPositionFractionalPart"] = 0
            if self.preferencesScreen.eventControl["settings"].selected[1] == 1.0:
                self.updateTempo()
            #the way we test for a switchover causes it to be True way too many times so this mechanism ensures we only get a single call
            if self.testForSwitchoverToNewNote():
                self.justDetectedAMiddlePoint = True
            elif self.justDetectedAMiddlePoint:
                if self.hasUserTappedNote == False: #they completely missed the note!
                    self.updateNoteColor(self.timePerSubPulse, self.getPastRhythmClick())
                self.hasUserTappedNote = False
                self.justDetectedAMiddlePoint = False
    def timerFired(self):
        for screen in self.currentScreens:
            screen.doAnimationStep()
        if self.currentScreens[-1].currentAnimationState == "animateNormalPos":
            self.currentScreens = [self.currentScreens[-1]]
        #update timers for the help boxes
        if self.learnPolyrhythmScreen in self.currentScreens:
            grid = self.preferencesScreen.eventControl["settings"]
            if grid.rows[-1][int(grid.selected[-1])] == "On":
                for box in self.learnPolyrhythmScreen.eventControl["helpBoxes"]:
                    if box[2]:
                        box[1] += self.timerDelay/24
                        
        
    
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
            
            for box in self.learnPolyrhythmScreen.eventControl["helpBoxes"]:
                if not box[0](event.x, event.y, self.learnPolyrhythmScreen): #if the mouse was not inside the box set the timer for that box to 0
                    box[2] = False
                    box[1] = 0
                else:
                    box[2] = True

            
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
            if self.learnPolyrhythmScreen.eventControl["isMouseInsideTapTempoBox"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.learnPolyrhythmScreen.eventControl["isMouseInsideTapTempoBox"][1] = "purple"
            else:
                self.learnPolyrhythmScreen.eventControl["isMouseInsideTapTempoBox"][1] = "yellow"
                self.tapTimes = []
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
                        self.updateSettings()
        if self.learnPolyrhythmScreen in self.currentScreens:

            for box in self.learnPolyrhythmScreen.eventControl["helpBoxes"]:
                box[1] = 0 #don't show help screen if they are pressing mouse
                
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
            if self.learnPolyrhythmScreen.eventControl["isMouseInsideTapTempoBox"][1] == "purple":
                self.learnPolyrhythmScreen.eventControl["isMouseInsideTapTempoBox"][1] = "red"
                self.tapTimes.append(self.tapTempoTimer)
                self.updateTempoForTapTempo()
            if self.learnPolyrhythmScreen.eventControl["isMouseInsideGreenToggleBox"][0](event.x, event.y, self.learnPolyrhythmScreen):
                if self.learnPolyrhythmScreen.eventControl["isMouseInsideGreenToggleBox"][1] == ui.rgbColorString(0, 180, 0):
                    self.learnPolyrhythmScreen.eventControl["isMouseInsideGreenToggleBox"][1] = ui.rgbColorString(0, 50, 0)
                else:
                    self.learnPolyrhythmScreen.eventControl["isMouseInsideGreenToggleBox"][1] = ui.rgbColorString(0, 180, 0)
            elif self.learnPolyrhythmScreen.eventControl["isMouseInsideBlueToggleBox"][0](event.x, event.y, self.learnPolyrhythmScreen):
                if self.learnPolyrhythmScreen.eventControl["isMouseInsideBlueToggleBox"][1] == ui.rgbColorString(0, 0, 180):
                    self.learnPolyrhythmScreen.eventControl["isMouseInsideBlueToggleBox"][1] = ui.rgbColorString(0, 0, 50)
                else:
                    self.learnPolyrhythmScreen.eventControl["isMouseInsideBlueToggleBox"][1] = ui.rgbColorString(0, 0, 180)
          
        if self.preferencesScreen in self.currentScreens and self.preferencesScreen.currentAnimationState == "animateNormalPos":
            grid = self.preferencesScreen.eventControl["settings"]
            result = grid.getSettingForMousePosition(event.x, event.y)
            if result != None:
                if grid.selected[result[0]] != None:
                    grid.selected[result[0]] = result[1] + 1
            if result != None and result[0] in grid.userInputRows:
                self.preferencesScreen.eventControl["justClickedInUserInput"] = [result[0], result[1]]
            else:
                self.preferencesScreen.eventControl["justClickedInUserInput"] = None
            if self.preferencesScreen.eventControl["applyButtonInfo"][0](event.x, event.y, self.preferencesScreen):
                self.preferencesScreen.currentAnimationState = "exitDown"
                self.currentScreens.append(self.learnPolyrhythmScreen)
                self.learnPolyrhythmScreen.currentAnimationState = "enterDown"
                self.resetPolyrhythmAttributes()
                self.updateSettings()
    
    def mouseReleased(self, event):
        if self.learnPolyrhythmScreen in self.currentScreens:
            if self.learnPolyrhythmScreen.eventControl["isMouseInsideTapTempoBox"][0](event.x, event.y, self.learnPolyrhythmScreen):
                self.learnPolyrhythmScreen.eventControl["isMouseInsideTapTempoBox"][1] = "purple"
            else:
                self.learnPolyrhythmScreen.eventControl["isMouseInsideTapTempoBox"][1] = "yellow"
                self.tapTimes = []

    #update the tempo based on an estimate of what the user wants the tempo to be based on the times of their taps in tapTimes
    def updateTempoForTapTempo(self):
        if len(self.tapTimes) < 2:
            return
        differenceSum = 0 #we are going to find the average time difference between all the taps
        for i in range(len(self.tapTimes) - 1):
            difference = self.tapTimes[i+1] - self.tapTimes[i]
            differenceSum += difference
        if differenceSum == 0: #prevent division by zero error
            return
        avgDif = differenceSum / (len(self.tapTimes) - 1) #this is the desired quarter note pulse, so seconds per beat
        beatsPerSecond = 1/(avgDif)
        newTempo = beatsPerSecond*60
        self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] = str(int(newTempo))
        self.tempo = newTempo
        self.handleTempoChange(True)



    
    def resetPolyrhythmAttributes(self):
        self.timeSinceStart = 0
        self.rhythmIndex = 0
        self.learnPolyrhythmScreen.eventControl["currentDotSelector"] = 0
        self.timeAtLastNote = 0
        self.slowSynth.turnNoteOff()
        self.fastSynth.turnNoteOff()
        self.countSynth.turnNoteOff()
        self.userFastSynth.turnNoteOff()
        self.userSlowSynth.turnNoteOff()
        self.hasUserTappedNote = False
        self.justDetectedAMiddlePoint = False 
        self.rhythmIndexSinceLastActivatedTempoChange = 0

    def keyPressed(self, event):
        if event.key.isalpha(): 
            event.key = event.key.lower() #don't want to deal with case
        if self.promptUserScreen in self.currentScreens and self.promptUserScreen.currentAnimationState == "animateNormalPos":
            if not event.key.isnumeric() and event.key != "delete":
                return
            if self.promptUserScreen.eventControl["mouseClickedInLeftBox"][1] == "gold":
                if event.key == "delete":
                    self.promptUserScreen.eventControl["typedInLeftBox"][1] = self.promptUserScreen.eventControl["typedInLeftBox"][1][:-1]
                    return
                if len(self.promptUserScreen.eventControl["typedInLeftBox"][1]) < 5:
                    self.promptUserScreen.eventControl["typedInLeftBox"][1] += event.key
            elif self.promptUserScreen.eventControl["mouseClickedInRightBox"][1] == "gold":
                if event.key == "delete":
                    self.promptUserScreen.eventControl["typedInRightBox"][1] = self.promptUserScreen.eventControl["typedInRightBox"][1][:-1]
                    return
                if len(self.promptUserScreen.eventControl["typedInRightBox"][1]) < 5:
                    self.promptUserScreen.eventControl["typedInRightBox"][1] += event.key
        elif self.learnPolyrhythmScreen in self.currentScreens and self.learnPolyrhythmScreen.currentAnimationState in ["animateNormalPos", "animatePolyrhythm"]:
            if not event.key.isnumeric() and event.key != "delete" and event.key != "space" and event.key not in  [self.preferencesScreen.eventControl["settings"].rows[0][1], self.preferencesScreen.eventControl["settings"].rows[0][2]]  and event.key != 'enter':
                return
            if self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] == "gold" and event.key != "space" and event.key != "enter":
                if event.key == "delete":
                    self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] = self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1][:-1]
                    return
                if len(self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1]) < 5:
                    self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] += event.key
            elif event.key == "space":
                if self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] != "gold" and self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] != "":
                    self.handlePlayPause()
            if self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1] != "" and event.key == "enter" and self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] == "gold":
                self.learnPolyrhythmScreen.eventControl["mouseInsideTempoBox"][1] = "black"
                self.handleTempoChange()
            if self.learnPolyrhythmScreen.currentAnimationState == "animatePolyrhythm" and event.key != "space":
                self.handleUserDrumming(event.key)
            else:
                self.doUserInputSynth(event.key)
        if self.preferencesScreen in self.currentScreens and self.preferencesScreen.currentAnimationState == "animateNormalPos":
            if event.key != "space" and not event.key.isnumeric():
                grid = self.preferencesScreen.eventControl["settings"]
                clickData = self.preferencesScreen.eventControl["justClickedInUserInput"]
                if clickData != None:
                    grid.rows[int(clickData[0])][int(clickData[1] + 1)] = event.key.lower()
    
    #simply test to see if it is time to reset the state of whether the user tried to press the note
    def testForSwitchoverToNewNote(self):
        num1, num2 = self.getPolyrhythm()
        timeToPastClick = self.timeSinceStart - self.timeAtLastNote #at this note, rhythmIndex was the current rhythmIndex - 1
        timeToNextClick = self.timeAtLastNote + self.timePerSubPulse - self.timeSinceStart #at this note, rhythmIndex will be the current rhythmIndex

        pastRhythmClick = self.getPastRhythmClick()
        nextRhythmClick = self.getNextRhythmClick()

        if pastRhythmClick == None or nextRhythmClick == None:
            return False
 
        timeToPastRhythmClick = timeToPastClick + self.timePerSubPulse*(self.rhythmIndex - 1 - pastRhythmClick)
        timeToNextRhythmClick = timeToNextClick + self.timePerSubPulse*(nextRhythmClick - self.rhythmIndex)

        return ui.almostEqual(timeToPastRhythmClick, timeToNextRhythmClick)


    #here is our algorithm for automating tempo changes
    #make the tempo faster if the user is doing pretty much perfect for an extended period of time
    #make the tempo slower if the user is struggling for an extended period of time
    #keep the tempo the same if the user is changing how well they are doing
    #how do we know how much the user is changing how well they are doing? Compute change in average brightness of a change in time
    #What is the change in time we use for this computation? Via testing, I found x to be the most effective value
    def updateTempo(self):
        num1, num2 = self.getPolyrhythm()
  
        accuracy = ui.getAverageBrightness(self.learnPolyrhythmScreen.eventControl["dotColorsForAccuracy"])/255

        stationaryTempo = not self.engageIncreaseTempo and not self.engageDecreaseTempo

        #we want to give 10 seconds in between tempo changes to correct
        numNotesAhead = int(10/self.timePerSubPulse)

        sufficientlyPastLastTempoDeactivation = self.rhythmIndex >= numNotesAhead + self.rhythmIndexSinceLastActivatedTempoChange
        if accuracy >= .8 and stationaryTempo and sufficientlyPastLastTempoDeactivation: #not doing that well
            self.engageIncreaseTempo = True
            self.rhythmIndexSinceLastActivatedTempoChange = self.rhythmIndex
        elif accuracy <= .6 and stationaryTempo and sufficientlyPastLastTempoDeactivation: #doing well
            self.engageDecreaseTempo = True
            self.rhythmIndexSinceLastActivatedTempoChange = self.rhythmIndex
        
    def doUserInputSynth(self, key):
        if key == self.preferencesScreen.eventControl["settings"].rows[0][1]:
            self.userSlowSynth.createHit()
        elif key == self.preferencesScreen.eventControl["settings"].rows[0][2]:
            self.userFastSynth.createHit()
    def handleUserDrumming(self, key):
        self.doUserInputSynth(key)
        if self.hasUserTappedNote: return
        self.learnPolyrhythmScreen.eventControl["selectorSqueezeSize"] = .75
        num1, num2 = self.getPolyrhythm()
        rhythmIndex = self.rhythmIndex - 1
        row = (rhythmIndex % (num1*num2)) // num1
        col = (rhythmIndex % (num1*num2)) % num1
        xMoveOver = (self.timeSinceStart - self.timeAtLastNote) / self.timePerSubPulse
        self.learnPolyrhythmScreen.eventControl["playedPositions"].append([row, col, xMoveOver, (255, 255, 255)])
        grid = self.preferencesScreen.eventControl["settings"]
        if grid.rows[3][int(grid.selected[3])] != "On":
            self.learnPolyrhythmScreen.eventControl["playedPositions"] = []

        timeToPastClick = self.timeSinceStart - self.timeAtLastNote #at this note, rhythmIndex was the current rhythmIndex - 1
        timeToNextClick = self.timeAtLastNote + self.timePerSubPulse - self.timeSinceStart #at this note, rhythmIndex will be the current rhythmIndex
        pastRhythmClick = self.getPastRhythmClick() #get the index of the last sub pulse which was played as part of the polyrhythm
        nextRhythmClick = self.getNextRhythmClick() #get the index of the next sub pulse which was played as part of the polyrhythm
        if pastRhythmClick == None or nextRhythmClick == None: 
            if not self.hasUserTappedNote:
                self.hasUserTappedNote = True
            return #deactivated all notes
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
        greenOff =  ui.inverseRgbColorString(self.learnPolyrhythmScreen.eventControl["isMouseInsideGreenToggleBox"][1]) == (0, 50, 0)
        blueOff = ui.inverseRgbColorString(self.learnPolyrhythmScreen.eventControl["isMouseInsideBlueToggleBox"][1]) == (0, 0, 50)
        start = self.rhythmIndex - 1
        if greenOff and not blueOff:
            while start % num1 != 0:
                start -= 1
        elif greenOff and not blueOff:
            while start % num2 != 0:
                start -= 1
        elif greenOff and blueOff:
            return None
        else:
            while start % num1 != 0 and start % num2 != 0:
                start -= 1
        return start
    
    #return the index of the next note which will be played
    def getNextRhythmClick(self):
        num1, num2 = self.getPolyrhythm()
        greenOff =  ui.inverseRgbColorString(self.learnPolyrhythmScreen.eventControl["isMouseInsideGreenToggleBox"][1]) == (0, 50, 0)
        blueOff = ui.inverseRgbColorString(self.learnPolyrhythmScreen.eventControl["isMouseInsideBlueToggleBox"][1]) == (0, 0, 50)
        start = self.rhythmIndex
        if greenOff and not blueOff:
            while start % num1 != 0:
                start += 1
        elif greenOff and not blueOff:
            while start % num2 != 0:
                start += 1
        elif greenOff and blueOff:
            return None
        else:
            while start % num1 != 0 and start % num2 != 0:
                start += 1
        return start
    

    def updateNoteColor(self, time, noteIndex):
        if noteIndex == None:
            return
        #time -= 10*self.timePerBuffer #account for latency
        num1, num2 = self.getPolyrhythm()
        assert(noteIndex % num1 == 0 or noteIndex % num2 == 0)
        time = abs(time)

        colorValue = None
        if time > self.timePerSubPulse/2: time = self.timePerSubPulse/2
        if self.timePerSubPulse >  0.08: #this value was found through testing 
            #in the worst case here the user must tap .125/4 seconds of the beat to hear feedback
            #we convert the time to a color value from 0 to 255, the maximum time is half the sub pulse time
            #multiply by .7 so it can never go completly black
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

    def convertOscillatorStringToOscillator(self, osc):
        assert(osc in ["saw", "square", "triangle", "sin"])
        return eval(f"Synth.{osc}()") #mwahaha

    #called whenever the user returns to self.learnPolyrhythmScreen from self.preferencesScreen to update any state that should be changed from the new settings
    def updateSettings(self):
        grid = self.preferencesScreen.eventControl["settings"]
        rowIndexOfFirstNoteSetting = 4
        slowNoteFrequency = getFrequencyFromMidiNote(grid.rows[rowIndexOfFirstNoteSetting][int(grid.selected[rowIndexOfFirstNoteSetting])], grid.rows[rowIndexOfFirstNoteSetting + 1][int(grid.selected[rowIndexOfFirstNoteSetting + 1])])
        fastNoteFrequency = getFrequencyFromMidiNote(grid.rows[rowIndexOfFirstNoteSetting + 3][int(grid.selected[rowIndexOfFirstNoteSetting + 3])], grid.rows[rowIndexOfFirstNoteSetting + 4][int(grid.selected[rowIndexOfFirstNoteSetting + 4])])
        countNoteFrequency = getFrequencyFromMidiNote(grid.rows[rowIndexOfFirstNoteSetting + 6][int(grid.selected[rowIndexOfFirstNoteSetting + 6])], grid.rows[rowIndexOfFirstNoteSetting + 7][int(grid.selected[rowIndexOfFirstNoteSetting + 7])])
        userSlowSynthFrequency = getFrequencyFromMidiNote(grid.rows[rowIndexOfFirstNoteSetting + 9][int(grid.selected[rowIndexOfFirstNoteSetting + 9])], grid.rows[rowIndexOfFirstNoteSetting + 10][int(grid.selected[rowIndexOfFirstNoteSetting + 10])])
        userFastSynthFrequency = getFrequencyFromMidiNote(grid.rows[rowIndexOfFirstNoteSetting + 12][int(grid.selected[rowIndexOfFirstNoteSetting + 12])], grid.rows[rowIndexOfFirstNoteSetting + 13][int(grid.selected[rowIndexOfFirstNoteSetting + 13])])
        self.slowSynth.changeFrequency(slowNoteFrequency)
        self.fastSynth.changeFrequency(fastNoteFrequency)
        self.countSynth.changeFrequency(countNoteFrequency)
        self.userFastSynth.changeFrequency(userFastSynthFrequency)
        self.userSlowSynth.changeFrequency(userSlowSynthFrequency)
        slowSynthWavetable = self.convertOscillatorStringToOscillator(grid.rows[rowIndexOfFirstNoteSetting + 2][int(grid.selected[rowIndexOfFirstNoteSetting + 2])])
        self.slowSynth.setWavetable(slowSynthWavetable[0], slowSynthWavetable[1])
        fastSynthWavetable = self.convertOscillatorStringToOscillator(grid.rows[rowIndexOfFirstNoteSetting + 5][int(grid.selected[rowIndexOfFirstNoteSetting + 5])])
        self.fastSynth.setWavetable(fastSynthWavetable[0], fastSynthWavetable[1])
        countSynthWavetable = self.convertOscillatorStringToOscillator(grid.rows[rowIndexOfFirstNoteSetting + 8][int(grid.selected[rowIndexOfFirstNoteSetting + 8])])
        self.countSynth.setWavetable(countSynthWavetable[0], countSynthWavetable[1])
        userSlowSynthWavetable = self.convertOscillatorStringToOscillator(grid.rows[rowIndexOfFirstNoteSetting + 11][int(grid.selected[rowIndexOfFirstNoteSetting + 11])])
        self.userSlowSynth.setWavetable(userSlowSynthWavetable[0], userSlowSynthWavetable[1])
        userFastSynthWavetable = self.convertOscillatorStringToOscillator(grid.rows[rowIndexOfFirstNoteSetting + 14][int(grid.selected[rowIndexOfFirstNoteSetting + 14])])
        self.userFastSynth.setWavetable(userFastSynthWavetable[0], userFastSynthWavetable[1])
        

        self.learnPolyrhythmScreen.eventControl["drawStreaks"] = (self.preferencesScreen.eventControl["settings"].selected[2] == 1.0)

    #called whenever the play or paused button (same button) is pressed
    #manage the events of turning off and on the sound and animation
    def handlePlayPause(self):
        if self.learnPolyrhythmScreen.currentAnimationState == "animateNormalPos":
            self.learnPolyrhythmScreen.currentAnimationState = "animatePolyrhythm"
        else:
            self.learnPolyrhythmScreen.currentAnimationState = "animateNormalPos"
            self.fastSynth.turnNoteOff()
            self.slowSynth.turnNoteOff()
            self.userFastSynth.turnNoteOff()
            self.userSlowSynth.turnNoteOff()



    #----------------------------------- these methods handle updates to variables when a tempo change happens
    #say whether the tempo change is coming from tap tempo or a change to the box
    def handleTempoChange(self, tapTempo = False):
        self.updateTimePerSubPulse(tapTempo)

    def updateTimePerSubPulse(self, tapTempo):
        if self.tempo == None or not tapTempo:
            self.tempo = int(self.learnPolyrhythmScreen.eventControl["typedInsideTempoBox"][1])
        if self.tempo != 0:
            num2, num1 = self.getPolyrhythm()
            #num1 is the slower note, and we want its pulse to match the quarter note, which is given by the tempo
            timePerQuarterNote = (1/self.tempo)*(60)
            timePerSlowNote = timePerQuarterNote
            #the rhythm consits of the slow note happening num1 times and the fast note happening num2 times
            #the total number of mini clicks in the whole duration is num1*num2
            #so we must have num1*num2*(miniClick time) = num1*(timePerSlowNote)
            #this is how we find the miniClick time
            self.timePerSubPulse = timePerSlowNote/num2

            assert(self.timePerSubPulse > self.timePerBuffer) #if this isn't true we will have all kinds of problems 
    #---------------------------------------------------------------------------


    #get the current polyrhythm, I probably should have made num1 and num2 avaiable to everyone in the app class so I don't have to call this function *everywhere* but it's okay
    def getPolyrhythm(self):
        num1 = int(self.promptUserScreen.eventControl["typedInRightBox"][1])
        num2 = int(self.promptUserScreen.eventControl["typedInLeftBox"][1])
        return num1, num2
            


    def redrawAll(self, canvas):
        for screen in self.currentScreens:
            screen.drawScreen(canvas)


appRunner = MainApp(width = 800, height = 800, mvcCheck = False)
