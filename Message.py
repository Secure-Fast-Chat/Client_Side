import json
import datetime
import nacl
import struct
import sys
import hashlib
# import app
from nacl.public import Box, PublicKey, PrivateKey
from nacl.secret import SecretBox
from nacl.encoding import Base64Encoder
PROTOHEADER_LENGTH = 2 # to store length of protoheader
ENCODING_USED = "utf-8" # to store the encoding used
                        # The program uses universal encoding
e2ePrivateKey = None # User Private Key

GROUP_KEYS = {}
USER_PUBLIC_KEYS = {}

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
    :param box: Server Public Key and User Private Key
    :type box: nacl.public.Box
    """

    def __init__(self,conn_socket,task,request, box):
        """Constructor Object

        :param conn_socket: Socket which has a connection with server
        :type conn_socket: socket.socket
        :param task: Task to do. It can have values: login, signup, send_message
        :type task: str
        :param request: Content to send to server
        :type request: str
        :param box: Server Public Key and User Private Key
        :type box: nacl.public.Box
        """
        self.task = task
        self.socket = conn_socket
        self.request_content = request
        self._data_to_send = b''
        self.box = box

    def _send_data_to_server(self):
        """ Function to send the string to the server. It sends content of _send_data_to_server to the server

        """
        left_message = self._data_to_send
        while left_message:
            bytes_sent = self.socket.send(left_message)
            left_message = left_message[bytes_sent:]
        return

    def _recv_data_from_server(self,size,encrypted=True):
        """ Function to recv data from server. Stores the bytes recieved in a variable named _recvd_msg.

        :param size: Length of content to recieve from server
        :type size: int
        :param encrypted: (optional, True) Is the information being recieved encrypted
        :type encrypted: bool
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
        :rtype: bytes
        """

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

    def _encrypt_server(self, data):
        """Encrypts the data

        :param data: the data to encrypt
        :type data: Any
        :return: Encrypted data
        :rtype: bytes
        """
        return self.box.encrypt(data)

    def _hash_password(self,passwd):
        """Function to salt and hash the password before sending to server

        :param passwd: Password to be hashed
        :type passwd: str
        :return: Transformed Password
        :rtype: str
        """

        global ENCODING_USED
        passwd = passwd.encode(ENCODING_USED)
        return hashlib.sha256(passwd).hexdigest()
        
    def _encryptE2E(self,msg, receiverPubkey: nacl.public.PublicKey)->bytes:
        """ Encrypt the message to send to reciever

        :param msg: Message to encrypt
        :type msg: bytes
        :param receiverPubkey: Public Key of the other user
        :type receiverPubkey: nacl.public.PublicKey
        :return: Message encrypted using receiver key
        :rtype: bytes
        """

        global e2ePrivateKey
        global ENCODING_USED
        box = Box(e2ePrivateKey, receiverPubkey)
        encrypted_msg = box.encrypt(msg,encoder=Base64Encoder)
        return encrypted_msg
    
    def _decrypt(self,msg, senderPubKey: PublicKey)->bytes:
        """ Function to decrypt the content accessible to users only

        :param msg: Content to decrypt
        :type msg: bytes
        :param key: Key to use for decryption
        :type key: str
        :return: Decrypted Message
        :rtype: bytes
        """

        box = Box(e2ePrivateKey, senderPubKey)
        msg = box.decrypt(msg,encoder=Base64Encoder)
        return msg

    def _prepare_request_to_send(self,json_header,content = b'',encrypt_content = True,encrypt_header = True):
        """ Function to prepare message of form protoheader + header + content and puts it in _data_to_send

        :param json_header: header with uncommon keys (Common keys include content-length,byteorder)
        :type json_header: dict
        :param content: Content of the request
        :type content: bytes
        :param encrypt_content: Is content to be encrypted for server to client interaction
        :type encrypt_content: bool
        :param encrypt_header: Is header to be encrypted for server to client interaction
        :type encrypt_header: bool
        """

        if encrypt_content and content != b'':
            content = self._encrypt_server(content)
        json_header['byteorder'] = sys.byteorder
        json_header['content-encoding'] = ENCODING_USED
        json_header['content-length'] = len(content)
        encoded_json_header = self._json_encode(json_header)
        if encrypt_header:
            encoded_json_header = self._encrypt_server(encoded_json_header)
        protoheader = struct.pack(">H",len(encoded_json_header))
        self._data_to_send = protoheader + encoded_json_header + content

    def _create_login_request(self):
        """ Prepares login request and stores in self._data_to_send. The jsonheader has the following keys: |
        byteorder, request, content-encoding, username, password. The value for request is 'login' |
        """

        global ENCODING_USED
        jsonheader = {
            "request" : 'login',
            "username" :self.request_content['userid'],
            "password": self._hash_password(self.request_content['password']), 
        }
        self._prepare_request_to_send(jsonheader)

    def _create_signuppass_request(self):
        """ The jsonheader has the following keys: |
        byteorder, request, content-length, content-encoding. The value for request is 'signuppass' |
        The content has encoded password and e2e public Key

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

        :return: Message to send to server directly for signup request
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

        self._create_login_request()
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
        if ("availability" not in header.keys()):
            return 2
        if header['availability'] == 0:
            return 0
        else:
            return 1

    def _create_group_key(self):
        """ Function to get the Private key of group to use it to encrypt the messages being sent in groups

        :return: private key
        :rtype: str
        """
        key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

        return key

    def _keyex(self):
        """ Send public key to server for encryption of server->client interaction

        """

        global ENCODING_USED
        publickey = self.request_content['key']
        jsonheader = {
            "request" : 'keyex',
            "key": publickey,
        }
        self._prepare_request_to_send(jsonheader,encrypt_header=False)
        self._send_data_to_server()
 
    def _recvmsg(self):
        """ Recieves the information from server. It interprets this as a message from some user and returns the message recieved. The header of recieved request should at least have 'content','content-type','sender','content-length','byteorder','sender_e2e_public_key' as the keys

        :return: The dictionary containing details of message.
        :rtype: dict
        """

        self._recv_data_from_server(2, False)
        len_header = struct.unpack('>H',self._recvd_msg)[0]
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg)
        self._recv_data_from_server(header['content-length'])
        msg_content = self._recvd_msg
        if header['sender-type'] == "user":
            senderKey = PublicKey(header["sender_e2e_public_key"], encoder=Base64Encoder)
            msg_content = self._decrypt(msg_content, senderKey)
        else:
            groupCreatorsPubKey = PublicKey(header['creatorPubKey'], encoder=Base64Encoder)
            box = Box(e2ePrivateKey, groupCreatorsPubKey)
            groupKey = box.decrypt(header['group-key'], encoder=Base64Encoder) #Send the key after base64 encoding
            box = nacl.secret.SecretBox(groupKey)
            msg_content = box.decrypt(msg_content,encoder=Base64Encoder)
        msg = {
                'content' : msg_content,
                'content-type' : header['content-type'],
                'sender' : header['sender'] ,
                'timestamp' : datetime.datetime.fromtimestamp(header['timestamp'])
                }
        if msg['content-type'] == 'text':
            msg['content'] = msg['content'].decode(ENCODING_USED)
        # self._data_to_send = struct.pack('>H',0)
        # self._send_data_to_server()
        return msg

    def _get_user_public_key(self,uid):
        """ Function to get public key of a user

        :param uid: uid of user
        :type uid: str
        :return: key of user if found, None otherwise
        :rtype: nacl.public.PublicKey
        """
        if uid in USER_PUBLIC_KEYS.keys():
            return USER_PUBLIC_KEYS[uid]
        header = {
                'request' : 'get-key' ,
                'recvr-username' : uid,
                }
        self._prepare_request_to_send(header)
        self._send_data_to_server()

        self._recv_data_from_server(2, False)
        len_header = struct.unpack('>H',self._recvd_msg)[0]
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg)
        if not 'key' in header.keys():
            return None
        if not header['key']:
            return None
        recvr_key = header['key']
        USER_PUBLIC_KEYS[uid] = PublicKey(recvr_key,encoder=Base64Encoder)
        return USER_PUBLIC_KEYS[uid]

    ####################################################################
    # Left to check the availability of uid and other minor edge cases #
    ####################################################################
    def _sendmsg(self):
        """ This function sends the message to the server

        :return: Exit status, 0 for success, 1 if no such uid
        :rtype: int
        """

        recvr_key = self._get_user_public_key(self.request_content['recvr-username'])
        if not recvr_key:
            return 1
        #send the message
        msg = self._encryptE2E(self.request_content['message-content'],recvr_key)
        # msg = self._encrypt_server(msg) #Encrypt it a second time so that an eavesdropper cannot see whom we sent the message to (otherwise they can see where this encrypted message went if they had access to every connection of the server)
        header = {
                'request' : 'send-msg',
                'content-type' : self.request_content['content-type'],
                'rcvr-uid' : self.request_content['recvr-username'],
                }
        self._prepare_request_to_send(header,content=msg,encrypt_content = False)
        self._send_data_to_server()
        return 0

    def _create_grp(self):
        """ Function to send a request to create a group

        :return: exit status. 0 for success, 1 if group name already exists
        :rtype: int
        """

        group_name = self.request_content
        group_private_key = self._create_group_key()
        encryption_key = e2ePrivateKey #Group creator's (my) private key
        group_key = self._encryptE2E(group_private_key,encryption_key.public_key).decode() #encrypt using my private key and also my public key. Only I can ever decrypt this
        header = {
                'guid' : group_name,
                'group-key' : group_key,
                'request': 'create-grp',
                }
        self._prepare_request_to_send(header)
        self._send_data_to_server()
        self._recv_data_from_server(2, False)
        return struct.unpack('>H',self._recvd_msg)[0]

    def _get_group_key(self, guid:str):
        """Function to get the encrypted group private key from server.

        :param guid: Group Name
        :type guid: str
        :return: This function returns key if found, else None if User not in group
        :rtype: str or None
        """

        if guid in GROUP_KEYS.keys():
            return GROUP_KEYS[guid]
        header = {
                'request' : 'grp-key',
                'group-name': guid,
                }
        self._prepare_request_to_send(header)
        self._send_data_to_server()
        self._recv_data_from_server(2, False)
        len_header, = struct.unpack('>H',self._recvd_msg)
        self._recv_data_from_server(len_header)
        header = self._json_decode(self._recvd_msg)
        if header['group-key']:
            groupCreatorsPubKey = PublicKey(header['creatorPubKey'], encoder=Base64Encoder)
            box = Box(e2ePrivateKey, groupCreatorsPubKey)
            key = box.decrypt(header['group-key'], encoder=Base64Encoder) #Send the key after base64 encoding
            GROUP_KEYS[guid] = key
            return key
        return None

    def _remove_member_from_group(self):
        """ Function to remove Member in a group. Will be accepted by the server only if I am the owner of the group

        :return: Exit status to tell the status
        :rtype: int
        """

        
        header = {
                'request' : 'remove-mem',
                'guid' : self.request_content['guid'],
                'uid' : self.request_content['uid'],
                }
        self._prepare_request_to_send(header)
        self._send_data_to_server()
        self._recv_data_from_server(2, False) # 0 for success and 2 if not admin
        return struct.unpack('>H',self._recvd_msg)[0]

    def _add_member_in_group(self):
        """ Function to add Member in a group. Will be accepted by the server only if I am the owner of the group

        :return: Exit status to tell the status
        :rtype: int
        """

        groupKey = self._get_group_key(self.request_content['guid'])
        if not groupKey:
            return 1
        userPublicKey = self._get_user_public_key(self.request_content['new-uid'])
        if not userPublicKey:
            return 3

        # Encrypt the new users group private key using their public key and the group creators private key
        box = Box(e2ePrivateKey, userPublicKey)
        newUserGroupKey = box.encrypt(groupKey,encoder=Base64Encoder).decode()
        header = {
                'request' : 'add-mem',
                'guid' : self.request_content['guid'],
                'new-uid' : self.request_content['new-uid'],
                'user-grp-key' : newUserGroupKey,
                }
        self._prepare_request_to_send(header)
        self._send_data_to_server()
        self._recv_data_from_server(2, False) # 0 for success and 2 if not admin
        return struct.unpack('>H',self._recvd_msg)[0]

    def _send_message_in_group(self):
        """Function to send message in a group

        :return: 0 for success, 1 for failure, 2 if not in group
        :rtype: int
        """

        groupPrivateKey = self._get_group_key(self.request_content['guid'])
        if not groupPrivateKey:
            return 2
        # print(groupPrivateKey)
        box = nacl.secret.SecretBox(groupPrivateKey)

        content = box.encrypt(self.request_content['message-content'], encoder=Base64Encoder)
        header = {
                'request': 'send-group-message',
                'content-type' : self.request_content['content-type'], 
                'guid' : self.request_content['guid']
                }
        self._prepare_request_to_send(header,content=content)
        self._send_data_to_server()
        self._recv_data_from_server(2, False)
        return struct.unpack('>H',self._recvd_msg)[0]
    
    def _get_server_from_lb(self):
        """Function to get Server's host, port from load balancer
        
        :return: tuple of host, port of the server
        :rtype: (str, int)"""
        self._recv_data_from_server(2,encrypted=False)
        header_len = struct.unpack(">H",self._recvd_msg)[0]
        self._recv_data_from_server(header_len,encrypted = False)
        header = self._json_decode(self._recvd_msg)
        return (header['host'],header['port'])
        
    def _leave_grp(self):
        """ This function is used to send request to leave a group

        :return: Exit status, 0 for success
        :rtype: int
        """

        json_header={
                'request' : 'leave-grp',
                'guid' : self.request_content
                }
        self._prepare_request_to_send(json_header,encrypt_content = False)
        self._send_data_to_server()
        self._recv_data_from_server(2,encrypted = False)
        return struct.unpack(">H",self._recvd_msg)[0]

    def _del_individual_message(self):
        """ This function is used to send request to delete a message sent to an individual

        :return: Exit status, 0 for success, 1 for failure
        :rtype: int
        """
        recvr_key = self._get_user_public_key(self.request_content['recvr-username'])
        if not recvr_key:
            return 1
        #send the message
        msg = self._encryptE2E(self.request_content['message-content'],recvr_key)
        # msg = self._encrypt_server(msg) #Encrypt it a second time so that an eavesdropper cannot see whom we sent the message to (otherwise they can see where this encrypted message went if they had access to every connection of the server)
        header = {
                'request' : 'del-msg',
                'rcvr-uid' : self.request_content['recvr-username'],
                }
        self._prepare_request_to_send(header,content=msg,encrypt_content = False)
        self._send_data_to_server()
        return 0

    def _del_group_message(self):
        """ This function is used to send request to delete a message sent to a group

        :return: Exit status, 0 for success, 1 for failure, 2 if invalid guid
        :rtype: int
        """
        groupPrivateKey = self._get_group_key(self.request_content['guid'])
        if not groupPrivateKey:
            return 2
        # print(groupPrivateKey)
        box = nacl.secret.SecretBox(groupPrivateKey)

        content = box.encrypt(self.request_content['message-content'], encoder=Base64Encoder)
        header = {
                'request': 'del-group-message',
                'guid' : self.request_content['guid']
                }
        self._prepare_request_to_send(header,content=content)
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
        if self.task == 'get-server':
            return self._get_server_from_lb()
        if self.task == 'leave-grp':
            return self._leave_grp()
        if self.task == 'remove-mem':
            return self._remove_member_from_group()
        if self.task == 'del-message':
            return self._del_individual_message()
        if self.task == 'del-group-message':
            return self._del_group_message()
        print(f"Unknown request {self.task}")
