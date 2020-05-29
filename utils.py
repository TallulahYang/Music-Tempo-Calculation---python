import cv2
import numpy as np
import os
import math
import sys

def aHash(img):
    try:
        img=cv2.resize(img,(8,8),interpolation=cv2.INTER_CUBIC)
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        s=0
        hash_str=''
        for i in range(8):
            for j in range(8):
                s=s+gray[i,j]
        avg=s/64
        for i in range(8):
            for j in range(8):
                if  gray[i,j]>avg:
                    hash_str=hash_str+'1'
                else:
                    hash_str=hash_str+'0'            
        return hash_str
    except cv2.error as e:
        print('Invalid frame!')
    
    return '0'

def pHash(img):
    try:
        img=cv2.resize(img,(32,32),interpolation=cv2.INTER_CUBIC)
        img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img = img.astype(np.float32)

        img = cv2.dct(img)
        img = img[0:8,0:8]
        avg = 0
        hash_str = ''
    
        for i in range(8):
            for j in range(8):
                avg += img[i,j]
        avg = avg/64
    
        for i in range(8):
            for j in range(8):
                if  img[i,j]>avg:
                    hash_str=hash_str+'1'
                else:
                    hash_str=hash_str+'0'            
        return hash_str
    
    except cv2.error as e:
        print('Invalid frame!')
    
    return '0'
 
def cmpHash(hash1,hash2):
    n=0
    if len(hash1)!=len(hash2):
        return -1
    for i in range(len(hash1)):
        if hash1[i]!=hash2[i]:
            n=n+1
    return n

def getKeyFrame(similarhash, similiaritystart, similiarityend=None):
    keyframes=[]
    for i in range(len(similarhash)):
        if similiarityend:
            if similarhash[i]['sm'] > similiaritystart and similarhash[i]['sm'] <= similiarityend:
                keyframes.append(similarhash[i])
        else:
            if similarhash[i]['sm'] > similiaritystart:
                keyframes.append(similarhash[i])
    
    return keyframes

def compareHash(neighbor):
    sorted_x = sorted(neighbor, key = lambda i: i['sm'],reverse=True) 
    return sorted_x[0]

def adjustKeyFrame(keyframes,dValue):
    # if(len(keyframes)<1) return []
    p_begin = 0
    p_next = 1
    adjustKeyframes =[]
    
    neighbor = []
    begin = keyframes[p_begin]
    neighbor.append(begin)
    
    while(p_begin<len(keyframes)):
        if p_next==len(keyframes):
            adjustKeyframes.append(keyframes[p_begin])
            break
        else:
            next = keyframes[p_next]
            if next['frame'] - begin['frame'] < dValue:
                neighbor.append(next)
                p_next +=1
            else:
#                 print(neighbor)
                compareNext = compareHash(neighbor)
#                 compareNext=neighbor[0]
                adjustKeyframes.append(compareNext)
                p_begin = p_next
                p_next +=1
                neighbor = []
                begin = keyframes[p_begin]
                neighbor.append(begin)        
    return adjustKeyframes

def walkFile(file):
    arr =[]
    for root, dirs, files in os.walk(file):
        for f in files:
            arr.append(os.path.join(root, f))
    return arr


def findCloseNum(arr, num):
    index = 0
    d_value = sys.maxsize
    for i in range(0, len(arr)):
        new_d_value = math.fabs(arr[i] - num)
        if new_d_value <= d_value:
            if new_d_value == d_value and arr[i] < arr[index]:
                continue
            index = i
            d_value = new_d_value

    closeNum = arr[index]
    return closeNum,index

def findCloseThreeNum(arr,bmps):
    rst = []
    rstCopy = []
    for i in bmps:
        for j in range(len(arr)):
            diff = math.fabs(arr[j] - i)
            rst.append({'diff':diff, 'idx':j })
    
    rst.sort(key=lambda x: x['diff'])
    
    rstCopy.append(rst[0]['idx'])
    for id in rst:
        if id['idx'] not in rstCopy:
            rstCopy.append(id['idx'])
    # print(rstCopy)
    return rstCopy[:3]

def frames_to_timecode(frames,framerate):
    return '{0:02d}:{1:02d}:{2:02d}:{3:02d}'.format(int(frames / (3600*framerate)),
                                                    int(frames / (60*framerate) % 60),
                                                    int(frames / framerate % 60),
                                                    int(frames % framerate))
def timecode_to_frames(timecode,framerate):
    return sum(f * int(t) for f,t in zip((3600*framerate, 60*framerate, framerate, 1), timecode.split(':')))



# print timecode_to_frames('15:41:08:02',24) - timecode_to_frames('15:41:07:00')
# print frames_to_timecode(26,24)

def getCloseBPM(frames,fps,minTempo=60,maxTempo=180):
    def frame_to_timeCode2(frames,framerate):
        return {'Hrs':int(frames / (3600*framerate)),'Min':int(frames / (60*framerate) % 60),'Sec':int(frames / framerate % 60),'Dsc':convertSmpteToDsc(int(frames % framerate)) }
    
    def findTempoSteps(minTempo,maxTempo,tempoStep) :
        thisStep = (tempoStep) if tempoStep else 1
        numberOfTempoSteps = math.fabs(maxTempo - minTempo) / thisStep
        nSteps = math.floor(numberOfTempoSteps)
        return nSteps

    def sortError(a, b):
        if (b.Error < a.Error) :
            return 1
        if (a.Error < b.Error) :
            return -1
        return 0

    def findClosestBeat(eventTime, bpmTempo) :
        eventSec = convertToSeconds(eventTime) - convertToSeconds(eventCue[0])
        if (bpmTempo) :
            beatInterval = 60 / bpmTempo
            beatNumber = round(eventSec / beatInterval)
            timeMismatch = math.fabs(beatNumber * beatInterval - eventSec)
        else:
            beatNumber = 1
            timeMismatch = 0

        beatError ={'Beat':beatNumber + 1 , 'Error':timeMismatch} 
        return beatError

    def rmsError(bpmTempo) :
        totError = 0
        nEvents = 0

        for iEv in range(nEventMax):
            eventSec = convertToSeconds(eventCue[iEv])
            if (eventSec > secThreshold):
                thisBeatError = findClosestBeat(eventCue[iEv], bpmTempo)
                theError = thisBeatError['Error']
                theSquaredError = theError * theError
                totError += theSquaredError
                nEvents +=1

        if (nEvents) :
            avError = totError / nEvents
        else:
            avError = 0

        totError = math.sqrt(avError)
        return totError

    def convertSmpteToDsc(theDsc) :
        dscValue = theDsc
        dscValue = round(100 * theDsc * 1/fps)
        return dscValue

    def convertToSeconds(theCue) :
        dscValue = convertSmpteToDsc(theCue['Dsc'])
        numberOfSec = theCue['Hrs'] * 3600 + theCue['Min'] * 60 + theCue['Sec'] + 0.01 * theCue['Dsc']
        return numberOfSec


    # minTempo  = 60
    # maxTempo = 160
    tempoStep = 1
    nTempoMax = findTempoSteps(minTempo,maxTempo,tempoStep)
    secThreshold = 0.050
    # fps = 30

    eventCue = []
    # frames = [0, 84, 152, 215]
    # print(frame_to_timeCode2(96,30))
    # print(frames_to_timecode(96,30))
    for i in range(len(frames)):
        print(frame_to_timeCode2(int(frames[i]),int(fps)))
        eventCue.append(frame_to_timeCode2(int(frames[i]),fps))

    nEventMax = len(frames)
        
    teAnEr = []
    if (nTempoMax < 4) :
        alert("--- FILM MUSIC TEMPO CALCULATION TOOL ---\n"+
          "WARNING: TEMPO SEARCH DOMAIN.\n"+
          "You have selected a small set of tempos (4 or less).\n"+
          "You may want to change the tempo search domain settings.\n")
    
    for i in range(nTempoMax) :
        thisTempo = minTempo + i * tempoStep
        thisRmsError = rmsError(thisTempo)
        teAnEr.append({'Tempo':thisTempo, 'Error':thisRmsError}) 

    teAnEr.sort(key=lambda x: x['Error'])
    # print(teAnEr)
    # for i in range(3):
    #     print(teAnEr[i])
    return teAnEr[0]['Tempo'],teAnEr[1]['Tempo'],teAnEr[2]['Tempo']

frames = [0, 84, 152, 215]
fps = 30
getCloseBPM(frames,30)