import Message

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
            'content-type' : content_type
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
            'content-type' : content_type
            'recvr-username' : username 
            }
    msg = Message.Message(socket,'send-group-message',req)
    response = msg.processTask()

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
