import numpy as np

#data is a numpy list, want to normalize it to a certain max value
def normalize(data, desiredMax):
    currentMax = np.max(data)
    return data * (desiredMax/currentMax)

#---------------wavetables!
def sin():
    period = 2*np.pi
    def func(x):
        return np.sin(x, dtype = np.float32)
    return (period, func)

def saw():
    period = 1
    def func(x):
        value = x - int(x)
        return (2*value - 1)
    return (period, func)

def square():
    period = 1
    def func(x):
        value = x - int(x)
        return -1 if value < .5 else 1
    return (period, func)

def triangle():
    period = 1
    def func(x):
        value = x - int(x)
        return 4*value - 1 if value < .5 else 1 - 4*(value - .5)
    return (period, func)
#-----------------------

#handle the actual generation of sound data
class Synthesizer():
    #waveTable is a function which will be used to get the audio values
    #waveTable is a tuple, first coordinate is the period of the wavetable, second is the actual function that is periodic
    def __init__(self, frequency, sampleRate, waveTable, bufferSize, dtype, maxAmplitude, phase = 0):
        self.sampleRate = sampleRate
        self.dtype = dtype
        self.waveTablePeriod, self.waveTable = waveTable[0], waveTable[1]
        self.bufferSize = bufferSize
        self.maxAmplitude = maxAmplitude
        self.bufferNum = 0
        self.fadingIn = False #used for more expressive longer note attacks
        self.noteOn = False
        self.amplitudeControlCoef = 1
        self.frequency = frequency
        self.phase = phase #if you are adding a bunch of similar waveforms you can change the phase of them to make them sum more nicely


    def changeFrequency(self, freq):
        self.frequency = freq
    
    def setWavetable(self, period, wavetable):
        phaseValue = self.waveTablePeriod/self.phase
        self.waveTablePeriod = period
        self.waveTable = wavetable
        self.phase = self.waveTablePeriod/phaseValue

    #use for a short percussive sound
    def createHit(self):
        self.fadingIn = True 
        self.noteOn = True
        self.amplitudeControlCoef = 1

    #used if the user pauses in the middle of a note
    def turnNoteOff(self):
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
        audioData = np.fromiter([self.maxAmplitude * self.waveTable(inputCoef*(self.bufferSize*self.bufferNum + x) + self.phase) for x in range(self.bufferSize)], dtype = self.dtype)
        self.bufferNum += 1
        if self.fadingIn:
            for i in range(len(audioData)):
                audioData[i] = self.dtype(audioData[i] * (1 - self.amplitudeControlCoef))
                self.amplitudeControlCoef *= .99
            if self.amplitudeControlCoef < 0.001:
                self.fadingIn = False
                self.amplitudeControlCoef = 1 - self.amplitudeControlCoef
        else:
            for i in range(len(audioData)):
                audioData[i] = self.dtype(audioData[i] * self.amplitudeControlCoef)
                self.amplitudeControlCoef *= .99
            if self.amplitudeControlCoef < 0.01:
                self.noteOn = False
        return audioData


    def getSinWav(self):
        secondsPerBuffer = self.bufferSize/self.sampleRate
        cyclesPerBuffer = self.frequency * secondsPerBuffer
        inputCoef = cyclesPerBuffer*self.waveTablePeriod/(self.bufferSize-1)
        audioData = np.fromiter([self.maxAmplitude * self.waveTable(inputCoef*(self.bufferSize*self.bufferNum + x) + self.phase) for x in range(self.bufferSize)], dtype = self.dtype)
        self.bufferNum += 1
        return audioData
