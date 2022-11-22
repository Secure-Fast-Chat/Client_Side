import Message
import os
import sys
import nacl
import re

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

def sendMessage(cmd,content_type,socket,box):
    """ Parse the messsage to send to the required user

    :param cmd: The cmd written after "\send "
    :type cmd: str
    :param socket: Connection socket
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    username = cmd.split(" ",1)[0]
    message = cmd.split(" ",1)[1]
    if content_type == 'file':
        if not os.path.exists(message):
            print("\033[3A"+"Couldn't find file : "+message+"\033[K\n\033[2B",end = '')
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
        return
    if response == 1:
        print("\033[3A"+"No user with userid: {username}"+"\033[K\n\033[2B",end = '')

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

    groupName = cmd.split(" ",1)[0]
    message = cmd.split(" ",1)[1]
    if content_type == 'file':
        if not os.path.exists(message):
            print("\033[3A"+"Couldn't find file : "+message+"\033[K\n\033[2B",end = '')
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
        return
    if response == 1:
        print("\033[3A"+"Couldn't Send"+"\033[K\n\033[2B",end = '')
    if response == 2:
        print("\033[3A"+"No group with group name "+groupName+"\033[K\n\033[2B",end = '')

def createGroup(cmd,socket,box):
    """ Create a group with the name cmd

    :param cmd: Group name
    :type cmd: str
    :param socket: Socket which is connected to server
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    is_valid = checkValidityOfUID(cmd)
    if not is_valid:
        print("\033[3A",end = '')
        print("Invalid UID for group. Please use only alphabets, numbers or _ in the group name",end='')
        print("\033[K\n\033[2B",end='')
        return
    response = Message.Message(socket,'create-grp',cmd,box).processTask()
    
    if response == 0:
        print("\033[3A",end='')
        print("Successfully Created Group",end='')
        print("\033[K\n\033[2B",end='')
    elif response == 1:
        print("\033[3A",end='')
        print("Group with this id already exists. Couldn't create group.",end='')
        print("\033[K\n\033[2B",end='')

def addMemberInGroup(cmd,socket,box):
    """ Function to add member in a group

    :param cmd: The part of command containing group name and new member userid
    :type cmd: str
    :param socket: Socket with active authorized connection to server
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    grpName = cmd.split(' ')[0]
    userID = cmd.split(' ')[1]
    req = {
            'guid' : grpName,
            'new-uid' : userID
            }
    response = Message.Message(socket,'add-mem',req,box).processTask()
    if response == 0:
        print("\033[3A",end='')
        print("Successfully Added New Member in Group",end='')
        print("\033[K\n\033[2B",end='')
    elif response == 1:
        print("\033[3A",end='')
        print("There is no group with this name",end='')
        print("\033[K\n\033[2B",end='')
    elif response == 2:
        print("\033[3A",end='')
        print("You are not authorized to add Members in this group",end='')
        print("\033[K\n\033[2B",end='')
    elif response == 3:
        print("\033[3A",end='')
        print(f'There is no user with username: {userID}',end='')
        print("\033[K\n\033[2B",end='')

def handleUserInput(socket,box):
    """ This function is called when the user sends some input. This function does the work asked by user

    :param socket: Socket for connection with server
    :type socket: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    userInput = input()
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
    print("\033[1A\033[K",end = '')
    sys.stdout.flush()
