#this script is meant to concat the go pro splits made from porting the videos onto a machine
#I'm assumming you already know the folder you're working in

import os, re, subprocess, platform
from CheckLibraryInstallation import CheckLibrary

#Use a config file to store the path and/or drive to where the user has their go pro files

#check if ffmpeg is installed
if not CheckLibrary("ffmpeg"):
    print("Please install ffmpeg to use this script.")
    quit()

# platform.system() returns 'Windows', 'Linux', or 'Darwin' (macOS)
currentOS = platform.system()
isWSL = False

if currentOS == "Linux":
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                isWSL = True
    except FileNotFoundError:
        pass  # /proc/version won't exist on non-Linux systems, safe to ignore
 
print(f"Detected OS: {currentOS}{' (WSL)' if isWSL else ''}")


isInDirectory = input("Are we already in the directory you want? ").lower() in ('yes', 'y')

if not isInDirectory:
    rawPath = input("Paste the full path to your GoPro splits folder: ").strip()
 
    # WSL path conversion:
    # If the user is on WSL and pastes a Windows-style path like C:\foo\bar,
    # we need to convert it to the WSL mount format /mnt/c/foo/bar.
    # We check if it looks like a Windows path (e.g. starts with a drive letter like C:\)
    # and if /mnt/ isn't already prepended.
    if isWSL and not rawPath.startswith("/mnt/"):
        if len(rawPath) >= 2 and rawPath[1] == ":":
            driveLetter = rawPath[0].lower()
            remainder = rawPath[2:].replace("\\", "/")
            rawPath = f"/mnt/{driveLetter}{remainder}"
            print(f"Converted to WSL path: {rawPath}")
 
    os.chdir(rawPath)
 
print(f"Working directory: {os.getcwd()}")
    
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