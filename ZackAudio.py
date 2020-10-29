import pyaudio
import struct

#audio player has a dictionary of clips that it can play
#clips has 3 elements, the double audio data, the byte form audio data, and the volume
#each clip is a 2d list, the first list has the audio data and the second has the volume
class AudioPlayer:
    def __init__(self, clips = {}, sampleRate = 48000):
        self.clips = clips 
        self.unAliasClips()
        for key in self.clips:
            self.updateVolumeOfClip(key)
        self.sampleRate = sampleRate
        for name in self.clips:
            self.smoothEdgesOfClip(name)
        self.addByteDataToClips()

    #in case the user aliased clips when creating the object
    def unAliasClips(self):
        for key in self.clips:
            self.clips[key][0] = self.clips[key][0] + []

    def updateVolumeOfClip(self, clipName):
        clip = self.clips[clipName]
        volume = clip[1]
        maxLevel = max(clip[0])
        for i in range(len(clip[0])):
            clip[0][i] *= volume/maxLevel

    def displayClips(self):
        print(self.clips)

    #'clip' in clipToEdge is completely unrelated from an audio 'clip' as in self.clips
    def clipToEdge(self, input, leftClip, rightClip):
        if input > rightClip:
            return rightClip
        if input < leftClip:
            return leftClip
        return input

    def updateClipByteData(self, name):
        self.clips[name][1] = self.convertFramesToBytes(self.clips[name][0])

    def addByteDataToClips(self):
        for name in self.clips:
            if len(self.clips[name]) == 2: #don't have byte data for this clip
                self.clips[name].insert(1, self.convertFramesToBytes(self.clips[name][0]))

    def convertFramesToBytes(self, audioValuesToConvert):
        bArray = b''
        for num in audioValuesToConvert:
            values = bytearray(struct.pack("f", num))
            bArray += values
        return bArray
    
    def playClip(self, clipName):
        clipAudioValues = self.clips[clipName][0]
        p = pyaudio.PyAudio()
        stream = p.open(format = pyaudio.paFloat32, channels = 1, 
        rate = self.sampleRate, output = True)
        stream.write(self.clips[clipName][1])
        stream.stop_stream()
        stream.close()
    
    def addClip(self, name, clip, volume = .8):
        self.clips[name] = [clip, volume]
        self.unAliasClips()
        self.updateVolumeOfClip(name)
        self.smoothEdgesOfClip(name)
        self.addByteDataToClips()
    
    def changeLevelOfClip(self, name, level):
        self.clips[name][1] = level
        self.updateVolumeOfClip(name)
        self.updateClipByteData(name)

    #stop pops at beginning and end of clip
    def smoothEdgesOfClip(self, name, fadeTime = .05):
        numSamples = int(fadeTime * self.sampleRate)
        for i in range(0, numSamples):
            self.clips[name][0][i] *= i/(numSamples - 1)
            self.clips[name][0][-1*i] *= i/(numSamples - 1)

