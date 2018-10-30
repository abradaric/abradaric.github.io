### [about me](https://abradaric.me)   |   [projects](./projects.html) | [R0A0](./r0a0.html)   |   raspberry pi essentials
* * *
There are soo many good tutorials about installing Raspbian (Rapberry Pi operating system) so I won't bother rewriting stuff in every single detail. Official _"easy way"_ is using [NOOBS](https://www.raspberrypi.org/documentation/installation/noobs.md). If you want that, just follow directions on the link. In my humble opinion [this method](https://www.raspberrypi.org/documentation/installation/installing-images/README.md) is not so hard that it should be labeled _"for advanced users only"_.

Basically what you do is, you download a tool called [Etcher](https://etcher.io/). Then you download a [raspbian image](https://www.raspberrypi.org/downloads/raspbian/). I recommend the _lite_ version since we won't need anything from full version with desktop.
Burn the downloaded image on the sd card using Etcher. The tool is so simple, you can't mess it up even if you try. If you can read all this and understand it, it means you understand English. You will understand Etcher too.

I mean, how hard can it be?

![Branching](https://upload.wikimedia.org/wikipedia/commons/8/88/Etcher-gif.gif)

Generally, we will connect to Raspberry Pi using [SSH](https://www.raspberrypi.org/documentation/remote-access/ssh/README.md). On that link, you will read about headless config, among other useful things. It mentions putting empty _ssh_ file in _boot_ partition for headless config, which means you don't have to connect it to monitor and keyboard, not even once... But it doesn't mention configuring *wpa_supplicant* (file containing network information). Anyhow, if you want to go that way, make wpa_supplicant.conf file in _boot_ directory too, like the _ssh_ file. Inside, add:
```
interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
    ssid="name of network"
    psk="password"
    }
```
You can add multiple networks, your home network, your _smartphone-as-a-router_ network.. Anyway, your Pi will automatically connect to available network and then you can simply SSH into it, like this:
```
ssh pi@its_ip_address
```
Read [here](https://www.raspberrypi.org/documentation/remote-access/ip-address.md) about finding out Pi's IP address. _Nmap_ is very simple to use.

In case you didn't bother with adding _ssh_ and *wpa_supplicant.conf* files to the _boot_ partition, that's ok. It just means that you'll have to _at least once_ connect some cables to the Pi. If that's what you want to do, not a big deal.. Also, some people report problems with headless approach. If _ssh_ somehow doesn't work for you, do it all manually.

Connect keyboard to USB, monitor to HDMI, and power to.. power. Login with username _pi_, password _raspberry_. Type:
```
sudo raspi-config
```
Here is some more [info](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) about raspi-config tool. As I said, I won't write about what is already written about, properly, a lot. First, enable SSH. Enable camera, expand filesystem, change user password, do whatever you want.

Edit networks config file. Type:
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
Add same network info like above. Now power it off, with
```
sudo systemctl poweroff
```
NO, you don't just pull the power cable out! First type that, and when the yellow light stops flashing, pull the power cable out. Disconnect HDMI and USB (keyboard). Power it back on by connecting power cable again, and ssh into it.

Don't forget to do a system update!
```
sudo apt update && sudo apt upgrade
```
