import socket
import threading

TCPORT = 8888
UDPORT = 8889

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

def imgrecv_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    server.bind(('0.0.0.0', TCPORT))
    server.listen(10)

    imgdata = None

    while True:
        sock, _ = server.accept()
        imgdata = recvall(sock)
        break

    if imgdata:
        open("/tmp/hoge.png", "wb").write(imgdata)

t = threading.Thread(target=imgrecv_server)
t.start()

for addr in ["0.0.0.0"]:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.connect((addr, UDPORT))
        client.send(b'HELLO')
    except socket.timeout:
        continue

t.join(timeout=10)
