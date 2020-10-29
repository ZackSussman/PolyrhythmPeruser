import ZackAudio as z
import Synthesizer as s

kick = s.getKick(.1, 180)
player = z.AudioPlayer()
player.addClip("kick", kick)
player.playClip("kick")