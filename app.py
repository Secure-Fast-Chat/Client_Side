import Message
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

def login():
    """Function to help user log in to the app

    :return: Socket with which user is connected to server
    :rtype: socket.socket"""

    uid = input("Enter Username: ")
    passwd = getpass.getpass(prompt = "Enter Password: ")
    print("  Connecting to Server...")
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #   try:
    #       sock.connect((host,port))
    #   except ConnectionRefusedError:
    #       print(f"\nUnable to Connect to server on {host}:{port}")
    #       exit()

    # Use message class for sending request
    message = Message.Message(sock,'login',{'userid' : uid , 'password' : passwd})
    response = message.processTask()
    if(response == 1):
        print("Successfully Logged In")
        return sock
    elif response == -1:
        print("Invalid User Id or Password. Try Again")
        return login()
    else:
        print("Unable to Login. Please Try Again.")
        return login()




if __name__ == "__main__":
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
                login()
                break
            elif cmd == '2':
                signup()
                break
            else:
                print("\n  Please Enter a valid Command\n")
    except KeyboardInterrupt:
        print("\nThanks For using the app!!")
        exit()
    except:
        raise
