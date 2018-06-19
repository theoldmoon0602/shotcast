TCPORT = 8888
UDPORT = 8889

def screenshot():
    import Xlib
    import Xlib.display
    import subprocess

    disp = Xlib.display.Display()
    root = disp.screen().root

    id = root.get_full_property(disp.intern_atom("_NET_ACTIVE_WINDOW"), Xlib.X.AnyPropertyType).value[0]
    r = subprocess.run(['import', '-window', str(id), "/tmp/shot.png"])
    if r.returncode != 0:
        raise Exception("Failed to capture window") 

    return open("/tmp/shot.png", "rb").read()

def broadcastaddrs():
    import netifaces
    from netifaces import AF_INET
    addrs = []
    for iface in netifaces.interfaces():
        ipv4 = netifaces.ifaddresses(iface).get(AF_INET)
        if ipv4:
            baddr = ipv4[0].get('broadcast')
            if baddr:
                addrs.append(baddr)
    return addrs

img = screenshot()


import socket
import asyncio

class Server(asyncio.DatagramProtocol):
    def __init__(self, data):
        self.data = data

    def datagram_received(self, data, addr):
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.connect((addr[0], TCPORT))
        tcp.send(self.data)


ev_loop = asyncio.get_event_loop()
factory = ev_loop.create_datagram_endpoint(lambda: Server(img), local_addr=("0.0.0.0", UDPORT))
server = ev_loop.run_until_complete(factory)
ev_loop.call_later(60, lambda: ev_loop.stop())
ev_loop.run_forever()

