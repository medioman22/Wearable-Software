# Remote SSH with VS Code

The VS Code is not compatible with debian 8.10 that is used for the firmware. However, it works fine with debian 10.3. 

## Usefull links

Follow the instruction given in the link below:

https://code.visualstudio.com/docs/remote/ssh

## Usefull info

It is suggested to creat a key for the local server(your PC) and pass it to beaglebone, and provide the informaton 
config file required for ssh connection in VS Code. 

### Creation of Key
ssh-keygen -t rsa -f ~/.ssh/name

### Passing the Public key to Board:
ssh-copy-id -i ~/.ssh/name.pub debian@address

### Testing
ssh -i ~/.ssh/name debian@address

### Setting SSH Agent
It might be needed to set the SSH agent as well.




