
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