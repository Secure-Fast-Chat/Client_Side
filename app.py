import Message
import selectors
import getpass
import socket

start_up_banner = """
***********************************************************************
**************************Welcome to FastChat**************************
***********************************************************************
           -Developed by: Khushang Singla, Mridul Agarwal, Arhaan Ahmad
"""

host = "127.0.0.0"
port = 8000

welcome_message = """    1. Login using and existing account
    2. Sign Up to make a new account
    3. Quit
      Enter Your Command(1/2/3): """

def login(sock = None):
    """Function to help user log in to the app

    :return: Socket with which user is connected to server
    :rtype: socket.socket"""

    uid = input("Enter Username: ")
    passwd = getpass.getpass(prompt = "Enter Password: ")
    print("  Connecting to Server...")
    if not sock:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            sock.connect((host,port))
        except ConnectionRefusedError:
            print(f"\nUnable to Connect to server on {host}:{port}")
            exit()

    # Use message class for sending request
    message = Message.Message(sock,'login',{'userid' : uid , 'password' : passwd})
    response = message.processTask()
    if(response == 1):
        print("Successfully Logged In")
        return sock
    elif response == 0:
        print("Invalid User Id or Password. Try Again")
        return login()
    elif response == 2:
        print("Unable to Login. Please Try Again.")
        return login()
    ##############################################################################################
    else:
        raise Exception("Why this Error in app.py -> login() ?") # Remove this if everything works correctly
    ##############################################################################################

def signup(sock = None):
    """Function to help user make new account

    :return: Socket with which user is connected to server
    :rtype: socket.socket"""
    username = input("Please enter username: ")
    password1 = getpass.getpass(prompt = "Enter Password: ")
    password2 = getpass.getpass(prompt = "Re-Enter Password: ")
    if password1 != password2:
        print("Password didn't match. Try Again!")
        return signup()
    # Do signup work
    print("  Connecting to Server...")
    if not sock:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host,port))
        except ConnectionRefusedError:
            print(f"\nUnable to Connect to server on {host}:{port}")
            exit()

    # Use message class for sending request for signup
    message = Message.Message(sock,'signup',{'userid' : username , 'password' : password1})
    response = message.processTask()
    if response == 0:
        print("This username is already taken. Sorry! Please try again with a different username")
        return signup()
    if response == 1:
        print("Account created successfully. Now you can login to your new account.\n")
        return login(sock)
    elif response == 2:
        print("Unable to signup. Please try Again.")
        return signup()
    ##############################################################################################
    else:
        raise Exception("Why this Error in app.py -> signup()?") # Remove this if everything works correctly
    ##############################################################################################

def handleUserInput():
    """ This function is called when the user sends some input. This function does the work asked by user
    """

    #Pending Implementation
    pass

def handleMessageFromServer(socket):
    """ This function is called when there is a message from server....
    """

    # Pending implementation
    pass

if __name__ == "__main__":
    conn_socket = None
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
                conn_socket = login()
                break
            elif cmd == '2':
                conn_socket = signup()
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

    # Setting up selectors for handling user-inputs and recieving messages
    sel = selectors.DefaultSelector()
    sel.register(0,selectors.EVENT_READ,data = 'user-input')
    sel.register(conn_socket,selectors.EVENT_READ,data = 'socket')

    # Loop for running the app
    while True:
        # Blocks until any input is recieved
        events = sel.select(timeout = None)
        for key,mask in events:
            if(key.data == 'user-input'):
                handleUserInput()
            else:
                handleMessageFromServer(key.fileobj)
