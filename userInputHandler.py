def sendMessage(cmd):
    """ Parse the messsage to send to the required user

    :param cmd: The cmd written after "\send "
    :type cmd: str
    """

def handleUserInput():
    """ This function is called when the user sends some input. This function does the work asked by user
    """

    userInput = input()
    if '\\send' == userInput[:5]:
        sendMessage(userInput[6:])
