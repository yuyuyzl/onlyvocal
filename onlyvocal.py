from pydub import AudioSegment
from multiprocessing import Pool
import math
def calculateMinK(item):
    songSlice = item[0]
    musicSlice = item[1]
    mindbfs = 1
    for k in range(0, 200):
        dbfs = songSlice.overlay(musicSlice.apply_gain(-k * 0.1)).dBFS
        if dbfs < mindbfs:
            mink = k
            mindbfs = dbfs
    return -mink * 0.1

def applyGain(item):
    songSlice = item[0]
    musicSlice = item[1]
    gain = item[2]
    return songSlice.overlay(musicSlice.apply_gain(gain))

if __name__ == '__main__':
    sliceLength=100
    song = AudioSegment.from_wav("lion518vocalEQ.wav")
    music = AudioSegment.from_wav("lion518instEQ.wav")
    totalSlices=math.ceil(len(song)/sliceLength)
    song=song[::sliceLength]
    music=music[::sliceLength]

    #mix = song.overlay(music.apply_gain(-8.4))


    mix=AudioSegment.empty()

    currentSlice=0
    mink=0
    kList=[]


    with Pool() as p:
        kList=p.map(calculateMinK,zip(song,music),totalSlices//64)


    fadeDuration=20
    song = AudioSegment.from_wav("lion518vocalEQ.wav")
    music = AudioSegment.from_wav("lion518instEQ.wav")
    song=song[::sliceLength]
    music=music[::sliceLength]
    targetGain=[]
    for currentSlice in range(len(kList)):
        iStart = currentSlice - 1
        if (iStart < 0):
            iStart = 0
        iEnd = currentSlice + 1
        arr = kList[iStart:iEnd]
        gain = sum(arr) / len(arr)
        targetGain.append(gain)


    with Pool() as p:
        mixSlices=p.map(applyGain,zip(song,music,targetGain),totalSlices//64)

    for s in mixSlices:
        mix+=s

    mix.export("export.wav", format="wav")