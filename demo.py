import ZackAudio as z
import math

sin = []
for i in range(48000*3):
    sin.append(math.sin(440*2*math.pi*(i/(48000))))
player = z.AudioPlayer()
player.addClip("loudSin", [sin, 1])
player.addClip("quietSin", [sin, .02])
player.playClip("quietSin")
print("played quiet sin")
player.playClip("loudSin")
print("played loud sin")
player.changeLevelOfClip("quietSin", .3)
player.playClip("quietSin")
print("played louder quietSin")