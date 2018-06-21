"""Shotcast client

Usage: [-h] [-t | --tcp-port 8888] [-u | --udp-port 8889] [--viewer <command>]

Options:
    -h --help               Show this help.
    -t --tcp-port <port>    Shotcast client(this) listening port number [default: 8888]
    -u --udp-port <port>    Shotcast server listening port number [default: 8889]
    --viewer <command>  Received image viewer default is xdg-open in Linux
"""
import socket
import threading

TCPORT = 8888
UDPORT = 8889
VIEWER = None

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

def recvall(sock):
    SIZE = 4096
    buf = b''
    while True:
        data = sock.recv(SIZE)
        buf += data
        if len(data) < SIZE:
            break
    return buf

def imgrecv_server(server):
    import tempfile
    import subprocess

    imgdata = None

    while True:
        sock, _ = server.accept()
        imgdata = recvall(sock)
        break

    if imgdata:
        _, f = tempfile.mkstemp(dir="/tmp", suffix=".png")
        fp = open(f, "wb")
        fp.write(imgdata)
        fp.close()

        subprocess.run([VIEWER, f])

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    server.bind(('0.0.0.0', TCPORT))
    server.listen(10)

    f = lambda: imgrecv_server(server)

    t = threading.Thread(target=f)
    t.setDaemon(True)
    t.start()

    for addr in broadcastaddrs():
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            client.connect((addr, UDPORT))
            client.send(b'HELLO')
        except socket.timeout:
            continue

    t.join(timeout=10)

if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)

    TCPORT = int(args['--tcp-port'][0])
    UDPORT = int(args['--udp-port'][0])

    if args.get('--viewer'):
        VIEWER = args['--viewer']
    else:
        VIEWER = "xdg-open"

    main()
