#this script is meant to concat the go pro splits made from porting the videos onto a machine
#I'm assumming you already know the folder you're working in

import os, re, subprocess

isInDirectory = input("Are we already in the directory you want? ").lower() in ('yes', 'y')
if not isInDirectory:
    drive = input("What drive will we be working in? ")
    os.chdir("/mnt/" + drive.lower())
    directory = input("Input directory of Go Pro Spilts: ")
    #os.chdir
#print(os.getcwd())
#Get all the files into a list
allFiles = os.listdir()
#print(allFiles)
goProFiles = [f for f in allFiles if any(char in f for char in {'G', 'X'})]
#print(goProFiles)

#extract the number from the Go Pro file name and sort them
def extractNumber(filename):
    match = re.search((r'GX(\d+)'), filename)
    return int(match.group(1)) if match else float('inf')
    
sortedGoProFiles = sorted(goProFiles, key=extractNumber)

#Group the files that are only 1 number away since they are part of a single video
grouped = []
currentGroup = []
prevNum = None

for file in sortedGoProFiles:
    number = extractNumber(file)
    if prevNum is None or number == prevNum + 1:
        currentGroup.append(file)
    else:
        grouped.append(currentGroup)
        currentGroup = [file]
    prevNum = number
    
if currentGroup:
    grouped.append(currentGroup)

#print(grouped)

#Writing files of the groups to splice together with ffmpeg later
GoProTextFiles = []
for i, g in enumerate(grouped, start=1):
    #print(i)
    #print(g)
    textFileName = 'VideoList_' + str(i)
    GoProTextFiles.append(textFileName)
    with open(textFileName + '.txt', 'w') as f:
        for name in g:
            f.write('file ' + name + '\n')
            
#run ffmpeg command: ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
for i in GoProTextFiles:
    subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', i + '.txt', '-c', 'copy', i + '.mp4'])