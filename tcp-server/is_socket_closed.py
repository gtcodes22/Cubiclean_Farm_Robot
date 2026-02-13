# from: https://stackoverflow.com/questions/48024720/python-how-to-check-if-socket-is-still-connected
# written by Michael Petrov (https://stackoverflow.com/users/552710/michael-petrov)

import logging
import socket
from select import select

logger = logging.getLogger(__name__)

def is_socket_closed(sock: socket.socket) -> bool:
    try:
        # this will try to read bytes without blocking and also without
        # removing them from buffer (peek only) (only works on linux sockets)
        #data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        
        # version for windows (TODO: determine host OS and choose check
        # accordingly
        # from: https://stackoverflow.com/questions/54071217/attributeerror-module-socket-has-no-attribute-msg-dontwait
        # put socket into non-blocking mode
        #sock.settimeout(0)
        #sock.setblocking(False)
        data = sock.recv(16, socket.MSG_PEEK)
        
        if len(data) == 0:
            return True
        else:
            #sock.setblocking(True)
            return False
            
        # from https://docs.python.org/3/howto/sockets.html
        # poll if the socket is ready to read, write or in error
        #canRead, canWrite, sockError = \
        #    select([sock],{sock}, {sock}, 60)
        '''
        if (sock in sockError or \
            sock not in canRead or \
            sock not in canWrite):
            print(sockError)
            print(canRead)
            print(canWrite)
            return True
        '''
        
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        logger.exception("unexpected exception when checking if a socket is closed")
        return False
    return False
