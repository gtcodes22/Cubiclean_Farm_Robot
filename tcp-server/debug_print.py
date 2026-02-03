from threading import Lock

printLock = Lock()
DEBUG = True

# enables debug messages to be printed if debug mode is on
def debugPrint(msg):
    if DEBUG:
        with printLock:
            print(msg)