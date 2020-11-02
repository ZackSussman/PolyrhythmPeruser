import math
import random
 
#oscillators ----------------------------
period = 2*math.pi
sin = lambda x: math.sin(x)
square = lambda x: 1 if x % (period) < period/2 else -1
saw = lambda x: 1 - (x % (period)) / (period)
triangle = lambda x: -1 + 4*((x % (period)) / (period)) if (x % period) < period/2 else 1 - 4*((x % (period) - period/2) / (period))
whitenoise = lambda x: random.randint(0, 1024)/1024 if random.randint(0, 1) == 0 else -1*random.randint(0, 1024)/1024
#------------------------------------------

def getSignal(duration = 1, frequencyFunction = lambda i: 440, amplitudeFunction = lambda i: 1, sampleRate = 48000, oscillator = sin, *kwargs):
    if "duration" in kwargs:
        duration = kwargs["duration"]
    if "frequencyFunction" in kwargs:
        frequencyFunction = kwargs["frequencyFunction"]
    if "amplitudeFunction" in kwargs:
        amplitudeFunction = kwargs["amplitudeFunction"]
    if "sampleRate" in kwargs:
        sampleRate = kwargs["sampleRate"]
    if "oscillator" in kwargs:
        oscillator = kwargs["oscillator"]
    signal = []
    for i in range(int(duration*sampleRate)):
        signal.append(amplitudeFunction(i)*oscillator((frequencyFunction(i)*2*math.pi)*(i/sampleRate)))
    return clipToEdges(smoothEdges(signal))

#retuan a lambda which is an adsr amplitudeFunction
#this is a very handy method for constructing amplitudeFunctions for your signals
def getADSRAmplitudeFunction(a = .1, d = .1, s = .75, r = .05, dur = 1, attackAmp = 1, sustainAmp = .8, sampleRate = 48000, **kwargs):
    if "attack" in kwargs:
        a = kwargs["attack"]
    if "decay" in kwargs:
        d = kwargs["decay"]
    if "sustain" in kwargs:
        s = kwargs["sustain"]
    if "release" in kwargs:
        r = kwargs["release"]
    if "duration" in kwargs:
        dur = kwargs["duration"]
    if "attackAmp" in kwargs:
        attackAmp = kwargs["attackAmp"]
    if "sustainAmp" in kwargs:
        sustainAmp = kwargs["sustainAmp"]
    if "sampleRate" in kwargs:
        sampleRate = kwargs["sampleRate"]
    assert(a + d + s + r == 1) #these are proportions
    aS = a*sampleRate
    dS = d*sampleRate + aS
    sS = s*sampleRate + dS + aS
    rS = r*sampleRate + sS + dS + aS
    durS = dur*sampleRate
    func = lambda i: (int(i < aS)*(attackAmp * i/(aS-1)) + int(aS <= i < dS)*(attackAmp + (sustainAmp - attackAmp)*((i - aS)/(dS - 1 - aS))) + int(dS <= i < sS)*(sustainAmp) + int(i >= sS)*(sustainAmp * (durS - i)/(durS - sS)))
    return func


def getKick(duration = .1, amplitude = 1, startingPitch = 440, endingPitch = 70, sampleRate = 48000, oscillator = triangle, **kwargs):
    if "duration" in kwargs:
        duration = kwargs["duration"]
    if "startingPitch" in kwargs:
        startingPitch = kwargs["startingPitch"]
    if "amplitude" in kwargs:
        amplitude = kwargs["amplitude"]
    if "endingPitch" in kwargs:
        endingPitch = kwargs["endingPitch"]
    if "sampleRate" in kwargs:
        sampleRate = kwargs["sampleRate"]
    frequencyFunction = lambda i: startingPitch + (endingPitch - startingPitch)*(i/(duration*sampleRate))
    amplitudeFunction = lambda i: amplitude * (1 + - (.7)*(((i)/(duration*sampleRate))**12))
    return getSignal(duration = duration, frequencyFunction = frequencyFunction,  amplitudeFunction = amplitudeFunction, oscillator = oscillator)

def normalize(output):
    maxValue = max(output)
    if maxValue == 0: return output #prevent division by zero error
    for x in range(len(output)):
        output[x] /= maxValue
    return output

#recursively sum a list of signals that may all be of different lengths
#the algorithm works by summing two signals at a time, then replacing one of the signals in the list with that sum
def sumSignals(signals):
    assert(len(signals) > 0) #can't sum an enpty list!
    if len(signals) == 1: #finished the recursion!
        return signals[0]
    partialSum = []
    shortSig, longSig = signals[0], signals.pop()
    clipToEdges(smoothEdges(shortSig))
    clipToEdges(smoothEdges(longSig))
    if len(longSig) < len(shortSig): shortSig, longSig = longSig, shortSig
    for i in range(len(shortSig)):
        partialSum.append(shortSig[i] + longSig[i])
    for i in range(len(shortSig), len(longSig)):
        partialSum.append(longSig[i])
    signals[0] = partialSum
    return normalize(sumSignals(signals))

#geta signal which puts together the signals contained in data
#data is a list of tuples, (signal, lengthOfPauseBeforeNextSignal)
def assortSignals(data, sampleRate = 48000):
    output = []
    for info in data:
        output += info[0]
        for i in range(int(info[1]*sampleRate)):
            output += [0]
    return output


#assumes all signals are the same length
def fastSumSignals(signals):
    for x in range(len(signals)):
        assert(len(signals[0]) == len(signals[x]))
    output = []
    for x in range(len(signals[0])):
        value = 0
        for signal in signals:
            value += signal[x]
        output.append(value)
    return normalize(output)

#prevent pops------------------------------------------------
def smoothEdges(signal, fadeTime = .005, sampleRate = 48000):
    numSamples = int(fadeTime * sampleRate)
    for i in range(0, numSamples):
        signal[i] *= i/(numSamples - 1)
        signal[-1*i] *= i/(numSamples - 1)
    return signal

def clipToEdges(signal):
    for i in range(len(signal)):
        if signal[i] > 1:
            signal[i] = 1
        elif signal[i] < -1:
            signal[i] = -1
    return signal
#-----------------------------------------------------



#given a list of relative amplitudes, get the harmonic series of frequencies starting on the baseFrequency
def getOvertoneSeries(duration = 1, baseFrequency = 440, amplitudeFunction = lambda i: 1, relativeAmplitudes = [1/(x**2) for x in range(1, 51)], oscillator = sin, **kwargs):
    if "duration" in kwargs:
        duration = kwargs["duration"]
    if "baseFrequency" in kwargs:
        baseFrequency = kwargs["baseFrequency"]
    if "relativeAmplitudes" in kwargs:
        relativeAmplitudes = kwargs["relativeAmplitudes"]
    if "oscillator" in kwargs:
        oscillator = kwargs["oscillator"]
    if "amplitudeFunction" in kwargs:
        amplitudeFunction = kwargs["amplitudeFunction"]
    sinWavList = []
    frequency = baseFrequency
    for x in range(len(relativeAmplitudes)):
        thisAmplitudeFunction = lambda i: amplitudeFunction(i)*relativeAmplitudes[x]
        sinWavList.append(getSignal(duration = duration, frequencyFunction = lambda i: baseFrequency*(x), oscillator = oscillator, amplitudeFunction = thisAmplitudeFunction))
    return fastSumSignals(sinWavList)
