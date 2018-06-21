#!/usr/bin/env python

"""Shotcast server

Usage: [-h] [-t | --tcp-port 8888] [-u | --udp-port 8889] [--timeout 60]

Options:
    -h --help               Show this help.
    -t --tcp-port <port>    Shotcast client listening port number [default: 8888]
    -u --udp-port <port>    Shotcast server(this) listening port number [default: 8889]
    --timeout <seconds>         Server listening seconds [default: 60]
"""

TCPORT = 8888
UDPORT = 8889
TIMEOUT = 60

def screenshot():
    import Xlib
    import Xlib.display
    import subprocess
    import tempfile

    disp = Xlib.display.Display()
    root = disp.screen().root

    id = root.get_full_property(disp.intern_atom("_NET_ACTIVE_WINDOW"), Xlib.X.AnyPropertyType).value[0]

    _, f = tempfile.mkstemp(dir="/tmp", suffix=".png")

    r = subprocess.run(['import', '-silent', '-window', str(id), f])
    if r.returncode != 0:
        raise Exception("Failed to capture window") 

    return open(f, "rb").read()

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

def main():
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
    ev_loop.call_later(TIMEOUT, lambda: ev_loop.stop())
    ev_loop.run_forever()


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)

    TCPORT = int(args['--tcp-port'][0])
    UDPORT = int(args['--udp-port'][0])
    TIMEOUT = int(args['--timeout'][0])

    main()
