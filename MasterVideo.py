def MasterVideo():
    #print(os.getcwd())
    #Get all the files into a list
    allFiles = os.listdir()
    #print(allFiles)
    goProFiles = [f for f in allFiles if any(char in f for char in {'G', 'X'})]
    #print(goProFiles)


    #extract the numbers from the Go Pro file name into 2 groups, the first 2 digits then the last group
    def extractNumber(filename):
        match = re.search((r'GX(\d{2})(\d+)'), filename)
        return (int(match.group(2)), int(match.group(1)))
        
    sortedGoProFiles = sorted(goProFiles, key=extractNumber)
    #Touple will go (end, beg)
    print(sortedGoProFiles)

    #Group the files that are only 1 number away since they are part of a single video
    grouped = []
    currentGroup = []
    prevEndNum = None
    prevBegNum = None

    for file in sortedGoProFiles:
        filenumber = extractNumber(file) #[0] will be 00NN, [1] will be GX0N
        #print(file)
        #print(filenumber)
        #print(f"prevBegNum as {prevBegNum}, prevEndNum as {prevEndNum} and filenumber as {filenumber}")
        #print(prevBegNum is None)
        #if prevBegNum is not None:
            #print(prevBegNum + 1 == filenumber[1] and prevEndNum == filenumber[0])
            #print(filenumber[1] == 1)
            #print(prevEndNum + 1 == filenumber[0])
        
        if prevBegNum is None:
            prevBegNum = filenumber[1]
            prevEndNum = filenumber[0]
            currentGroup.append(file)
        elif prevBegNum + 1 == filenumber[1] and prevEndNum == filenumber[0]:
            prevBegNum = filenumber[1]
            currentGroup.append(file)
        elif (filenumber[1] == 1 and prevEndNum + 1 == filenumber[0]):
            prevBegNum = filenumber[1]
            prevEndNum = filenumber[0]
            currentGroup.append(file)
        elif (filenumber[1] == 1 and prevEndNum < filenumber[0]):
            prevBegNum = filenumber[1]
            prevEndNum = filenumber[0]
            grouped.append(currentGroup)
            currentGroup = [file]
        
    #print(currentGroup)
    if currentGroup:
        grouped.append(currentGroup)

    print(grouped)

    #Writing files of the groups to splice together with ffmpeg later
    GoProTextFiles = []
    textFileName = ''
    if MasterVideo:
        textFileName = 'MasterVideo'
        with open(textFileName + '.txt', 'w') as f:
            for g in grouped:
                for name in g:
                    f.write('file ' + name + '\n')
    else:
        for i, g in enumerate(grouped, start=1):
            #print(i)
            #print(g)
            textFileName = 'VideoList_' + str(i)
            GoProTextFiles.append(textFileName)
            with open(textFileName + '.txt', 'w') as f:
                for name in g:
                    f.write('file ' + name + '\n')
                    print(textFileName + " created")
                
    #run ffmpeg command: ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
    if not MasterVideo:
        for i in GoProTextFiles:
            subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', i + '.txt', '-c', 'copy', i + '.mp4'])
    else:
        subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', textFileName + '.txt', '-c', 'copy', textFileName + '.mp4'])