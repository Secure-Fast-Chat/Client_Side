import json
import struct
import sys
import hashlib
# import app
from nacl.public import Box, PublicKey
from nacl.encoding import Base64Encoder
PROTOHEADER_LENGTH = 2 # to store length of protoheader
ENCODING_USED = "utf-8" # to store the encoding used
                        # The program uses universal encoding
e2ePrivateKey = None # User Private Key

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

    def __init__(self,conn_socket,task,request, box):
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
        self.box = box

    def _encrypt_server(self, data):
        """Encrypts the data

        :param data: the data to encrypt
        :type data: Any
        :return: The data after encryption
        :rtype: _type_
        """
        return self.box.encrypt(data)

    def _send_data_to_server(self):
        """ Function to send the string to the server. It sends content of _send_data_to_server to the server

        """
        left_message = self._data_to_send
        while left_message:
            bytes_sent = self.socket.send(left_message)
            left_message = left_message[bytes_sent:]
        return

    def _recv_data_from_server(self,size,encrypted=True, authenticated=True):
        """ Function to recv data from server. Stores the bytes recieved in a variable named _recvd_msg.

        :param size: Length of content to recieve from server
        :type size: int
        """

        if size<20:
            encrypted=False # Since the nonce itself must be atleast 24 bits long, this should never happen
        self._recvd_msg = b''
        while len(self._recvd_msg) < size:
            self._recvd_msg += self.socket.recv(size-len(self._recvd_msg))
        if encrypted:
            self._recvd_msg = self.box.decrypt(self._recvd_msg)
        return

    def _json_encode(self, obj, encoding=ENCODING_USED):
        """Function to encode dictionary to bytes object

        :param obj: dictionary to encode
        :type obj: dict
        :param encoding: Encoding to use
        :type encoding: str
        :return: Encoded obj
        :rtype: bytes"""

        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, obj, encoding = ENCODING_USED):
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
        global ENCODING_USED
        passwd = passwd.encode(ENCODING_USED)
        return hashlib.sha256(passwd).hexdigest()
        
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

    def _encryptE2E(self,msg, receiverPubkey: PublicKey)->str:
        """ Encrypt the message to send to reciever

        :param msg: Message to encrypt
        :type msg: bytes
        :param receiverPubkey: Public Key of the other user
        :type receiverPubkey: nacl.public.PublicKey
        """
        ########################################################
        ############### Pending Implementation #################
        ########################################################
        global e2ePrivateKey
        global ENCODING_USED
        box = Box(e2ePrivateKey, receiverPubkey)
        encrypted_msg = box.encrypt(msg)
        return encrypted_msg
    
    def _decrypt(self,msg, senderPubKey: PublicKey)->str:
        """ Function to decrypt the content accessible to users only

        :param msg: Content to decrypt
        :type msg: bytes
        :param key: Key to use for decryption
        :type key: str
        """
        box = Box(e2ePrivateKey, senderPubKey)
        msg = box.encrypt(msg)
        return msg

    def _create_login_request(self):
        """ The jsonheader has the following keys: |
        byteorder, request, content-length, content-encoding. The value for request is 'loginuid' |
        The content has user id.

        :return: Message to send to server directly for login
        :rtype: bytes
        """

        global ENCODING_USED
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'login',
            "username" :self.request_content['userid'],
            "password": self._hash_password(self.request_content['password']), 
            "content-encoding" : ENCODING_USED,
        }
        encoded_json_header = self._json_encode(jsonheader,ENCODING_USED)
        encoded_json_header = self._encrypt_server(encoded_json_header)
        proto_header = struct.pack('>H',len(encoded_json_header))
        # Command to use for unpacking of proto_header: 
        # struct.unpack('>H',proto_header)[0]
        return proto_header + encoded_json_header

    def _create_signuppass_request(self):
        """ The jsonheader has the following keys: |
        byteorder, request, content-length, content-encoding. The value for request is 'signuppass' |
        The content has encoded password

        :return: Message to send to server directly for login
        :rtype: bytes
        """

        global ENCODING_USED
        # password = self._hash_password(self.request_content['password'])
        # content = bytes(self._encode(self.request_content["password"]), encoding=ENCODING_USED) 
        content={
            "password": self._hash_password(self.request_content["password"]),
            "e2eKey": self.request_content["e2eKey"]
        }
        content = self._json_encode(content,ENCODING_USED)
        content =self._encrypt_server(content) 
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'signuppass',
            'content-length' : len(content),
            "content-encoding" : ENCODING_USED,
        }
        encoded_json_header = self._json_encode(jsonheader,ENCODING_USED)
        encoded_json_header = self._encrypt_server(encoded_json_header)
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
        content = self._encrypt_server(content)
        jsonheader = {
            "byteorder": sys.byteorder,
            "request" : 'signupuid',
            'content-length' : len(content),
            "content-encoding" : ENCODING_USED,
        }
        encoded_json_header = self._json_encode(jsonheader,ENCODING_USED)
        encoded_json_header = self._encrypt_server(encoded_json_header)
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

        self._data_to_send = self._create_login_request()
        self._send_data_to_server()
        # Recieve login result from server
        self._recv_data_from_server(2, False)
        response = struct.unpack('>H',self._recvd_msg)[0]
        return response

    def _signuppass(self):
        """ Function to save account password at server
        The function expects to recieve a response of size 2 from server which gives 0 if username already taken and 1 for success

        :return: Response from server converted to int
        :rtype: int
        """

        self._data_to_send = self._create_signuppass_request()
        self._send_data_to_server()
        # Recieve login result from server
        self._recv_data_from_server(2, False)
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
        self._recv_data_from_server(2, False)
        len_header = struct.unpack('>H',self._recvd_msg)[0]
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg, ENCODING_USED)
        if header['availability'] == 0:
            return 0
        else:
            return 1

    def _create_group_key(self):
        """ Function to get the Private key of group to use it to encrypt the messages being sent in groups

        :return: private key
        :rtype: bytes
        """
        key = b'0'*16
        return key

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
        """ Recieves the information from server. It interprets this as a message from some user and returns the message recieved. The header of recieved request should at least have 'content','content-type','sender','content-length','byteorder' as the keys
        """

        self._recv_data_from_server(2, False)
        len_header = struct.unpack('>H',self._recvd_msg)[0]
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg)
        self._recv_data_from_server(header['content-length'])
        msg_content = self._recvd_msg
        senderKey = PublicKey(header["sender_e2e_public_key"], encoder=Base64Encoder)
        msg_content = self._decrypt(msg_content, senderKey)
        msg = {
                'content' : msg_content,
                'content-type' : header['content-type'],
                'sender' : header['sender']
                }
        if msg['content-type'] == 'text':
            msg['content'] = msg['content'].decode(ENCODING_USED)
        return msg

    def _get_user_public_key(self,uid):
        """ Function to get public key of a user

        :param uid: uid of user
        :type uid: str
        :return: key of user if found, None otherwise
        :rtype: bytes
        """
        header = {
                'byteorder' : sys.byteorder ,
                'request' : 'get-key' ,
                'recvr-username' : uid,
                'content-length' : 0
                }
        header = self._json_encode(header)
        header = self._encrypt_server(header)
        protoheader = struct.pack('>H',len(header))
        self._data_to_send = protoheader + header
        self._send_data_to_server()

        self._recv_data_from_server(2, False)
        print(self._recvd_msg)
        len_header = struct.unpack('>H',self._recvd_msg)[0]
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg)
        if 'key' not in header.keys():
            return None
        recvr_key = header['key']
        return PublicKey(recvr_key, encoder=Base64Encoder)

    def _sendmsg(self):
        """ This function sends the message to the server
        """

        ####################################################################
        # Left to check the availability of uid and other minor edge cases #
        ####################################################################

        recvr_key = self._get_user_public_key(self.request_content['recvr-username'])
        if not recvr_key:
            return 1
        #send the message
        print(recvr_key)
        msg = self._encryptE2E(self.request_content['message-content'],recvr_key)
        msg = self._encrypt_server(msg) #Encrypt it a second time so that an eavesdropper cannot see whom we sent the message to (otherwise they can see where this encrypted message went if they had access to every connection of the server)
        header = {
                'byteorder' : sys.byteorder,
                'request' : 'send-msg',
                'content-type' : self.request_content['content-type'],
                'rcvr-uid' : self.request_content['recvr-username'],
                'content-length' : len(msg)
                }
        encoded_json_header = self._json_encode(header)
        encrypted_header = self._encrypt_server(encoded_json_header)
        protoheader = struct.pack('>H',len(encrypted_header))
        self._data_to_send = protoheader + encrypted_header + msg
        self._send_data_to_server()
        return 0

    def _create_grp(self):
        """ Function to send a request to create a group

        """

        group_name = self.request_content
        group_private_key = self._create_group_key()
        global user_public_key
        encryption_key = user_public_key
        group_key = self._encryptE2E(group_private_key,encryption_key)
        header = {
                'guid' : group_name,
                'content-length' : 0,
                'group-key' : group_key
                }
        hdr = self._json_encode(header)
        self._data_to_send = struct.pack('>H',len(hdr)) + hdr
        self._send_data_to_server()
        self._recv_data_from_server(2, False)
        return struct.unpack('>H',self._recvd_msg)[0]

    def _get_group_key(self,guid):
        """Function to get the encrypted group private key from server.

        :param guid: Group Name
        :type guid: str
        :return: This function returns key if found, else None if User not in group
        :rtype: str or None
        """

        header = {
                'request' : 'grp-key',
                'content-length' : 0,
                'byteorder' : sys.byteorder
                }
        hdr = self._json_encode(header)
        self._data_to_send = struct.pack(">H",len(hdr)) + hdr
        self._send_data_to_server()
        self._recv_data_from_server(2, False)
        len_header = struct.unpack('>H',self._recvd_msg)
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg)
        if 'group-key' in header.keys():
            return header['group-key']
        return None

    def _add_member_in_group(self):
        """ Function to add Member in a group

        :return: Exit status to tell the status
        :rtype: int
        """

        userGroupKey = self._get_group_key(self.request_content['guid'])
        if not userGroupKey:
            return 1
        global userSecret
        groupPrivateKey = self._decrypt(userGroupKey,userSecret)
        userPublicKey = self._get_user_public_key(self.request_content['new-uid'])
        if not userPublicKey:
            return 3
        newUserGroupKey = self._encryptE2E(groupPrivateKey,userPublicKey)
        header = {
                'request' : 'add-mem',
                'guid' : self.request_content['guid'],
                'new-uid' : self.request_content['new-uid'],
                'user-grp-key' : newUserGroupKey
                }
        hdr = self._json_encode(header)
        self._data_to_send = struct.pack('>H',len(hdr)) + hdr
        self._send_data_to_server()
        self._recv_data_from_server(2, False) # 0 for success and 2 if not admin
        return struct.unpack('>H',self._recvd_msg)[0]

    def _send_message_in_group(self):
        """Function to send message in a group

        :return: 0 for success, 1 for failure, 2 if not in group
        """

        userGroupKey = self._get_group_key(self.request_content['guid'])
        if not userGroupKey:
            return 2
        global userSecret
        groupPrivateKey = self._decrypt(userGroupKey,userSecret)
        content = self._encryptE2E(self.request_content['message-content'],groupPrivateKey)
        header = {
                'content-length' : len(content),
                'content-type' : self.request_content['content-type'], 
                'guid' : self.request_content['guid']
                }
        hdr = self._json_encode(header)
        self._data_to_send = struct.pack('>H',len(hdr)) + hdr + content
        self._send_data_to_server()
        self._recv_data_from_server(2, False)
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
        if self.task == 'send-message':
            return self._sendmsg()
        if self.task == 'create-grp':
            return self._create_grp()
        if self.task == 'add-mem':
            return self._add_member_in_group()
        if self.task == 'send-group-message':
            return self._send_message_in_group()
