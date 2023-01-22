import os
import sys
import time
import socketserver
import threading


from multiprocessing import Semaphore
from multiprocessing import Process

sem = None
server = None

def read_int(filename, default):
    try:
        with open(filename, 'r') as file:
            return int(f.read())
    except:
        return default

def work():
    global sem
    with sem:
        print('start working', os.getpid(),flush=True);
        time.sleep(.5)
        print('end working', os.getpid(),flush=True);

def manage_request():
    global sem
    Process(target = work, args=()).start()

def sem_init():
    global sem
    ## 1 worker per 100MB
    unit = 100*1000*1000
    nb_parallel = read_int('/sys/fs/cgroup/memory.max', 3*unit) // unit
    sem = Semaphore(value = nb_parallel)


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global server
        data = self.request.recv(1024)
        print(data)
        if data == b'quit':
            
            server.shutdown()            
            server.socket.close()
            os._exit(0)
        else:
            work()
            self.request.sendall(b'ok')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def main():
    global server
    print("run worker",flush=True)
    sem_init()

    try:
        port = int(sys.argv[1])
    except:
        port = 9090
    
    server = ThreadedTCPServer(('0.0.0.0', port), ThreadedTCPRequestHandler)
    server.socket.settimeout(1)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.shutdown()            
    server.socket.close()

if __name__ == '__main__':
    main()
