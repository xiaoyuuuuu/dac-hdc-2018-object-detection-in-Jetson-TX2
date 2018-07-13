# dac-hdc-2018-object-detection-in-Jetson-TX2

    采用了darknet平台上的yolov2对多张图片进行目标检测，采用voc2007格式的训练集进行训练，然后对多张图片集进行测试，在tx2上检测速度能达到23帧左右，识别准确率能达到67%左右。同时还可以用摄像头进行实时检测。



#测试过程
　　可以选择对一定数量的图片集进行测试，也可以选择用摄像头拍摄实时识别。（测试过程，我们在图片预处理和network_predict过程开了３个线程，这部分代码在examples/det.c文件中，可以对其进行修改来调整线程数。涉及到的文件有：det.c,pydarknet.c,pydarknet.h,darknet.h,network.c）

    一、对图片集进行测试
　　　　
　　　　１．将图片放在test/images文件夹下，同时，该文件夹下包含一个images.txt，内容为所有图片的绝对路径。（也可以放在其他文件夹，修改３中的路径即可）

　　　　２. interface-DAC-SDC为接口文件夹，修改procfunc_ex.py文件中的cfg和weights文件的路径和名称，并将你自己的cfg和weights权重文件放到interface-DAC-SDC/yolov2中。这里我们给出相匹配的cfg和weights文件：dac_May26.cfg和dac_May26.weights。
　　
　　　　３. 修改main_ex.py中DAC的路径为存放测试图片的images文件夹的路径，这里默认为test文件夹。

　　　　４. 执行main_ex.py。这里默认测试１０００张图片，在TX2上开超频大概１分钟左右，运行结果生成的xml文件路径为test/result/xml/SDU-LEGEND/。
　　　　运行时间帧数存放在test/result/time/alltime.txt。
　　　　图片测试的准确率运行validation.py可以获得：
　　　　　　　　python validation.py <测试图片生成的xml文件路径> <文件原始的xml文件路径>

　　二、用摄像头拍摄识别

	对cfg和weights文件的修改见上述第２步。

　　　　１. PC上通过摄像头获取视频，修改sender_1_client.py中的MyIP为图片接收方IP，执行命令：
	python sender_1_client.py

　　　　２．在tx2板子上进入interface-DAC-SDU文件夹下，修改display_buf.py中的MyIP为图片发送方IP执行：
	python display_buf.py


