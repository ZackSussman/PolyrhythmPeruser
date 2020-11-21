import numpy as np

#data is a numpy list, want to normalize it to a certain max value
def normalize(data, desiredMax):
    currentMax = np.max(data)
    return data * (desiredMax/currentMax)


#handle the actual generation of sound data
class Synthesizer():
    #waveTable is a function which will be used to get the audio values
    #waveTable is a tuple, first coordinate is the period of the wavetable, second is the actual function that is periodic
    #noteOn and noteOff time are both in miliseconds
    def __init__(self, frequency, sampleRate, waveTable, bufferSize, dtype, maxAmplitude):
        self.sampleRate = sampleRate
        self.dtype = dtype
        self.waveTablePeriod, self.waveTable = waveTable
        self.bufferSize = bufferSize
        self.maxAmplitude = maxAmplitude
        self.bufferNum = 0
        self.fadingIn = False #used for more expressive longer note attacks
        self.fadingOut = False
        self.noteOn = False
        self.amplitudeControlCoef = 1
        self.frequency = frequency
        self.hitFadingIn = False #used for very fast sharp hits

    def turnNoteOn(self):
        self.fadingIn = True
        self.noteOn = True
        if self.fadingOut:
            self.amplitudeControlCoef = 1 - self.amplitudeControlCoef
            self.fadingOut = False

    #use for a short percussive sound
    def createHit(self):
        self.fadingIn = True #this will happen very quickly so we just set fadingOut to True here
        self.fadingOut = True
        self.noteOn = True
        #we are not fading in and out at the same time but this is the nicest way to do it

    def setFrequency(self, freq):
        self.frequency = freq
    
    def turnNoteOff(self):
        self.fadingOut = True
        if self.fadingIn:
            self.amplitudeControlCoef = 1 - self.amplitudeControlCoef
            self.fadingIn = False

    #get a buffer of audio data at the given frequency
    def getAudioData(self):
        if not self.noteOn:
            return np.fromiter([0] * self.bufferSize, dtype = self.dtype)
        
        secondsPerBuffer = self.bufferSize/self.sampleRate
        cyclesPerBuffer = self.frequency * secondsPerBuffer
        inputCoef = cyclesPerBuffer*self.waveTablePeriod/(self.bufferSize-1)
        audioData = np.fromiter([self.maxAmplitude * self.waveTable(inputCoef*(self.bufferSize*self.bufferNum + x)) for x in range(self.bufferSize)], dtype = self.dtype)
        self.bufferNum += 1

        if not self.fadingIn and not self.fadingOut:
            self.hitFadingIn = True
            self.fadingOut = True
            return audioData

        if self.fadingIn:
            for i in range(len(audioData)):
                audioData[i] = self.dtype(audioData[i] * (1 - self.amplitudeControlCoef))
                self.amplitudeControlCoef *= .9
            if self.amplitudeControlCoef < 0.001:
                self.fadingIn = False
                self.amplitudeControlCoef = 1 - self.amplitudeControlCoef
        else:
            for i in range(len(audioData)):
                audioData[i] = self.dtype(audioData[i] * self.amplitudeControlCoef)
                self.amplitudeControlCoef *= .999
            if self.amplitudeControlCoef < 0.0001:
                self.fadingOut = False
                self.noteOn = False
    
        return audioData


