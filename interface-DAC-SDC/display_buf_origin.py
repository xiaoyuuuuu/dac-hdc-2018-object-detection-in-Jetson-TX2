# coding:utf8
import math
import socket
import cv2
import threading
import struct
import numpy

import time
import Queue
import procfunc_ex as procfunc

###### change your team name here
teamName = "SDU-Legend"
windowName = "DAC HDC contest team:" + teamName
# 设置每次从队列里取出的图片张数，与源码里写的多线程格式有关
BATCH_SIZE = 2

MyIP = "211.87.235.197"
SENDER_ON_WIN = False


class ImageAndIndex:
    def __init__(self, image, index):
        self.image = image
        self.index = index
        # 保存检测最后的结果，两个点的坐标
        self.detecRec = []
        self.start_time = 0
        self.end_time = 0


class process_display_Object:
    def __init__(self, addr_port_client_Img=("", 1000)):
        print 'displayImg_Connect_Object init'
        self.resolution = [640, 360]
        self.client_port_Img = addr_port_client_Img
        # 标准库里的queue线程安全
        self.q = Queue.Queue(BATCH_SIZE * 2)
        #
        self.q_list = []
        self.q_center = []

    def Socket_Connect_Client(self):
        print 'displayImg_Connect_Object   Socket_Connect'
        self.clientIMG = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientIMG.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("As a client, displayImg receives imgs from %s:%d" %
              (self.client_port_Img[0], self.client_port_Img[1]))
        self.clientIMG.connect(self.client_port_Img)

    def get_q_xy_mean(self, current_point):
        # center_x = self.q_center[0]
        # center_y = self.q_center[1]
        # center_x
        if not self.q_list:
            return True
        mean_x = 0
        mean_y = 0
        for point in self.q_list:
            # left_top_x = point[0]
            # left_top_y = point[1]
            # right_bottom_x = point[2]
            # right_bottom_y = point[3]
            # temp_center_x = (left_top_x + right_bottom_x) / 2.0
            # temp_center_y = (left_top_y + right_bottom_y) / 2.0
            mean_x += point[0]
            mean_y += point[1]
        mean_x /= len(self.q_list)
        mean_y /= len(self.q_list)
        temp_center_x = (current_point[2] - current_point[0]) / 2.0
        temp_center_y = (current_point[3] - current_point[1]) / 2.0

        distance = math.sqrt((mean_x - temp_center_x) **
                             2 + (mean_y - temp_center_y) ** 2)
        print(distance)
        if distance > 200:
            return False
        return True

    def ProcessImg(self):
        global CLOSE
        print 'displayImg_Object shows imgs'
        self.name = "displayImg"
        self.clientIMG.send(struct.pack(
            "hh", self.resolution[0], self.resolution[1]))
        self.start_time = time.time()
        if SENDER_ON_WIN:
            type_model = 'ii'
            HEAD_SIZE = 8
        else:
            type_model = 'll'
            HEAD_SIZE = 16
        while 1:
            info = struct.unpack(type_model, self.clientIMG.recv(HEAD_SIZE))
            buf_size = info[0]
            if buf_size:
                try:
                    self.buf = b""
                    temp_buf = self.buf
                    while buf_size:
                        temp_buf = self.clientIMG.recv(buf_size)
                        buf_size -= len(temp_buf)
                        self.buf += temp_buf
                    data = numpy.fromstring(self.buf, dtype='uint8')
                    image = cv2.imdecode(data, 1)
                    # 阻塞式的加入队列，加入的是自定义类型，包含图片信息
                    temp_image = ImageAndIndex(image, info[1])
                    self.q.put(temp_image, block=True)
                    self.clientIMG.send(struct.pack("h", 168))
                except Exception as e:
                    print(e)
                    self.clientIMG.close()
                    cv2.destroyAllWindows()
                    print("I'm out!")
                    break
                # finally:
                # if cv2.waitKey(10) == 27:
                #     self.clientIMG.close()
                #     cv2.destroyAllWindows()
                #     print("I'm out!")
                #     break

    def show_image(self, images, fps):
        for image in images:
            try:
                print("show")
                print(image.detecRec)
                cv2.rectangle(image.image, (abs(int(image.detecRec[0])), abs(int(image.detecRec[2]))), (abs(
                    int(image.detecRec[1])), abs(int(image.detecRec[3]))), (0, 255, 0), 4)

                # 显示fps
                font = cv2.FONT_HERSHEY_TRIPLEX
                cv2.putText(image.image, 'fps:%.2f' %
                            fps, (50, 50), font, 1, (255, 255, 0), 1, False)
                ###### uncomment the following 2 lines to enable fullscreen when you can successfully run the code
                #  cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
                # cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
                cv2.imshow(windowName, image.image)
            finally:
                if cv2.waitKey(10) == 27:
                    raise KeyboardInterrupt

    def process_buf(self):
        while 1:
            try:
                # 计算帧速
                # 存放要显示的原始图片
                image_origin = []
                batchImageData = numpy.zeros((BATCH_SIZE, 360, 640, 3))
                for i in range(BATCH_SIZE):
                    t_img = self.q.get(timeout=5)
                    batchImageData[i, :, :] = t_img.image[:, :]
                    image_origin.append(t_img)
                # 检测出来的结果，三组，每组是左上角和右下角的坐标
                detecRec = procfunc.detectionAndTracking(batchImageData, 1)
                # print(str(
                #     image_origin[i].index) + ", perform detection processing successfully, and the result is " + str(detecRec))
                for i in range(BATCH_SIZE):


                    # 如果当前的结果可以采用
                    # if self.get_q_xy_mean(detecRec[i]):
                    #     left_top_x = detecRec[i][0]
                    #     left_top_y = detecRec[i][1]
                    #     right_bottom_x = detecRec[i][2]
                    #     right_bottom_y = detecRec[i][3]
                    #     temp_center_x = (left_top_x + right_bottom_x) / 2.0
                    #     temp_center_y = (left_top_y + right_bottom_y) / 2.0
                    #     self.q_list.append((temp_center_x, temp_center_y))
                    #     image_origin[i].detecRec = detecRec[i]
                    # else:
                    #     self.q_list.append(self.q_list[-1])
                    #     image_origin[i].detecRec = self.q_list[-1]
                    # if len(self.q_list) >= 6:
                    #     del self.q_list[0]
                    image_origin[i].detecRec = detecRec[i]
                # 计算帧速
                self.end_time = time.time()
                fps = 1 / ((self.end_time - self.start_time) / BATCH_SIZE)
                self.show_image(image_origin, fps)
                self.start_time = self.end_time
            except KeyboardInterrupt as e:
                print(e)
                self.clientIMG.close()
                cv2.destroyAllWindows()
                self.showThread.join()
                print("Ctrl + C : I'm out!")
                break
            # finally:
            #     if cv2.waitKey(10) == 27:
            #         self.clientIMG.close()
            #         cv2.destroyAllWindows()
            #         self.showThread.join()
            #         print("ESC: I'm out!")
            #         break

    def ProcessInThread(self):
        print 'displayImg_Connect_Object   Get_Data'
        self.showThread = threading.Thread(target=self.ProcessImg)
        self.showThread.start()


if __name__ == '__main__':
    ###### Change the ip and port according to your setting in the line below
    displayImg = process_display_Object((MyIP, 3010))
    displayImg.Socket_Connect_Client()
    displayImg.ProcessInThread()
    displayImg.process_buf()
