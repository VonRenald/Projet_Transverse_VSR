import os
import sys
import time
import socketserver
import threading

import socket

from multiprocessing import Semaphore
from multiprocessing import Process

sem = None
serverC = None
serverW = None

count = 0

portW = 0 
portC = 0

try:
    portC = int(sys.argv[1])
    portW = int(sys.argv[2])
    portW2 = int(sys.argv[3])
    portW3 = int(sys.argv[4])
except:
    portC = 9080
    portW = 9090
    portW2= 9095 
    portW2= 9098 

def send_msg(msg, port, wait_answer = True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(('127.0.0.1',port))
        t1 = time.time()
        client.send(msg)
        if wait_answer:
            response = client.recv(1024)
            t2 = time.time()
            print("return in ",t2-t1,"- ",end=' ')
            print(response)
            return response
    return None

def read_int(filename, default):
    try:
        with open(filename, 'r') as file:
            return int(f.read())
    except:
        return default

def work():
    global sem
    with sem:
        print('start working', os.getpid());
        time.sleep(.5)
        print('end working', os.getpid());

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
        global count
        global server
        count += 1
        print(count)
        data = self.request.recv(1024)
        print("read - ",end=' ')
        print(data)
        if count%3 == 0:
            ret = send_msg(data,portW)
        else :
            if count%3 == 1:
                ret = send_msg(data,portW2)
            else:
                ret = send_msg(data,portW3)
        if data == b'quit':
            os._exit(0)
        else:
            self.request.sendall(ret)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def main():
    global server

    sem_init()
    
    count = 0
    
    
    


    server = ThreadedTCPServer(('0.0.0.0', portC), ThreadedTCPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print("lalala")
    server.shutdown()      
    server.socket.close()

        

if __name__ == '__main__':
    main()
