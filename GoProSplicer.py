#this script is meant to concat the go pro splits made from porting the videos onto a machine
#I'm assumming you already know the folder you're working in

import os, re, subprocess

isWSL = input("Are we in WSL? ").lower() in ('yes', 'y')
#make a windows version
#check if ffmpeg is installed

isInDirectory = input("Are we already in the directory you want? ").lower() in ('yes', 'y')

def folderSearch(folderName, drive):
    command = [
        "powershell.exe",
        "-Command",
        f"Get-ChildItem -Path {drive}:\\ -Recurse -Directory "
        f"| Where-Object {{$_.Name -like '*{folderName}*'}} "
        f"| Select-Object -First 1 -ExpandProperty FullName"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    path = result.stdout.strip()
    return path if path else None

if not isInDirectory:
    drive = input("What drive will we be working in? ")
    if isWSL:
        os.chdir("/mnt/" + drive.lower())
    else:
        os.chdir(drive.lower())
    directory = input("Input directory of Go Pro Spilts: ")
    #print(folderSearch(directory, drive))
    os.chdir("/mnt/" + folderSearch(directory, drive).replace("\\", "/").lower().replace(":",""))
    
#Ask if the user wants the videos invidviually or a master video(All of them combined)
MasterVideo = input("Last question, would you like all the go pro videos spliced into a Master Video? ").lower() in ('yes', 'y')

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
#print(sortedGoProFiles)

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
    elif filenumber[1] == 1 and prevEndNum + 1 == filenumber[0]:
        prevBegNum = filenumber[1]
        prevEndNum = filenumber[0]
        currentGroup.append(file)
    
#print(currentGroup)
if currentGroup:
    grouped.append(currentGroup)

print(grouped)

#Writing files of the groups to splice together with ffmpeg later
GoProTextFiles = []
textFileName = ''
if MasterVideo:
    textFileName = 'MasterVideo'
    for i, g in enumerate(grouped, start=1):
        with open(textFileName + '.txt', 'w') as f:
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
else
    subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', textFileName + '.txt', '-c', 'copy', i + '.mp4'])