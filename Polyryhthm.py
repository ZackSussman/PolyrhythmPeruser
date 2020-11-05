import Synthesizer as synth

#take in a list of tuples, each tuple is the number of the note value
#of that note in the polyrhythm, the second is the frequency of that note
#an 'x' in data means x evenly spaced notes per time period specified in tempo 
def makePolyrhythm(data, tempo):
    result = []
    for note in data:
        timePerHit = tempo/note[0]
        ampFunc = synth.getADSRAmplitudeFunction(attack = .01, decay = .001, sustain = .004, release = .01, attackAmp = 1, sustainAmp = .5)
        sound = (synth.getOvertoneSeries(amplitudeFunction = ampFunc, baseFrequency = note[1], duration = timePerHit))*note[0]
        if result == []:
            result = sound
        else:
            result = synth.sumSignals([sound, result])
    return result


#get only one note of one component of the polyrhythm
#much faster than getting the whole polyrhythm
def getPolyrhythmPiece(data, tempo, piece):
    note = None
    for val in data:
        if val[0] == piece:
            note = val
            break
    timePerHit = tempo/note[0]
    ampFunc = synth.getADSRAmplitudeFunction(attack = .01, decay = .001, sustain = .004, release = .01, attackAmp = 1, sustainAmp = .5)
    sound = (synth.getOvertoneSeries(amplitudeFunction = ampFunc, baseFrequency = note[1], duration = timePerHit))
    return sound

