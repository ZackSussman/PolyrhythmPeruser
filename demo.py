import ZackAudio as z
import Synthesizer as s
import time

player = z.AudioPlayer()

def demo():
    kick = s.getKick(duration = .1, amplitude = 1, startingPitch = 220)
    duration = 4
    base = s.getSignal(frequencyFunction = lambda i: 440, oscillator = s.sin, duration = duration)
    third = s.getSignal(frequencyFunction = lambda i: 440*5/4, oscillator = s.saw, amplitudeFunction = lambda i: 0 if i < 1/6 * duration * 48000  else 1, duration = duration)
    fifth = s.getSignal(frequencyFunction = lambda i: 440*3/2, oscillator = s.triangle, amplitudeFunction = lambda i: 0 if i < 1/6 * 2 * duration * 48000 else 1, duration = duration)
    seventh = s.getSignal(frequencyFunction = lambda i: 440*15/8, oscillator = s.square, amplitudeFunction = lambda i: 0 if i < 1/6 * duration * 48000 *3 else 1, duration = duration)
    ninth = s.getOvertoneSeries(baseFrequency = 440*9/4, oscillator = s.sin, amplitudeFunction = lambda i: 0 if i < 1/6 * duration * 48000 *4 else 1, duration = duration)
    bg = s.getSignal(oscillator = s.whitenoise, amplitudeFunction = lambda i: .1, duration = duration)
    combination = s.sumSignals([base, third, fifth, seventh, bg, kick, ninth])
    player.addClip("chord hit", combination)
    player.playClip("chord hit")

demo()