import os
import sys
from datetime import datetime
import Message
import selectors
import getpass
import socket
import userInputHandler
import nacl
import nacl.utils
from nacl.public import PrivateKey, Box
import hashlib
import struct
import json
from nacl.encoding import Base64Encoder

start_up_banner = """
***********************************************************************
**************************Welcome to FastChat**************************
***********************************************************************
           -Developed by: Khushang Singla, Mridul Agarwal, Arhaan Ahmad
"""

host = "127.0.0.1"
port = 8000


ENCODING_USED = "utf-8" 

welcome_message = """    1. Login using and existing account
    2. Sign Up to make a new account
    3. Quit
      Enter Your Command(1/2/3): """

serverkey = None # This is the public key of server to encrypt content to send to server
privatekey = None # This is the private key of client for recieving content from server
user_public_key = None # Public Key of user to encrypt messages being sent by other users

def connectToServer():
    """ Function to connect to server and exchange keys for encrypted connection

    :return: Connection Socket and box with keys for decryption and encryption
    :rtype: socket.socket,nacl.public.Box
    """

    print("Connecting to server")
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    try:
        sock.connect((host,port))
    except ConnectionRefusedError:
        print(f"\nUnable to Connect to server on {host}:{port}")
        exit()
    # Receive the public key of the server
    # First the server sends their key, then we send ours
    global privatekey
    privatekey = PrivateKey.generate()
    myPublicKey = privatekey.public_key
    message = Message.Message(sock,'keyex',{'key' : myPublicKey.encode(Base64Encoder).decode()}, box=None) 
    message.processTask()
    data = sock.recv(2)
    
    len_header = struct.unpack('>H',data)[0]
    data = sock.recv(len_header)
    header = json.loads(data.decode(ENCODING_USED))
    if header["request"] != "keyex":
        print("Error occurred while connecting")
        exit()
    global serverkey
    serverkey = nacl.public.PublicKey(header['key'], encoder=Base64Encoder) 
    print(f"Keys Exchanged. server public key = {serverkey}")
    print(f"My public key is {myPublicKey}")
    box = Box(privatekey, serverkey)
    
    return sock, box

def login(sock, box):
    """Function to help user log in to the app

    :param sock: Socket used for connection to server
    :type sock: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    :return: Socket with which user is connected to server
    :rtype: socket.socket
    """

    uid = input("Enter Username: ")
    passwd = getpass.getpass(prompt = "Enter Password: ")
    

    # Use message class for sending request
    message = Message.Message(sock,'login',{'userid' : uid , 'password' : passwd}, box)
    response = message.processTask()
    if(response == 0):
        print("Successfully Logged In")
        Message.e2ePrivateKey = PrivateKey(hashlib.sha256((uid+passwd).encode("utf-8")).digest())
        return sock
    elif response == 1:
        print("Invalid User Id. Try Again")
        return -1
    elif response == 2:
        print("Invalid Password. Please Try Again.")
        return -1
    elif response == 3:
        print("Uid type is not correct, uid can have only alphabets and underscore")
        return -1
    ##############################################################################################
    else:
        print(response)
        raise Exception("Why this Error in app.py -> login() ?") # Remove this if everything works correctly
    ##############################################################################################

def signup(sock, box):
    """Function to help user make new account

    :param sock: Socket used for connection to server
    :type sock: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    :return: Socket with which user is connected to server
    :rtype: socket.socket
    """

    username = input("Please enter username: ")
    print("Checking for availability of Username ... ")
    message = Message.Message(sock,'signupuid',{'userid' : username}, box)
    response = message.processTask()
    # Do signup work

    if response == 0:
        print("This username is already taken. Sorry! Please try again with a different username")
        return -1
    elif response == 2:
        print("This username type is invalid, please use only alphabets and underscore")
        return -1
    
    print("The username you requested for is available")
    password1 = getpass.getpass(prompt = "Enter Password: ")
    password2 = getpass.getpass(prompt = "Re-Enter Password: ")
    while password1 != password2:
        print("Passwords didn't match. Try Again!")
        password1 = getpass.getpass(prompt = "Enter Password: ")
        password2 = getpass.getpass(prompt = "Re-Enter Password: ")

    Message.e2ePrivateKey = PrivateKey(hashlib.sha256((username+password1).encode("utf-8")).digest()) 
    message = Message.Message(sock,'signuppass',{'password' :password1, "e2eKey":Message.e2ePrivateKey.public_key.encode(Base64Encoder).decode()}, box)
    response = message.processTask()
    if response == 1:
        print("Account created successfully. Now you can login to your new account.\n")
        return login(sock, box)
    elif response == 2:
        print("Unable to signup. Please try Again.")
        Message.e2ePrivateKey = None
        return signup(sock, box)
    ##############################################################################################
    else:
        raise Exception("Why this Error in app.py -> signup()?") # Remove this if everything works correctly
    ##############################################################################################

def handleMessageFromServer(socket,box):
    """ This function is called when there is a message from server....

    :param sock: Socket used for connection to server
    :type sock: socket.socket
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    msg = Message.Message(socket,'recv_msg','',box).processTask()
    to_print = ''
    if(msg['content-type'] == 'file'):
        filename = 'SecureFastChat_'+msg['sender'] + datetime.now().strftime("%H:%M:%S")
        f = open(filename,'wb')
        f.write(msg['content'])
        f.close()
        to_print = 'You recieved a file from ' + msg['sender'] + '. The address to access file is: ' + os.getcwd() + filename
    else:
        to_print = '[' + msg['sender'] + ' : ' + datetime.now().strftime("%H:%M:%S") + ']: ' + msg['content']

    f = open(os.path.join(os.path.expanduser('~'),'SecureFastChatMessages.txt'),'a')
    f.write(to_print+'\n')

    print('\033[s\033[3B'+to_print.strip() + '\033[K\033[u',end = '')
    sys.stdout.flush()

if __name__ == "__main__":
    os.system('clear')
    conn_socket = None
    conn_socket, box = connectToServer()
    sel = selectors.DefaultSelector()

    # Try to login/signup
    try:
        print(start_up_banner)
        while True:
            cmd = input(welcome_message)
            if cmd == '3':
                print("\n  Hope you use the app again  ")
                exit()
                break
            elif cmd == '1':
                if login(conn_socket, box) != -1:
                    break
            elif cmd == '2':
                if signup(conn_socket, box) != -1:
                    break
            else:
                print("\n  Please Enter a valid Command\n")
    except KeyboardInterrupt:
        print("\nThanks For using the app!!")
        if conn_socket:
            conn_socket.close()
        exit()
    except:
        raise

    # print("\n\n\n")
    # Setting up selectors for handling user-inputs and recieving messages
    sel.register(0,selectors.EVENT_READ,data = {'type':'user-input', 'box':box})
    sel.register(conn_socket,selectors.EVENT_READ,data = {'type':'socket', 'box':box})

    print("\n\n")
    # Loop for running the app
    while True:
        # Blocks until any input is recieved
        events = sel.select(timeout = None)
        for key,mask in events:
            # print('going good ',key)
            if(key.data['type'] == 'user-input'):
                userInputHandler.handleUserInput(conn_socket,box)
            else:
                handleMessageFromServer(key.fileobj,box)
