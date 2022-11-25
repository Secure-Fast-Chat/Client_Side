# Client Side

## Usage Instructions

After login, one can use the following commands for using the app.

### Commands for messages

- `\send <username> <message>`
	
	Use this command to send `message` to `username`.
- `\sendfile <username> <file>`

	Use this command to send `file` to `username` where `file` is relative address of file.

### Group Related Commands

- `\mkgrp <grpname>`
	
	This command is used to create a group with grpname `grpname`. The creator of group is admin of group by default.
- `\addmem <grpname> <username>`
	
	Use this command to add member with `username` in group `grpname`.
- `\sendgrp <grpname> <messsage>`
	
	Use this command to send message in group.
- `\sendfilegrp <grpname> <file>`
	
	Use this command to send file in group.
- `\rmmem <grpname> <username>`

	Use this command to remove a group member
- `\rmgrp <grpname>`

	Use this command to leave a group

### Other Commands

- `\logout`

	Use this command to logout 

### Other Information

The latest message recieved is displayed 3 lines below the cursor.
Also, the result/exit status of last command run is displayed 2 lines above the cursor.
All the files recieved are saved in the current directory.
The filename with complete path to file is printed as a file recieved msg.
All the messages recieved are put in a file named `SecureFastChatMessages.txt` in the home directory of user.
This file is updated every time you recv message on app.

## Security Information

All the messages sent are end-to-end encrypted. 
This uses PyNaCl for encryption. 

#### For Authentication

The hash of password is sent through a secure channel to the server. Database stores this hash of password.
It checks if hash of password matches.

#### For Direct Messages

The private key for the user is derived from the string given by uid+password.
Corresponding public key is sent to server at time of signup to store in database.
When message send request is recieved, user gets the public key of reciever. Then the encrypted message is sent to reciever.
The reciever decrypts it using it's private key derived from his uid and password.

#### For Group Messages

For every group, a random key is generated to use as group private key at time of making group. This key is stored in database by encrypting it using the public key of group member.
This key can be decrypted by group members only.
For sending group messages, the messages are encrypted using this group private key.
