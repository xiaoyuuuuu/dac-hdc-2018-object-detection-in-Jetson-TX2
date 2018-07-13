## this is for GPU demo with only one FPGA and one computer for computer for display
## xxu8@nd.edu
# coding:utf8

import socket
import threading
import struct
import time
import cv2
import numpy

NofClients = 1
MyIP = ""　
SENDER_ON_WIN = False

class Senders_Carame_Object:
    def __init__(self, addr_ports=[(MyIP, 3000)]):
        print 'Senders_Carame_Object init'
        print addr_ports
        self.resolution = (640, 360)
        self.img_fps = 10
        self.addr_ports = addr_ports
        self.connections = []
        for i in range(0, NofClients):
            print "setup connection " + str(i)
            self.Set_Socket(self.addr_ports[i])

    def Set_Socket(self, addr_port):
        print 'Senders_Carame_Object Set_Socket'
        self.connections.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.connections[-1].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connections[-1].bind(addr_port)
        self.connections[-1].listen(5)
        print("the process work in the port:%d" % addr_port[1])


def check_option(object, clients):
    for i in range(0, NofClients):
        info = struct.unpack('hh', clients[i].recv(4))  ## 8 or 12
        if info[0] != object.resolution[0] or info[1] != object.resolution[1]:
            print "error: check option fails, received resolution is: " + str(info[0]) + "," + str(info[1])
            return 1
        else:
            return 0


def RT_Image(object, clients):
    print 'RT_Image '
    if check_option(object, clients) == 1:
        return
    camera = cv2.VideoCapture(0)
    img_param = [int(cv2.IMWRITE_JPEG_QUALITY), object.img_fps]
    indexN = 0
    # the ll type on windows has different size as on linux.
    if SENDER_ON_WIN:
        type_model = 'ii'
    else:
        type_model = 'll'

    while 1:
        # time.sleep(0.1) ## about 10 fps              
        _, object.img = camera.read()
        indexN = indexN + 1
        object.img = cv2.resize(object.img, object.resolution)
        _, img_encode = cv2.imencode('.jpg', object.img, img_param)
        img_code = numpy.array(img_encode)
        object.img_data = img_code.tostring()
        try:
            for i in range(0, NofClients):
                # @warning: the size of ll is different in different os, so we use ii
                clients[i].send(struct.pack(type_model, len(object.img_data), indexN) + object.img_data)
            # print str(indexN) + ', size of the send img:', len(object.img_data)
            ## wait until the images are processed on FPGAs
            feedback = struct.unpack('h', clients[0].recv(2))
            if feedback[0] != 168:
                print "feedback from FPGA error, " + str(feedback)
                return
        except Exception as e:
            print(e)
            camera.release()
            return


if __name__ == '__main__':
    senders = Senders_Carame_Object([(MyIP, 3010)])
    clients = []
    for i in range(0, NofClients):
        print "connection accept with " + str(i)
        clients.append(senders.connections[i].accept()[0])
    clientThread = threading.Thread(None, target=RT_Image, args=(senders, clients,))
    clientThread.start()
