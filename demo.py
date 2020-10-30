import ZackAudio as z
import Synthesizer as s

player = z.AudioPlayer()

kick = s.getKick(duration = .1, amplitude = 1, startingPitch = 220)
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

synthBase = s.getOvertoneSeries(baseFrequency = 360, duration = 3)
synthFifth = s.getOvertoneSeries(baseFrequency = 360*3/2, duration = 3)
synthThird = s.getOvertoneSeries(baseFrequency = 360*5/4, duration = 3)
synthSeventh = s.getOvertoneSeries(baseFrequency = 360*15/8, duration = 3)
player.addClip("synth!", s.fastSumSignals([synthBase, synthSeventh, synthThird, synthFifth]))
player.playClip("synth!")

