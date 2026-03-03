# Source - https://stackoverflow.com/a/64067297
# Posted by Mario Camilleri, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-02, License - CC BY-SA 4.0

import socket
from time import sleep

def main():
    interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
    allips = [ip[-1][0] for ip in interfaces]

    # only broadcast on local area network
    LANip = None
    for ip in allips:
        if ip.split('.')[2] in ('0', '1'):
            LANip = ip

    msg = b'TCP Server 0.2.2'
    while True:
        #for ip in allips:
        print(f'sending on {LANip}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((LANip,0))
        sock.sendto(msg, ("255.255.255.255", 1995))
        sock.close()

        sleep(2)


main()
