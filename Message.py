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

    def _recv_data_from_server(self,size, authenticated=True):
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

    def _json_decode(self, obj, encoding):
        """Function to decode bytes object to dictionary

        :param obj: Encoded json data
        :type obj: bytes
        :param encoding: Encoding used
        :type encoding: str
        :return: Decoded json object
        :rtype: json"""

        return json.loads(obj.decode(encoding))

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

    def _encode(self,text,key):
        """ Function to encode the text using key from server

        :param text: string to encode
        :type text: str
        :param key: key for encryption
        :type key: str
        :return: Encoded text
        :rtype: str
        """

        ###################################################
        ########## Pending Implementation #################
        ###################################################
        # Commented out instances of this for now, because we are sending the plain text password to the server for now, remember to uncomment them if we change minds
        return text

    def _encrypt(self,msg,key):
        """ Encrypt the message to send to reciever

        :param msg: Message to encrypt
        :type msg: str
        :param key: Key to encrypt the message
        :type key: str
        """
        ########################################################
        ############### Pending Implementation #################
        ########################################################
        return msg
    
    def _create_loginpass_request(self):
        """ The jsonheader has the following keys: |
        byteorder, request, content-length, content-encoding. 

        :return: Message to send to server directly for login
        :rtype: bytes
        """

        global ENCODING_USED
        userid = self.request_content['userid']
        # hashed_password = self._hash_password(self.request_content['password'])
        content = bytes(self.request_content['password'],encoding=ENCODING_USED)
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'loginpass',
            'content-length' : len(content),
            "content-encoding" : ENCODING_USED,
        }
        encoded_json_header = self._json_encode(jsonheader,ENCODING_USED)
        proto_header = struct.pack('>H',len(encoded_json_header))
        # Command to use for unpacking of proto_header: 
        # struct.unpack('>H',proto_header)[0]
        return proto_header + encoded_json_header + content

    def _create_loginuid_request(self):
        """ The jsonheader has the following keys: |
        byteorder, request, content-length, content-encoding. The value for request is 'loginuid' |
        The content has user id.

        :return: Message to send to server directly for login
        :rtype: bytes
        """

        global ENCODING_USED
        userid = self.request_content['userid']
        content = bytes(userid ,encoding=ENCODING_USED)
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'loginuid',
            'content-length' : len(content),
            "content-encoding" : ENCODING_USED,
        }
        encoded_json_header = self._json_encode(jsonheader,ENCODING_USED)
        proto_header = struct.pack('>H',len(encoded_json_header))
        # Command to use for unpacking of proto_header: 
        # struct.unpack('>H',proto_header)[0]
        return proto_header + encoded_json_header + content

    def _create_signuppass_request(self):
        """ The jsonheader has the following keys: |
        byteorder, request, content-length, content-encoding. The value for request is 'signuppass' |
        The content has encoded password

        :return: Message to send to server directly for login
        :rtype: bytes
        """

        global ENCODING_USED
        # password = self._hash_password(self.request_content['password'])
        content = bytes(self._encode(self.request_content["password"]), encoding=ENCODING_USED) 
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'signuppass',
            'content-length' : len(content),
            "content-encoding" : ENCODING_USED,
        }
        encoded_json_header = self._json_encode(jsonheader,ENCODING_USED)
        proto_header = struct.pack('>H',len(encoded_json_header))
        # Command to use for unpacking of proto_header: 
        # struct.unpack('>H',proto_header)[0]
        return proto_header + encoded_json_header + content

    def _create_signupuid_request(self):
        """ The jsonheader has the following keys: |
        byteorder, request, content-length, content-encoding. The value for request is 'signupuid' |
        The content has user id.

        :return: Message to send to server directly for login
        :rtype: bytes
        """

        global ENCODING_USED
        userid = self.request_content['userid']
        content = bytes(userid , encoding=ENCODING_USED)
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'signupuid',
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
        The function expects to recieve a response of size 2 from server which gives 0 if success and 1 if wrong uid and 2 for wrong passwd

        :return: Response from server converted to int
        :rtype: int
        """

        self._data_to_send = self._create_loginuid_request()
        self._send_data_to_server()
        # Recieve login result from server
        self._recv_data_from_server(2)
        header_length = struct.unpack('>H',self._recvd_msg)[0]
        self._recv_data_from_server(header_length)
        header = self._json_decode(self._recvd_msg,ENCODING_USED)
        if not header['uid_found']:
            return 2
        logintoken = header['logintoken']
        self._data_to_send = self._create_loginpass_request(logintoken)
        self._send_data_to_server()
        self._recv_data_from_server(2)
        return struct.unpack('>H',self._recvd_msg)[0]

    def _signuppass(self):
        """ Function to save account password at server
        The function expects to recieve a response of size 2 from server which gives 0 if username already taken and 1 for success

        :return: Response from server converted to int
        :rtype: int
        """

        self._data_to_send = self._create_signuppass_request()
        self._send_data_to_server()
        # Recieve login result from server
        self._recv_data_from_server(2)
        return struct.unpack('>H',self._recvd_msg)[0]

    def _signupuid(self):
        """ Function to help signup to make new account. This function sends the new user userid to the server |
        The function expects to recieve a response of size 2 from server which gives 0 if username already taken and 1 if username is available

        :return: Response from server converted to int
        :rtype: int
        """

        self._data_to_send = self._create_signupuid_request()
        self._send_data_to_server()
        # Recieve login result from server
        self._recv_data_from_server(2)
        len_header = struct.unpack('>H',self._recvd_msg)[0]
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg, ENCODING_USED)
        if header['availability'] == 0:
            return 0
        key = header['key']
        return 1,key

    def _keyex(self):
        global ENCODING_USED
        publickey = self.request_content['key']
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'keyex',
            "key": publickey,
            "content-encoding" : ENCODING_USED,
            
        }
        encoded_json_header = self._json_encode(jsonheader,ENCODING_USED)
        proto_header = struct.pack('>H',len(encoded_json_header))
        # Command to use for unpacking of proto_header: 
        # struct.unpack('>H',proto_header)[0]
        self._data_to_send = proto_header + encoded_json_header # Not sending any content since the data is in the header
        self._send_data_to_server()
 
    def _recvmsg(self):
        """ Recieves the information from server. It interprets this as a message from some user and returns the message recieved. The header of recieved request should at least have 'content','content-type','sender','content-len','byteorder' as the keys
        """

        self._recv_data_from_server(2)
        len_header = struct.unpack('>H',self._recvd_msg)[0]
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg)
        self._recv_data_from_server(header['content-len'])
        msg = {
                'content' : self._recvd_msg,
                'content-type' : header['content-type'],
                'sender' : header['sender']
                }
        if msg['content-type'] == 'text':
            msg['content'] = msg['content'].decode(ENCODING_USED)
        return msg

    def _sendmsg(self):
        """ This function sends the message to the server
        """

        ####################################################################
        # Left to check the availability of uid and other minor edge cases #
        ####################################################################
        header = {
                'byteorder' : sys.byteorder() ,
                'request' : 'get-key' ,
                'recvr-username' : self.request['username'] ,
                'content-len' : 0
                }
        header = self._json_encode(header)
        protoheader = struct.pack('>H',len(header))
        self._data_to_send = protoheader + header
        self._send_data_to_server()

        self._recv_data_from_server(2)
        len_header = struct.unpack('>H',self._recvd_msg)
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg)
        recvr_key = header['key']

        #send the message
        msg = self._encrypt(self.request_content['message-content'],recvr_key)
        header = {
                'byteorder' : sys.byteorder(),
                'request' : 'send-msg',
                'content-type' : self.request_content['content-type'],
                'rcvr-uid' : self.request_content['content_type'],
                'content-len' : len(msg)
                }
        header = self._json_encode(header)
        protoheader = struct.pack('>H',len(header))
        self._data_to_send = protoheader + header + msg
        self._send_data_to_server()

    def _create_group_key(self):
        """ Function to get the Private key of group to use it to encrypt the messages being sent in groups

        :return: private key
        :rtype: str
        """
        key = '0'*16
        return key

    def _create_grp(self):
        """ Function to send a request to create a group

        """

        group_name = self.request_content
        group_private_key = self._create_group_key()
        global user_public_key
        encryption_key = user_public_key
        group_key = self._encrypt(group_private_key,encryption_key)
        header = {
                'guid' : group_name,
                'content-len' : 0,
                'group-key' : group_key
                }
        hdr = self._json_encode(header)
        self._data_to_send = struct.pack('>H',len(hdr)) + hdr
        self._send_data_to_server()
        self._recv_data_from_server(2)
        return struct.unpack('>H',self._recvd_msg)[0]

    def processTask(self):
        """ Processes the task to do

        :return: Returns int to represent result of the process. The details of return values are given in the corresponding functions handling the actions.
        :rtype: int
        """
        if self.task == 'login':
            return self._login()
        if self.task == 'signupuid':
            return self._signupuid()
        if self.task == 'signuppass':
            return self._signuppass()
        if self.task == "keyex":
            return self._keyex()
        if self.task == 'recv_msg':
            return self._recvmsg()
        if self.task == 'send_msg':
            return self._sendmsg()
        if self.task == 'create-grp':
            return self._create_grp()
