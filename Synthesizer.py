import math

def getSinWav(frequencyFunction, duration, amplitudeFunction = lambda i: 1, sampleRate = 48000):
    sin = []
    for i in range(int(duration * sampleRate)):
        sin.append(amplitudeFunction(i)*math.sin((frequencyFunction(i)*2*math.pi)*(i/sampleRate)))
    return sin


def getKick(time, startingPitch = 440, endingPitch = 70, sampleRate = 48000):
    frequencyFunction = lambda i: startingPitch + (endingPitch - startingPitch)*(i/(time*sampleRate))
    amplitudeFunction = lambda i: (1 + - (.7)*(((i)/(time*sampleRate))**12)
    return getSinWav(frequencyFunction,time, amplitudeFunction)