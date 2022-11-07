import Message
import selectors
import getpass
import socket
import userInputHandler

start_up_banner = """
***********************************************************************
**************************Welcome to FastChat**************************
***********************************************************************
           -Developed by: Khushang Singla, Mridul Agarwal, Arhaan Ahmad
"""

host = "127.0.0.1"
port = 8000

welcome_message = """    1. Login using and existing account
    2. Sign Up to make a new account
    3. Quit
      Enter Your Command(1/2/3): """

def login(sock = None):
    """Function to help user log in to the app

    :return: Socket with which user is connected to server
    :rtype: socket.socket
    """

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
    if(response == 0):
        print("Successfully Logged In")
        return sock
    elif response == 1:
        print("Invalid User Id. Try Again")
        return login()
    elif response == 2:
        print("Invalid Password. Please Try Again.")
        return login()
    ##############################################################################################
    else:
        print(response)
        raise Exception("Why this Error in app.py -> login() ?") # Remove this if everything works correctly
    ##############################################################################################

def signup(sock = None):
    """Function to help user make new account

    :return: Socket with which user is connected to server
    :rtype: socket.socket"""

    if not sock:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host,port))
        except ConnectionRefusedError:
            print(f"\nUnable to Connect to server on {host}:{port}")
            exit()
    username = input("Please enter username: ")
    print("Checking for availability of Username ... ")
    message = Message.Message(sock,'signupuid',{'userid' : username})
    response = message.processTask()
    # Do signup work
    print("  Connecting to Server...")

    if response == 0:
        print("This username is already taken. Sorry! Please try again with a different username")
        return signup(sock)
    
    return_code, key = response
    print("The username you requested for is available")
    password1 = getpass.getpass(prompt = "Enter Password: ")
    password2 = getpass.getpass(prompt = "Re-Enter Password: ")
    while password1 != password2:
        print("Passwords didn't match. Try Again!")
        password1 = getpass.getpass(prompt = "Enter Password: ")
        password2 = getpass.getpass(prompt = "Re-Enter Password: ")
    # Use message class for sending password for signup
    message = Message.Message(sock,'signuppass',{'password' : password1,'key' : key})
    response = message.processTask()
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

def handleMessageFromServer(socket):
    """ This function is called when there is a message from server....
    """

    # Pending implementation
    print('\033[1;2H'+msg+'\033[10;1H')

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
                userInputHandler.handleUserInput()
            else:
                handleMessageFromServer(key.fileobj)
