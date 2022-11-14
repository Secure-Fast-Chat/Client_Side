import Message

def sendMessage(cmd,socket):
    """ Parse the messsage to send to the required user

    :param cmd: The cmd written after "\send "
    :type cmd: str
    :param socket: Connection socket
    :type socket: socket.socket
    """

    username = cmd.split(" ",1)[0]
    message = cmd.split(" ",1)[1]
    request = {
            'message-content' : message ,
            'recvr-username' : username
            }
    msg = Message.Message(socket,'send-message',req)
    response = msg.processTask()


def sendGroupMessage(cmd,socket):
    """ Parse the message to send to everyone in the group

    :param cmd: The cmd written after "\sendgrp "
    :type cmd: str
    :param socket: Connection socket
    :type socket: socket.socket
    """

    username = cmd.split(" ",1)[0]
    message = cmd.split(" ",1)[1]
    request = {
            'message-content' : message ,
            'recvr-guid' : username
            }
    msg = Message.Message(socket,'send-group-message',req)
    response = msg.processTask()

def handleUserInput(socket):
    """ This function is called when the user sends some input. This function does the work asked by user
    """

    userInput = input()
    if '\\sendgrp' == userInput[:8]:
        sendGroupMessage(userInput[9:],socket)
    elif '\\send' == userInput[:5]:
        sendMessage(userInput[6:],socket)
