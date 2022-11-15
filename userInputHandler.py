import Message
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


def sendMessage(cmd,content_type,socket):
    """ Parse the messsage to send to the required user

    :param cmd: The cmd written after "\send "
    :type cmd: str
    :param socket: Connection socket
    :type socket: socket.socket
    """

    username = cmd.split(" ",1)[0]
    message = cmd.split(" ",1)[1]
    if content_type == 'file':
        f = open(message,'rb')
        message = f.read()
        f.close()

    request = {
            'message-content' : message ,
            'content-type' : content_type,
            'recvr-username' : username 
            }
    msg = Message.Message(socket,'send-message',req)
    response = msg.processTask()

def sendGroupMessage(cmd,content_type,socket):
    """ Parse the message to send to everyone in the group

    :param cmd: The cmd written after "\sendgrp "
    :type cmd: str
    :param socket: Connection socket
    :type socket: socket.socket
    """

    username = cmd.split(" ",1)[0]
    message = cmd.split(" ",1)[1]
    if content_type == 'file':
        f = open(message,'rb')
        message = f.read()
        f.close()

    request = {
            'message-content' : message ,
            'content-type' : content_type ,
            'recvr-username' : username 
            }
    msg = Message.Message(socket,'send-group-message',req)
    response = msg.processTask()

def createGroup(cmd,socket):
    """ Create a group with the name cmd

    :param cmd: Group name
    :type cmd: str
    :param socket: Socket which is connected to server
    :type socket: socket.socket
    """

    is_valid = checkValidityOfUID(cmd)
    if not is_valid:
        print("Invalid UID for group. Please use only alphabets, numbers or _ in the group name")
    response = Message.Message(socket,'create-grp',cmd).processTask()
    
    if response == 0:
        print("Successfully Created Group")
    elif response == 1:
        print("Group with this id already exists. Couldn't create group.")

def handleUserInput(socket):
    """ This function is called when the user sends some input. This function does the work asked by user

    """

    userInput = input()
    if '\\send ' == userInput[:6]:
        sendMessage(userInput[6:],'text',socket)
    elif '\\sendfile ' == userInput[:10]:
        sendMessage(userInput[10:],'file',socket)
    elif '\\sendgrp ' == userInput[:9]:
        sendGroupMessage(userInput[9:],'text',socket)
    elif '\\sendfilegrp ' == userInput[:13]:
        sendGroupMessage(userInput[13:],'file',socket)
    elif '\\mkgrp ' == userInput[:7]:
        createGroup(userInput[7:],socket)
