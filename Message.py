import json
import struct
import sys

PROTOHEADER_LENGTH = 2 # to store length of protoheader
ENCODING_USED = "utf-8" # to store the encoding used
                        # The program uses universal encoding

class Message:
    """This is the class to handle Encryption of messages. The format in which the message is sent to server is determined in this class

    :param task: Task to be done. It can have the values signup, login, send_message
    :type task: str
    :param socket: The socket used for connection with Server
    :type socket: socket.socket
    :param request_content: Content to include in the request to send to server
    :type request_content: dict
    :param _data_to_send: Contains the data to send to the server
    :type _data_to_send: bytes
    :param _recvd_msg: Content recieved from server is stored here
    :type _recvd_msg: bytes
    """

    def __init__(self,conn_socket,task,request):
        """Constructor Object

        :param conn_socket: Socket which has a connection with server
        :type conn_socket: socket.socket
        :param task: Task to do. It can have values: login, signup, send_message
        :type task: str
        :param request: Content to send to server
        :type request: str
        """
        self.task = task
        self.socket = conn_socket
        self.request_content = request
        self._data_to_send = b''

    def _send_data_to_server(self):
        """ Function to send the string to the server. It sends content of _send_data_to_server to the server

        """
        left_message = self._data_to_send
        while left_message:
            bytes_sent = self.socket.send(left_message)
            left_message = left_message[bytes_sent:]
        return

    def _recv_data_from_server(self,size):
        """ Function to recv data from server. Stores the bytes recieved in a variable named _recvd_msg.

        :param size: Length of content to recieve from server
        :type size: int
        """

        self._recvd_msg = self.socket.recv(size)
        return

    def _json_encode(self, obj, encoding):
        """Function to encode dictionary to bytes object

        :param obj: dictionary to encode
        :type obj: dict
        :param encoding: Encoding to use
        :type encoding: str
        :return: Encoded obj
        :rtype: bytes"""

        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _hash_password(self,passwd):
        """Function to salt and hash the password before sending to server

        :param passwd: Password to be hashed
        :type passwd: str
        :return: Transformed Password
        :rtype: string
        """

        ###################################################
        ########## Pending Implementation #################
        ###################################################
        return passwd

    def _create_login_request(self):
        """ The jsonheader has the following keys: |
        byteorder, request, content-length, content-encoding. The value for request is 'login' |
        The content has user id and password separated using '\0\0\0\0\0\0\0\0'

        :return: Message to send to server directly for login
        :rtype: bytes
        """

        global ENCODING_USED
        userid = self.request_content['userid']
        password = self._hash_password(self.request_content['password'])
        content = bytes(userid + '\0'*8 + password,encoding=ENCODING_USED)
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'login',
            'content-length' : len(content),
            "content-encoding" : ENCODING_USED,
        }
        encoded_json_header = self._json_encode(jsonheader,ENCODING_USED)
        proto_header = struct.pack('>H',len(encoded_json_header))
        # Command to use for unpacking of proto_header: 
        # struct.unpack('>H',proto_header)[0]
        return proto_header + encoded_json_header + content

    def _create_signup_request(self):
        """ The jsonheader has the following keys: |
        byteorder, request, content-length, content-encoding. The value for request is 'signup' |
        The content has user id and password separated using '\0\0\0\0\0\0\0\0'

        :return: Message to send to server directly for login
        :rtype: bytes
        """

        global ENCODING_USED
        userid = self.request_content['userid']
        password = self._hash_password(self.request_content['password'])
        content = bytes(userid + '\0'*8 + password, encoding=ENCODING_USED)
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'signup',
            'content-length' : len(content),
            "content-encoding" : ENCODING_USED,
        }
        encoded_json_header = self._json_encode(jsonheader,ENCODING_USED)
        proto_header = struct.pack('>H',len(encoded_json_header))
        # Command to use for unpacking of proto_header: 
        # struct.unpack('>H',proto_header)[0]
        return proto_header + encoded_json_header + content

    def _login(self):
        """ Function to help login into the system. This function sends the login details to the server |
        The function expects to recieve a response of size 2 from server which gives 0 if invalid id/password and 1 if successful login and 2 for any other case

        :return: Response from server converted to int
        :rtype: int
        """

        self._data_to_send = self._create_login_request()
        self._send_data_to_server()
        # Recieve login result from server
        self._recv_data_from_server(2)
        return struct.unpack('>H',self._recvd_msg)[0]

    def _signup(self):
        """ Function to help signup to make new account. This function sends the new user details to the server |
        The function expects to recieve a response of size 2 from server which gives 0 if username already taken and 1 if successful login and 2 for any other case

        :return: Response from server converted to int
        :rtype: int
        """

        self._data_to_send = self._create_signup_request()
        self._send_data_to_server()
        # Recieve login result from server
        self._recv_data_from_server(2)
        return struct.unpack('>H',self._recvd_msg)[0]

    def processTask(self):
        """ Processes the task to do

        :return: Returns int to represent result of the process. The details of return values are given in the corresponding functions handling the actions.
        :rtype: int
        """
        if self.task == 'login':
            return self._login()
        if self.task == 'signup':
            return self._signup()
