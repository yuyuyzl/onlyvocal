from pydub import AudioSegment
import math

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
for item in zip(song,music):
    currentSlice+=1
    songSlice=item[0]
    musicSlice=item[1]
    mindbfs=1
    for k in range(70,200):
        dbfs=songSlice.overlay(musicSlice.apply_gain(-k*0.1)).dBFS
        if dbfs<mindbfs:
            mink=k
            mindbfs=dbfs
    print((currentSlice/totalSlices),-mink*0.1)
    kList.append(-mink*0.1)
    #mix+=songSlice.overlay(musicSlice.apply_gain(-mink*0.1))

currentSlice=0
fadeDuration=20
song = AudioSegment.from_wav("lion518vocalEQ.wav")
music = AudioSegment.from_wav("lion518instEQ.wav")
song=song[::sliceLength]
music=music[::sliceLength]
for item in zip(song,music):
    songSlice=item[0]
    musicSlice=item[1]
    iStart=currentSlice-1
    if(iStart<0):
        iStart=0
    iEnd=currentSlice+1
    arr=kList[iStart:iEnd]
    gain=sum(arr)/len(arr)
    mixSlice=songSlice.overlay(musicSlice.apply_gain(gain))
    mix+=mixSlice
    print((currentSlice/totalSlices))
    currentSlice+=1
mix.export("export.wav", format="wav")