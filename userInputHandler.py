import Message
import datetime
import os
import sys
import nacl
import re

USERNAME = None

def checkValidityOfUID(uid):
    """ Function to check if the uid is valid. A valid uid is one which has only a-z,A-Z,0-9,_ characters

    :param uid: User id to check for
    :type uid: str
    :return: Return True if valid
    :rtype: bool
    """

    pattern = re.compile(r'[a-zA-Z0-9_]+')
    if not re.fullmatch(pattern,uid):
        return False
    return True

def updateLogs(logs):
    print("\033[3A",end='')
    print(logs,end='')
    print("\033[K\n\033[2B",end='')
    f = open(f"SecureFastChatlogs_{USERNAME}.txt",'a')
    f.write(logs+'\n')
    f.close()

def sendMessage(cmd,content_type,socket,box):
    """ Parse the messsage to send to the required user

    :param cmd: The cmd written after "\send "
    :type cmd: str
    :param socket: Connection socket
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    log = str(datetime.datetime.timestamp(datetime.datetime.now()))+" : " 
    username = cmd.split(" ",1)[0]
    message = cmd.split(" ",1)[1]
    if content_type == 'file':
        if not os.path.exists(message):
            log += "Couldn't find file : "+message
            updateLogs(log)
            return
        f = open(message,'rb')
        message = f.read()
        f.close()
    else:
        # global Message.ENCODING_USED
        message = message.encode(Message.ENCODING_USED)

    request = {
            'message-content' : message ,
            'content-type' : content_type,
            'recvr-username' : username 
            }
    msg = Message.Message(socket,'send-message',request,box)
    response = msg.processTask()
    if response == 0:
        log += "Message Sent Successfully"
    if response == 1:
        log +="No user with userid: "+username
    updateLogs(log)

def sendGroupMessage(cmd,content_type,socket,box):
    """ Parse the message to send to everyone in the group

    :param cmd: The cmd written after "\sendgrp "
    :type cmd: str
    :param content_type: Type of message content, i.e. file or text. It is 'file' or 'text'
    :type content_type: str
    :param socket: Connection socket
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    # log = datetime.datetime.now().strftime("[ %d/%m/%Y | %H:%M:%S ] : ")
    log = str(datetime.datetime.timestamp(datetime.datetime.now()))+" : " # TODO
    groupName = cmd.split(" ",1)[0]
    message = cmd.split(" ",1)[1]
    if content_type == 'file':
        if not os.path.exists(message):
            log += "Couldn't find file : "+message
            updateLogs(log)
            return
        f = open(message,'rb')
        message = f.read()
        f.close()
    else:
        message = message.encode(Message.ENCODING_USED)

    request = {
            'message-content' : message ,
            'content-type' : content_type ,
            'guid' : groupName 
            }
    msg = Message.Message(socket,'send-group-message',request,box)
    response = msg.processTask()
    if response == 0:
        log += "Message Sent Successfully"
    if response == 1:
        log += "Couldn't Send"
    if response == 2:
        log += "No group with group name "+groupName
    updateLogs(log)

def createGroup(cmd,socket,box):
    """ Create a group with the name cmd

    :param cmd: Group name
    :type cmd: str
    :param socket: Socket which is connected to server
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    log = str(datetime.datetime.timestamp(datetime.datetime.now())) +" : "
    is_valid = checkValidityOfUID(cmd)
    if not is_valid:
        log += "Invalid UID for group. Please use only alphabets, numbers or _ in the group name"
        updateLogs(log)
        return
    response = Message.Message(socket,'create-grp',cmd,box).processTask()
    
    if response == 0:
        log += "Successfully Created Group"
    elif response == 1:
        log += "Group with this id already exists. Couldn't create group."
    updateLogs(log)

def addMemberInGroup(cmd,socket,box):
    """ Function to add member in a group

    :param cmd: The part of command containing group name and new member userid
    :type cmd: str
    :param socket: Socket with active authorized connection to server
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    log = str(datetime.datetime.timestamp(datetime.datetime.now()))+" : " 
    grpName = cmd.split(' ')[0]
    userID = cmd.split(' ')[1]
    req = {
            'guid' : grpName,
            'new-uid' : userID
            }
    response = Message.Message(socket,'add-mem',req,box).processTask()
    if response == 0:
        log += "Successfully Added New Member in Group"
    elif response == 1:
        log += "There is no group with this name"
    elif response == 2:
        log += "You are not authorized to add Members in this group"
    elif response == 3:
        log += 'There is no user with username: ' + userID
    updateLogs(log)

def leaveGroup(cmd,socket,box):
    """ Function to leave a group

    :param cmd: The part of command containing group name
    :type cmd: str
    :param socket: Socket with active authorized connection to server
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    log = str(datetime.datetime.timestamp(datetime.datetime.now()))+" : " 
    response = Message.Message(socket,'leave-grp',cmd,box).processTask()
    if response == 0:
        log += "Group Successfully Removed"
    elif response == 1:
        log += "There is no group with this name"
    updateLogs(log)

def removeMemberFromGroup(cmd,socket,box):
    """ Function to add member in a group

    :param cmd: The part of command containing group name and member userid
    :type cmd: str
    :param socket: Socket with active authorized connection to server
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    log = str(datetime.datetime.timestamp(datetime.datetime.now()))+" : " 
    grpName = cmd.split(' ')[0]
    userID = cmd.split(' ')[1]
    req = {
            'guid' : grpName, 'uid' : userID }
    response = Message.Message(socket,'remove-mem',req,box).processTask()
    if response == 0:
        log += "Successfully Removed From the Group"
    elif response == 1:
        log += "There is no group with the name: " + grpName
    elif response == 2:
        log += "You are not authorized to remove Members in this group"
    elif response == 3:
        log += 'There is no user with username: ' + userID
    updateLogs(log)

def handleUserInput(socket,box):
    """ This function is called when the user sends some input. This function does the work asked by user

    :param socket: Socket for connection with server
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    userInput = input()
    try:
        if '\\send ' == userInput[:6]:
            sendMessage(userInput[6:],'text',socket,box)
        elif '\\sendfile ' == userInput[:10]:
            sendMessage(userInput[10:],'file',socket,box)
        elif '\\sendgrp ' == userInput[:9]:
            sendGroupMessage(userInput[9:],'text',socket,box)
        elif '\\sendfilegrp ' == userInput[:13]:
            sendGroupMessage(userInput[13:],'file',socket,box)
        elif '\\mkgrp ' == userInput[:7]:
            createGroup(userInput[7:],socket,box)
        elif '\\addmem ' == userInput[:8]:
            addMemberInGroup(userInput[8:],socket,box)
        elif '\\rmmem ' == userInput[:7]:
            removeMemberFromGroup(userInput[7:],socket,box)
        elif '\\rmgrp ' == userInput[:7]:
            leaveGroup(userInput[7:],socket,box)
        elif '\\logout' == userInput:
            socket.close()
            log = str(datetime.datetime.timestamp(datetime.datetime.now()))+" : " 
            log += "User Logged Out"
            updateLogs(log)
            print("\n\n")
            exit()
        else:
            log = str(datetime.datetime.timestamp(datetime.datetime.now()))+" : " 
            log += "Invalid Command"
            updateLogs(log)
    except(IndexError):
        log = str(datetime.datetime.timestamp(datetime.datetime.now()))+" : " 
        log += "Invalid Command"
        updateLogs(log)
    print("\033[1A\033[K",end = '')
    sys.stdout.flush()
