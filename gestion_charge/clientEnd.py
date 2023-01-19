import sys
import socket
from multiprocessing import Process
import time

host = '127.0.0.1'
try:
    port = int(sys.argv[1])
except:
    port = 9090

nb_messages = 30
sleeping_time = .1

def send_msg(msg, wait_answer = True):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host,port))
        client.send(msg)
        if wait_answer:
            response = client.recv(1024)
            print(response)



send_msg(b'quit', False)
