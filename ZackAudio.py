import pyaudio
import struct
import wave
import _thread as thread

#audio player has a dictionary of clips that it can play
#clips has 2 elements, the double audio data, and the byte form audio data
class AudioPlayer:
    def __init__(self, clips = {}, sampleRate = 48000):
        self.clips = clips
        self.unAliasClips()
        self.sampleRate = sampleRate
        self.addByteDataToClips()

    #in case the user aliased clips when creating the object
    def unAliasClips(self):
        for key in self.clips:
            self.clips[key][0] = self.clips[key][0] + []

    def displayClips(self):
        print(self.clips)

    def addByteDataToClips(self):
        for name in self.clips:
            if len(self.clips[name]) == 1: #don't have byte data for this clip
                self.clips[name].append(self.convertFramesToBytes(self.clips[name][0]))

    def convertFramesToBytes(self, audioValuesToConvert):
        bArray = b''
        for num in audioValuesToConvert:
            values = bytearray(struct.pack("f", num))
            bArray += values
        return bArray
    

    def asynchPlayClip(self, clipName, meaningLessPlaceholder):
        clipValues = self.clips[clipName][1]
        p = pyaudio.PyAudio()
        stream = p.open(format = pyaudio.paFloat32, channels = 1, 
        rate = self.sampleRate, output = True)
        stream.write(clipValues)
        stream.stop_stream()
        stream.close()

    def playClip(self, clipName, asynchronous = True):
        clipAudioData = self.clips[clipName][1]
        if not asynchronous:
            p = pyaudio.PyAudio()
            stream = p.open(format = pyaudio.paFloat32, channels = 1, 
            rate = self.sampleRate, output = True)
            stream.write(clipAudioData)
            stream.stop_stream()
            stream.close()
        else:
            thread.start_new_thread(self.asynchPlayClip, (clipName, 0))
        
    
    def addClip(self, name, clip):
        self.clips[name] = [clip]
        self.unAliasClips()
        self.addByteDataToClips()
    