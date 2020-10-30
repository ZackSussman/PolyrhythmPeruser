import ZackAudio as z
import Synthesizer as s

kick = s.getKick(duration = .1, amplitude = 1, startingPitch = 200)
player = z.AudioPlayer()
player.addClip("kick", kick)
player.playClip("kick")

sinWav = s.getSignal(duration = 2, amplitudeFunction = lambda i: .2)
player.addClip("sin", sinWav)
player.playClip("sin")
majorThird = s.getSignal(duration = 2, amplitudeFunction = lambda i: .2, frequencyFunction = lambda i: 440*5/4)
majorSeventh = s.getSignal(duration = 2, amplitudeFunction = lambda i: .2, frequencyFunction = lambda i: 440*15/8)

sinsAndKick = s.sumSignals([sinWav, kick, majorThird, majorSeventh])
player.addClip("chord", sinsAndKick)
player.playClip("chord")