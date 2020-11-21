import numpy as np


#handle the actual generation of sound data
class Synthesizer():
    #waveTable is a function which will be used to get the audio values
    #waveTable is a tuple, first coordinate is the period of the wavetable, second is the actual function that is periodic
    #noteOn and noteOff time are both in miliseconds
    def __init__(self, sampleRate, waveTable, bufferSize, dtype, maxAmplitude):
        self.sampleRate = sampleRate
        self.dtype = dtype
        self.waveTablePeriod, self.waveTable = waveTable
        self.bufferSize = bufferSize
        self.maxAmplitude = maxAmplitude
        self.bufferNum = 0
        self.fadingIn = False
        self.fadingOut = False
        self.noteOn = False
        self.amplitudeControlCoef = 1

    def turnNoteOn(self):
        self.fadingIn = True
        self.noteOn = True
        if self.fadingOut:
            self.amplitudeControlCoef = 1 - self.amplitudeControlCoef
            self.fadingOut = False

    
    def turnNoteOff(self):
        self.fadingOut = True
        if self.fadingIn:
            self.amplitudeControlCoef = 1 - self.amplitudeControlCoef
            self.fadingIn = False

    #get a buffer of audio data at the given frequency
    def getAudioData(self, frequency):
        if not self.noteOn:
            return np.fromiter([0] * self.bufferSize, dtype = self.dtype)
        
        secondsPerBuffer = self.bufferSize/self.sampleRate
        cyclesPerBuffer = frequency * secondsPerBuffer
        inputCoef = cyclesPerBuffer*self.waveTablePeriod/(self.bufferSize-1)
        audioData = np.fromiter([self.maxAmplitude * self.waveTable(inputCoef*(self.bufferSize*self.bufferNum + x)) for x in range(self.bufferSize)], dtype = self.dtype)
        self.bufferNum += 1

        if not self.fadingIn and not self.fadingOut:
            return audioData

        if self.fadingIn:
            for i in range(len(audioData)):
                audioData[i] = self.dtype(audioData[i] * (1 - self.amplitudeControlCoef))
                self.amplitudeControlCoef *= .9999

            if self.amplitudeControlCoef < 0.001:
                self.fadingIn = False
                self.amplitudeControlCoef = 1 - self.amplitudeControlCoef
        else:
            for i in range(len(audioData)):
                audioData[i] = self.dtype(audioData[i] * self.amplitudeControlCoef)
                self.amplitudeControlCoef *= .9999
            if self.amplitudeControlCoef < 0.001:
                self.fadingOut = False
                self.noteOn = False
    
        return audioData


