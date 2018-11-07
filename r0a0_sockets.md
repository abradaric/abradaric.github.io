* * *
### [about me](https://abradaric.me)   |   [projects](./projects.html) | [R0A0](./r0a0.html)   |   sockets (RC & visual feed)

[Sockets](https://en.wikipedia.org/wiki/Network_socket) are used in this project to transmit movement controls and visual feed between RPi and server. Read about sockets in Python more [here](https://docs.python.org/3.7/howto/sockets.html). Two protocols are used: UDP and TCP. Basically, TCP guarantees correct delivery by numbering packets and waiting for acknowledgment from the other side. If something goes wrong, packets are sent again. With UDP, if some packets get dropped, they're dropped for good.

Both protocols have found their use in this project. If we are remotely controlling robot (_WASD_ style), TCP would be problematic because of delay/lag induced by potential connection problems. Suppose we are driving and network hogs down for a second, and in the meantime we decide to change direction input. All those previously dropped packets would get resent, with consequence of robot traversing unwanted path. Here, UDP is good because only the latest input is relevant. But, if we want to do some computer vision image processing, it would be nice to have correct data. Therefore, we transport JPG images with TCP protocol.

Check out remote control [here](./r0a0_sockets_rc.html) and visual feed here: [h264](./r0a0_sockets_h264.html) and [jpeg](./r0a0_sockets_jpeg.html).
