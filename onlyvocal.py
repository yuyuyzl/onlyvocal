from pydub import AudioSegment
from multiprocessing import Pool
from matplotlib import pyplot
import numpy
import math
import time
import os

muteGain=-120

def calculateMinK(item):
    songSlice = item[0]
    musicSlice = item[1]
    mindbfs = 9999
    minGain=muteGain
    for k in range(0, 100):
        dbfs = songSlice.overlay(musicSlice.apply_gain(-k * 0.1)).dBFS
        if dbfs < mindbfs:
            minGain = -k * 0.1
            mindbfs = dbfs
    return minGain


def applyGain(item):
    songSlice = item[0]
    musicSlice = item[1]
    gain = item[2]
    return songSlice.overlay(musicSlice.apply_gain(gain))


def appendSlices(item):
    mix = AudioSegment.empty()
    for s in item:
        mix += s
    return mix


def showProgress(asyncList, name="Task"):
    totalProgress = asyncList._number_left
    while not asyncList.ready():
        time.sleep(2)
        print(name, "%.1f%%" % (100 - asyncList._number_left * 100 / totalProgress))
    return asyncList.get()


if __name__ == '__main__':
    print("LiveRecord: ")
    songPath = input()
    if songPath=="":
        songPath="rv.wav"
    #songPath = "testvocal.wav"
    print("Instrumental: ")
    musicPath = input()
    if musicPath=="":
        musicPath="ri.wav"
    #musicPath = "testinst.wav"
    with Pool() as p:
        print("START")
        sliceLength = 20
        matchOffset = 40
        songOrig = AudioSegment.from_wav(songPath)
        musicOrig = AudioSegment.from_wav(musicPath)
        songlength=len(songOrig)
        totalSlices = math.ceil(len(songOrig) / sliceLength)
        song = songOrig[::sliceLength]
        music = musicOrig[::sliceLength]
        songMatch=[songOrig[i*sliceLength-matchOffset:(i+1)*sliceLength+matchOffset] for i in range(totalSlices)]
        musicMatch=[musicOrig[i*sliceLength-matchOffset:(i+1)*sliceLength+matchOffset] for i in range(totalSlices)]

        mix = AudioSegment.empty()

        currentSlice = 0
        mink = 0

        print("CALCULATE MIN K")

        kList = showProgress(p.map_async(calculateMinK, zip(songMatch, musicMatch), totalSlices // 99),"ANALYZE")

        song = AudioSegment.from_wav(songPath)
        music = AudioSegment.from_wav(musicPath)
        song = song[::sliceLength]
        music = music[::sliceLength]
        targetGain = []
        # for currentSlice in range(len(kList)):
        #     if(kList[currentSlice]==muteGain):
        #         if currentSlice==0:
        #             kList[currentSlice]=muteGain
        #         else:
        #             kList[currentSlice]=kList[currentSlice-1]

        for currentSlice in range(len(kList)):
            # iStart = currentSlice - 0
            # if iStart < 0:
            #     iStart = 0
            # iEnd = currentSlice + 1
            # arr = kList[iStart:iEnd]
            # gain = sum(arr) / len(arr)
            gain=kList[currentSlice]
            targetGain.append(gain)
        print("APPLY GAIN")
        mixSlices = showProgress(p.map_async(applyGain, zip(song, music, targetGain), totalSlices // 99),"GAIN")
        while len(mixSlices) > 1:
            print("MIX SLICES", len(mixSlices))
            mixSlices = p.map(appendSlices, [mixSlices[i:i + 2] for i in range(0, len(mixSlices), 2)], 8)

        mix = mixSlices[0]
        # if len(mix)<25 or len(s)<25:
        #     mix+=s
        # else:
        #     mix=mix.append(s,25)
    song = AudioSegment.from_wav(songPath)
    print("RES_DBFS:",mix.dBFS)
    print("RES_DBFS_MAX:",mix.max_dBFS)
    print("ORIG_DBFS:",song.dBFS)
    print("ORIG_DBFS_MAX:",song.max_dBFS)
    mix.export("export.wav", format="wav")
    os.startfile("export.wav")

    pyplot.plot([t * sliceLength for t in range(len(targetGain))],
                targetGain, "r-",
                [t * sliceLength for t in range(len(kList))],
                kList, 'g-', linewidth=1)
    pyplot.xticks(range(0,songlength-1000,1000),["%02d:%02d"%(t//60,t%60) for t in range(0,songlength//1000,1)])
    pyplot.show()
