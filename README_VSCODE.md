# Detailed Installation Guide
This guide explains the different steps to follow in order to be able to debug Wearable-Software project with VSCode. It also explains how to quickly run the code without VSCode.

## Purposes
VScode is mainly used for the development of the project as its main purpose here is to facilitate debugging and not simply run the code. On the other hand, being able to run the project in only a few steps is also important for potential users. This guide will show you how to do both.

## Versions
This guide allows to debug or run Wearable-Software project on the 10.3 version of the Beagle Bone Green Wireless. All code (on board and on computer) is interpretable with Python3. We still use a depreciated [Adafruit_Python_GPIO](https://github.com/adafruit/Adafruit_Python_GPIO) library. The new library is [Adafruit_Blinka](https://github.com/adafruit/Adafruit_Blinka). 

## Guide Options
*The guide is based on ssh communication through WiFi (change accordingly for USB)*
- If your board is not configured and you want to start using VSCode, start from the beginning.
- If your board is not configured and you want to run the code fast, start from the beginning and finish with this [step](#fast).
- If your board is already configured and you want to start using VSCode, start [here](#vscode).
- If your board is already configured and you want to run the code fast, proceed to this [step](#fast) only.

## Prerequisites
- Beagle Bone Green Wireless (BBGW)
- WiFi connection
- SD card 
- VSCode and Python3

## Guide
### Firmware on Board

- Download a 10.3 version **flasher** image for BBGW [here](https://beagleboard.org/latest-images). Last one used was `AM3358 Debian 10.3 2020-04-06 4GB eMMC IoT Flasher` image.
- Burn the image on the SD card using [balenaEtcher](https://www.balena.io/etcher/) or other.
- Introduce the SD card in the board while it is off. 
- Turn the board on to flash the SD card to the eMMC and wait until the 4 leds are either turned on or off (5-15 min).
- Turn the board off, remove the SD card and turn the board on.

*You can also boot the board directly from the SD card. More information [here](http://beagleboard.org/getting-started#update).*

### SSH WiFi Access
- Wait until the board's network (BeagleBone-XXXX) appears in the detected networks list of your machine and select it.
- Open a CLI on your computer and type `ssh debian@192.168.8.1`.

*You might get the following warning: "Remote host identification has changed". In this case, find the known_host file on your computer (usually in ~/.ssh folder) and remove “192.168.7.2 ecdsa-sha2-nistp256” or equivalent so that only keys are left.*

- Type `yes` when asked “Are you sure you want to continue connecting?”.
- Type the built-in password of the board `temppwd`.

*You can also have ssh communication through USB. More information [here](http://beagleboard.org/getting-started#update).*

At this point, you should get to the CLI of the board. 

### Connect Board to WiFi/Hotspot
- Type the following commands in the board's CLI: `sudo connmanctl`, enter `temppwd` if necessary, `enable wifi`, `services`. 
- Copy the WiFi key of the WiFi that you want to connect to (example of key: wifi_xxxxxxxxxx_managed_psk).
- Type `agent on` and `connect wifi_xxxxxxxxxx_managed_psk` where you replace the WiFi key with your own key. Enter the WiFi password.
- Type `exit` to quit the WiFi manager and close the ssh connection (Ctrl C).

*More information [here](https://www.digikey.com/en/maker/blogs/2017/how-to-setup-wifi-on-the-beaglebone-black-wireless)*

At this point, your board should be connected to WiFi. The board should have memorized the WiFi for next time.

### Code and Libraries on Board
- Open a CLI on the board and type `cd ~` and `git clone https://github.com/medioman22/Wearable-Software.git` to clone the project's repository.
- Switch branch if necessary by typing `git checkout <branch>`.
- Type `sudo ~/Wearable-Software/Firmware/src/./cmds` to update and download libraries.

Your board is now ready to go.

### Code on Computer
- Clone the repository on your computer with `git clone https://github.com/medioman22/Wearable-Software.git`.

### Fast run - No debugging <a id='fast'></a>
Skip this part if you want to use VSCode.
- Open `Wearable-Software/Interface/src` folder on your computer and run `main_FastConnection.py`.
- Connect to the board directly with the user interface.

### VSCode <a id='vscode'></a>
- Open VSCode and click on the ssh green tab in the bottom left corner
- Click on `connect to Host` and then `Add New SSH Host`. Type in the ssh command `ssh debian@192.168.8.1`. 
- Select SSH configuration file (usually the first one). VSCode will automatically generate the configuration file and save host information if there is no existant known configuration file.
- Open ssh tab again and connect to the added host (make sure that your computer is connected to the WiFi of the board and that the board is connected to internet).
- Enter the board's password `temppwd`

*More information [here](https://code.visualstudio.com/docs/remote/ssh#_getting-started)*

*The ssh connection might fail if you are going too fast in the procedure. In this case, try to connect again*

You should now be connected to the board.

### Key Based Authentication (optional)
This part is for macOS/Linux machines only. Please refer to this [link](https://code.visualstudio.com/docs/remote/troubleshooting#_enabling-alternate-ssh-authentication-methods) for Windows machines.
- Generate a dedicated public key for remote ssh on your **local** terminal with `ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa-remote-ssh`. You do not need to enter a passphrase.
- Copy the key to the board with `ssh-copy-id -i ~/.ssh/id_rsa-remote-ssh.pub debian@192.168.8.1`. The board will automatically put the key in a `authorized_keys` file located in `~/.ssh` folder on the board.
- Add `IdentityFile ~/.ssh/id_rsa-remote-ssh` to your ssh configuration file on VSCode.

*More information [here](https://code.visualstudio.com/docs/remote/troubleshooting#_enabling-alternate-ssh-authentication-methods)*

At this point you should not need to enter a password each time you connect with VSCode and only you can access the board.

### Run with VSCode
- Open `Wearable-Software/Interface/src` folder on your computer with VSCode. 
- Connect to the board with the ssh tab (this will automatically open a new window) and open `Wearable-Software/Firmware/src` folder.
- In the firmware window (the board), run `Main.py`.

*If it is not done automatically, you might need to install microsoft python extension on the board with VSCode to be able to select an interpreter (select Python3)*

- In the interface window (your computer), run `main.py`. The user interface should show up.
- Press connect on the user interface.

*A video demo is available*


