import ZackAudio as z
import Synthesizer as s
import time

player = z.AudioPlayer()

kick = s.getKick(duration = .1, amplitude = 1, startingPitch = 220)
player.addClip("kick", kick)
player.playClip("kick", False)

sinWav = s.getSignal(duration = 2, amplitudeFunction = lambda i: .2)
print(sinWav[:300])
player.addClip("sin", sinWav)
player.playClip("sin", False)
majorThird = s.getSignal(duration = 2, amplitudeFunction = lambda i: .2, frequencyFunction = lambda i: 440*5/4)
majorSeventh = s.getSignal(duration = 2, amplitudeFunction = lambda i: .2, frequencyFunction = lambda i: 440*15/8)

sinsAndKick = s.sumSignals([sinWav, kick, majorThird, majorSeventh])
player.addClip("chord", sinsAndKick)
player.playClip("chord", False)

overtonedWav = s.getOvertoneSeries(baseFrequency = 440, duration = 3)
player.addClip("overtones", overtonedWav)
print("start play")
player.playClip("overtones") #asynchronosuly
print("playing :)")
begin = time.time() 
while time.time() - begin < 3:
    pass
print("finish play")