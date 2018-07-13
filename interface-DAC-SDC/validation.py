import os
import sys
import matplotlib.pylab as plt
import cv2
import time
import numpy as np
import xml.dom.minidom
import random
import ctypes
import xml.etree.ElementTree as ET


class DetectorInstance:
    def __init__(self, data_file="dac_lj.data", cfg_file="dac_test5.cfg"):
        DataFile = "/home/embedded/zcq/yolov3/darknet/data/" + data_file
        # DataFile = "/home/embedded/zcq/darknet/data/dac_lj.data"
        CfgFile = "/home/embedded/zcq/yolov3/darknet/cfg/" + cfg_file
        # CfgFile = "/home/embedded/zcq/darknet/cfg/dac_test5.cfg"
        #WeightFile = "/home/embedded/zcq/yolov3/darknet/backup/dac_test6_90000.weights"
        # WeightFile = "/home/embedded/zcq/darknet/backup/dac_test5_96000.weights"
        Thresh = 0

        self.p_DataFile = ctypes.c_char_p(DataFile)
        self.p_CfgFile = ctypes.c_char_p(CfgFile)
        #self.p_WeightFile = ctypes.c_char_p(WeightFile)
        self.p_Thresh = ctypes.c_float(Thresh)

        dac_dll = ctypes.cdll.LoadLibrary
        self.dac_lib = dac_dll("/home/embedded/zcq/yolov3/darknet3/darknet.so")
        self.dac_lib.test_detector.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_int))
        # self.dac_lib.run_detector.restype = ctypes.POINTER(ctypes.POINTER(ctypes.c_int))

    def init_detector(self, imgPathFile):
        self.imgPathFile = imgPathFile
        # self.cmd = ctypes.c_char_p("test")
        self.gpu_list = ctypes.c_char_p("0")
        # self.dac_lib.init_test_detector_cpu(self.p_NamesFile, self.p_CfgFile, self.p_WeightFile, ctypes.c_char_p("init"), self.p_Thresh, ctypes.c_int(self.img_num))

    def detect(self, weightFile):
        self.p_WeightFile = ctypes.c_char_p(weightFile)
        self.result = self.dac_lib.test_detector(self.p_DataFile, self.p_CfgFile, self.p_WeightFile,
                                                 ctypes.c_char_p(self.imgPathFile), self.p_Thresh, self.gpu_list)
        # self.result = self.dac_lib.run_detector(self.cmd, ctypes.c_char_p(self.imgPathFile), self.p_DataFile, self.p_CfgFile, self.p_WeightFile, self.gpu_list, self.p_Thresh)
        #os.remove(self.imgPathFile)

def getInfoFromXml(xml):
    #print(xml)
    tree = ET.parse(xml)
    root = tree.getroot()
    object = root.find("object")
    nameNode = object.find("name")
    bndNode = object.find("bndbox")
    try:
        class_name_index = int(nameNode.text)
        classes = []
        for line in open("dac_82.names"):
            classes.append(line)
        class_name = classes[class_name_index]
    except Exception:
        class_name = nameNode.text
    #print(class_name)
    xmin = bndNode.find("xmin").text
    xmax = bndNode.find("xmax").text
    ymin = bndNode.find("ymin").text
    ymax = bndNode.find("ymax").text
    #print(xmin+"|"+xmax+"|"+ymin+"|"+ymax)
    return class_name, int(float(xmin)), int(float(xmax)), int(float(ymin)), int(float(ymax))

def storeResultsToXML(detector, allImageName, myXmlDir):
    for i in range(len(allImageName)):
        doc = xml.dom.minidom.Document()
        root = doc.createElement('annotation')

        doc.appendChild(root)
        nameE = doc.createElement('filename')
        nameT = doc.createTextNode(allImageName[i])
        nameE.appendChild(nameT)
        root.appendChild(nameE)

        sizeE = doc.createElement('size')
        nodeWidth = doc.createElement('width')
        nodeWidth.appendChild(doc.createTextNode("640"))
        nodelength = doc.createElement('length')
        nodelength.appendChild(doc.createTextNode("360"))
        sizeE.appendChild(nodeWidth)
        sizeE.appendChild(nodelength)
        root.appendChild(sizeE)

        object = doc.createElement('object')
        nodeName = doc.createElement('name')
        nodeName.appendChild(doc.createTextNode('Object'))
        nodebndbox = doc.createElement('bndbox')
        nodebndbox_xmin = doc.createElement('xmin')
        nodebndbox_xmin.appendChild(doc.createTextNode(str(detector.result[i][0])))
        nodebndbox_xmax = doc.createElement('xmax')
        nodebndbox_xmax.appendChild(doc.createTextNode(str(detector.result[i][1])))
        nodebndbox_ymin = doc.createElement('ymin')
        nodebndbox_ymin.appendChild(doc.createTextNode(str(detector.result[i][2])))
        nodebndbox_ymax = doc.createElement('ymax')
        nodebndbox_ymax.appendChild(doc.createTextNode(str(detector.result[i][3])))
        nodebndbox.appendChild(nodebndbox_xmin)
        nodebndbox.appendChild(nodebndbox_xmax)
        nodebndbox.appendChild(nodebndbox_ymin)
        nodebndbox.appendChild(nodebndbox_ymax)

        object.appendChild(nodeName)
        object.appendChild(nodebndbox)
        root.appendChild(object)

        fileName = allImageName[i].replace('jpg', 'xml')
        fp = open(myXmlDir + "/" + fileName, 'w')
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding='utf-8')

##write time result to alltime.txt
def writeTxt(flag, runTime, originalXmls, predictedXmlPath, allImageNames):
    f_result = open(predictedXmlPath + "/weight_result.txt", "a+")
    predictedXmls = predictedXmlPath + "/" + flag + "-xml"
    iou_list = []
    fps = len(allImageNames) / runTime
    class_same_count = 0
    for i in range(len(allImageNames)):
        o_className, o_xmin, o_xmax, o_ymin, o_ymax = getInfoFromXml(originalXmls + "/" + allImageNames[i].replace("jpg", "xml"))
        p_className, p_xmin, p_xmax, p_ymin, p_ymax = getInfoFromXml(predictedXmls + "/" + allImageNames[i].replace("jpg", "xml"))
        #print("o_data: "+str(o_xmin)+"|"+str(o_xmax)+"|"+str(o_ymin)+"|"+str(o_ymax)+"\n")
        #print("p_data: "+str(p_xmin)+"|"+str(p_xmax)+"|"+str(p_ymin)+"|"+str(p_ymax)+"\n")
        if o_className == p_className:
            class_same_count = class_same_count + 1
        i_w = min(o_xmax, p_xmax) - max(o_xmin, p_xmin)
        i_h = min(o_ymax, p_ymax) - max(o_ymin, p_ymin)
        #print("i: "+str(i_w)+"|"+str(i_h)+"\n")
        if i_w < 0:
            i_w = 0
        if i_h < 0:
            i_h = 0
        o_area = (o_xmax - o_xmin) * (o_ymax - o_ymin)
        p_area = (p_xmax - p_xmin) * (p_ymax - p_ymin)
        #print("area: "+str(o_area)+"|"+str(p_area)+"\n")
        iou = float(i_w * i_h) / (o_area + p_area - i_w * i_h)
        #iou = (min(o_xmax, p_xmax) - max(o_xmin, p_xmin))*(min(o_ymax, p_ymax) - max(o_ymin, p_ymin)) / ((o_xmax - o_xmin) * (o_ymax - o_ymin) + (p_xmax - p_xmin) * (p_ymax - p_ymin) - (min(o_xmax, p_xmax) - max(o_xmin, p_xmin))*(min(o_ymax, p_ymax) - max(o_ymin, p_ymin)))
        #print(str(iou))
        iou_list.append(iou)
    class_same_accuracy = class_same_count * 100 / len(os.listdir(originalXmls))
    f_result.write(flag + "----" + "FPS: " + str(fps) + ", Accuray: " + str(class_same_accuracy) + "%, Average IOU: " + str(sum(iou_list) / len(iou_list)) + "\n")
    f_result.close()

##write time result to alltime.txt
def writeTxtDirectly(originalXmls, predictedXmlPath):
    print(originalXmls)
    print(predictedXmlPath)
    f_result = open(predictedXmlPath + "/result.txt", "a+")
    #predictedXmls = predictedXmlPath + "/" + flag + "-xml"
    iou_list = []
    #fps = len(allImageNames) / runTime
    #class_same_count = 0
    for xml in os.listdir(originalXmls):
        print(xml)
        o_className, o_xmin, o_xmax, o_ymin, o_ymax = getInfoFromXml(originalXmls + "/" + xml)
        p_className, p_xmin, p_xmax, p_ymin, p_ymax = getInfoFromXml(predictedXmlPath + "/" + xml)
        #print("o_data: "+str(o_xmin)+"|"+str(o_xmax)+"|"+str(o_ymin)+"|"+str(o_ymax)+"\n")
        #print("p_data: "+str(p_xmin)+"|"+str(p_xmax)+"|"+str(p_ymin)+"|"+str(p_ymax)+"\n")
        #if o_className == p_className:
            #class_same_count = class_same_count + 1
        i_w = min(o_xmax, p_xmax) - max(o_xmin, p_xmin)
        if i_w < 0:
            i_w = 0
        i_h = min(o_ymax, p_ymax) - max(o_ymin, p_ymin)
        if i_h < 0:
            i_h = 0
        #print("i: "+str(i_w)+"|"+str(i_h)+"\n")
        o_area = (o_xmax - o_xmin) * (o_ymax - o_ymin)
        p_area = (p_xmax - p_xmin) * (p_ymax - p_ymin)
        #print("area: "+str(o_area)+"|"+str(p_area)+"\n")
        iou = float(i_w * i_h) / (o_area + p_area - i_w * i_h)
        print(iou)
        #iou = (min(o_xmax, p_xmax) - max(o_xmin, p_xmin))*(min(o_ymax, p_ymax) - max(o_ymin, p_ymin)) / ((o_xmax - o_xmin) * (o_ymax - o_ymin) + (p_xmax - p_xmin) * (p_ymax - p_ymin) - (min(o_xmax, p_xmax) - max(o_xmin, p_xmin))*(min(o_ymax, p_ymax) - max(o_ymin, p_ymin)))
        #print(str(iou))
        iou_list.append(iou)
    #class_same_accuracy = class_same_count * 100 / len(os.listdir(originalXmls))
    print(sum(iou_list) / len(iou_list))
    f_result.write("Average IOU: " + str(sum(iou_list) / len(iou_list)) + "\n")
    f_result.close()

if __name__ == "__main__":
    writeTxtDirectly(sys.argv[1], sys.argv[2])
    
