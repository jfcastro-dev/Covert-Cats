# Covert Cats

![alt text](cc.png "Data Transmission")

Covert Cats is a proof of concept covert command & control channel. It was created for
our Offensive Security course, for which all group members received As.

It specifically masks "malicious" traffic, through Twitter's API using messages embedded in images of cats, which are then publicly tweeted.

## A Note to Script Kitties
Yes, this was pun intended. The project is specifically proof of concept, and as such, if one were to copy it verbatim for otherwise illegal purposes,
they'd encounter some issues. For instance, we deliberately left all embedded messages in plaintext. We also used Twitter's API rather than something
more covert like a headless browser with the headers modified.

## A Note to those Testing
The API limits with respect to demoing had issues - This is meant that we could not 
demonstrate in a timely manner. In order to run how it is meant to be run, the global variable interval in clients
should be set to a reasonable timeframe (~900 seconds), and scaled accordingly for the number of clients it is
supporting. Alternatively, purchasing an API Key with more requests for a larger scale production is likely required. 
Or, one could bypass this limit as previously stated, via headless browser frameworks.

## Proof of Transfer
* [Click here to view the record of the transactions](https://twitter.com/NateSBU)
* Download the files and run decode.py as root to see the hidden messages.

## Description
The server is divided into two portions, the server and the client(s):


### client
* Client uses scapy to dynamically monitor traffic. If no one is using the computer, don't check for new messages. Else, do.
* The way we determine this is via TCP requests. They are both periodic and asynchronous in the sense that it will check every 5-60 minutes+ if and only if there are outgoing requests from the machine. This is currently set to 60 seconds because
of the demo.
* However, TCP Traffic is very common. Utilizing Strict Mode will much more safely ensure that traffic isn't checked
unless the user is on his or her computer.
* The reason for these limits is because the twitter API limits the amount of requests to 15 per 15 minutes. So if you'd like to scale up your number of clients, you will also have to scale up the amount of time they wait.

### server 
* Keeps track of all the active clients and has the ability to send/receive messages from clients.
* Check the Twitter every few minutes to check for client receipts (the time frame needs to be scaled according to numClients)

#### server commands
Because this is proof of concept, we limited the malicious capabilities of this.
Most commands are in the format, "[ID] Command [Arg]". Below is a list of all the commands that one can execute and a short explaination of what they do:
* [ID] Download [URL] - Downloads a file from the URL at Client with id [ID]
* [ID] Upload [FilePath] - Uploads a file to the server from the client.
* [ID] Kill Null - Kills Client with id [ID]
* [ID] ls [None] - Acquires the directory from Client with id [ID]

###### server specific commands
These following commands are ran the same as the previous but do not have any effect on the clients. It still may make Twitter API requests:
* 0 Shutdown - Shuts down server
* 0 Listen - Switches to Listening Mode
* 0 List - Lists all active clients
* 0 Scan - Manually scans once
* 0 Status - Prints time till API rate reset

### Notable files
**handleMessage.py** - Handles the encoding/decoding of messages.

**keys.py** - Keys used to access the Twitter API, the keys currently in this folder are nonfunctioning and only for demonstration.

**cats** - A folder containing a ton of cat photos that will be used to encode messages.

**msgs.txt** - Prewritten Messages to accompany pictures on twitter to help the bot become more inconspicuous

## Installation
pip3 install -r pkgs.txt for packages we used
pip3 install textract

## How to Run
### Linux
1. Enter `sudo python3 server.py` - in the /server directory
2. Enter `sudo python3 client.py [ID]` in the /client directory with ID being the desired ID of the client

### Windows 
1. Make sure that the terminal you are running this program is Running as Administrator
2. Enter `python server.py` - in the /server directory
3. Enter `python client.py [ID]` in the /client directory with ID being the desired ID of the client

## Team and Contributions
"CCC on the CNC" - J.C.
* James Castro - Implementing client/server functionality, encoding/decoding, and more
* Thomas Clarke - Crafting project specifications and parameters
* Nathaniel Chan - Twitter API implementation 

## Bugs
* Download/Upload Receipts may Hang.
