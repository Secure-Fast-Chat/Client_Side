import json
import struct
import sys

ENCODING_USED = "utf-8"
class Message:
    """This is the class to handle Encryption of messages. The format in which the message is sent to server is determined in this class

    :param PROTOHEADER_LENGTH: Stores the length of the "protoheader"
    :type PROTOHEADER_LENGTH: int
    """
    PROTOHEADER_LENGTH = 2

    def __init__(self,conn_socket,task,request):
        """Constructor Object

        """
        self.task = task
        self.socket = conn_socket
        self.request_content = request
        self._data_to_send = b''
        self._encoding = ENCODING_USED

    def _send_data_to_server(self):
        left_message = self._data_to_send
        while left_message:
            bytes_sent = self.conn_socket.send(left_message)
            left_message = left_message[bytes_sent:]
        return

    def _recv_data_from_server(self,size):
        self._recvd_msg = b''
        msg_length_left = size
        while True:
            self._recvd_msg += self.socket.recv(msg_length_left)
            msg_length_left = size - len(self._recvd_msg)
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

    def processTask(self):
        if self.task == 'login':
            return self._login()
