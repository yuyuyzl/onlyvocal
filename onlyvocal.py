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

def appendSlices(item):
    mix=AudioSegment.empty()
    for s in item:
        mix+=s
    return mix


if __name__ == '__main__':
    songPath="いのちの名前rec.wav"
    musicPath="いのちの名前inst.wav"
    with Pool() as p:
        print("START")
        sliceLength=10
        song = AudioSegment.from_wav(songPath)
        music = AudioSegment.from_wav(musicPath)
        totalSlices=math.ceil(len(song)/sliceLength)
        song=song[::sliceLength]
        music=music[::sliceLength]

        mix=AudioSegment.empty()

        currentSlice=0
        mink=0

        print("CALCULATE MIN K")
        kList=p.map(calculateMinK,zip(song,music),totalSlices//64)

        song = AudioSegment.from_wav(songPath)
        music = AudioSegment.from_wav(musicPath)
        song=song[::sliceLength]
        music=music[::sliceLength]
        targetGain=[]
        for currentSlice in range(len(kList)):
            iStart = currentSlice - 1
            if iStart < 0:
                iStart = 0
            iEnd = currentSlice + 2
            arr = kList[iStart:iEnd]
            gain = sum(arr) / len(arr)
            targetGain.append(gain)

        print("APPLY GAIN")
        mixSlices=p.map(applyGain,zip(song,music,targetGain),totalSlices//64)
        while len(mixSlices)>1:
            print("MIX SLICES",len(mixSlices))
            mixSlices=p.map(appendSlices, [mixSlices[i:i+2] for i in range(0, len(mixSlices), 2)], 8)

        mix=mixSlices[0]
        # if len(mix)<25 or len(s)<25:
        #     mix+=s
        # else:
        #     mix=mix.append(s,25)

    mix.export("export.wav", format="wav")