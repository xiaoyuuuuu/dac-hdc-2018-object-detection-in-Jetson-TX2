/*******************************************************
 *
 * 这个项目是讲darknet detector封装成Python Extention
 * 的工作，为了提高资源利用率，讲opencv的imagePython对象
 * 有效转化成darknet可直接利用的对象，避免反复磁盘访问，
 * 具体方法支持：
 *
 * PyObject -(pyopencv_to)-> Mat -(IplImage(Mat*))->
 * IplImage -(ipl_to_image)->Image(darknet原生结构)
 * 其中ipl_to_image有优化空间
 *
 *
 * update：
 * PyObject的类型是numpy的ndarray，而且numpy又有c++接口
 * 那么我们只要开发出一套C-numpy -> image的转换就可以了
 * 技术测试：tech_test.cpp
 *
 *******************************************************/

#include "pydarknet.h"

#ifndef radical__
/**
 * @brief build_pyarr
 * 单独写出来，反正就是为了把int类型转换成一个可以返回的python对象
 * @param coordinates 表示边界的四维数组
 * @return 创建好的可以直接返回的Python对象
 */
inline static PyObject* build_pyarr(int** coordinates)
{
	//int* i_data = calloc(batch_size*4, sizeof(int));
	//printf("access : %d \n",coordinates[0][1]);
	//memcpy(i_data, coordinates[0], sizeof(int)*4*batch_size);

	npy_intp* dims = calloc(2,sizeof(npy_intp));
	dims[0] = batch_size;
	dims[1] = 4;

	PyObject* ret = PyArray_SimpleNewFromData(2, dims, NPY_INT, coordinates[0]);
	Py_INCREF(ret);
	return ret;
}

#include <Python.h>
/**
 * @brief pydarknet_detect
 * python 直接调用的函数，现在做一个过渡，真正的实现不要和Python接口这种东西混在一起
 * @param self
 * @param args
 * @return
 */
static PyObject* pydarknet_detect(PyObject* self, PyObject* args)
{
	float 		thresh;
	PyObject* 	parr;

	PyArg_ParseTuple(args, "fO",&thresh, &parr);
	//----------------------------------
	//printf("Your thresh: %f\n",thresh);
	//----------------------------------
	PyArrayObject *ndarr = (PyArrayObject* ) parr;	//获得对象指针
	/*
	if(ndarr->nd != 4 
	|| ndarr->dimensions[1] != IN_H
	|| ndarr->dimensions[2] != IN_W
	|| ndarr->dimensions[3] != 3
	|| ndarr->data == NULL)
	{
		printf("fatal error: I don't know what happened to input data!\n");
		printf("Your Pic:\n\tsize: %d * %d\n",ndarr->dimensions[1],ndarr->dimensions[2]);
		exit(-1); //意思就是说这个numpy的nd数组肯定是4维的，提交前注释掉此分支
	}
	*/
	batch_size = ndarr->dimensions[0];
	if(!batch_size) Py_RETURN_NONE;
	//----------------------------------
	//printf("Batch with %d pics\n",batch_size);
	//----------------------------------

	//把核心逻辑放到别的文件里吧
	int** coord = do_detection((double *)ndarr->data, thresh);

	//cord进行一些处理，生成可以用来返回的对象
	PyObject* pyArray = build_pyarr(coord);

	batch_size = 0; //最后记得归0
	return pyArray;
}

/**
 * @brief pydarknet_init_detector
 * 完成头文件中关键组件的初始化，同时调用不同实现的初始化函数
 *  datacfg	data文件
 *  cfgfile	cfg文件
 *  weightfile	权值文件
 */
static PyObject* pydarknet_init_detector(PyObject* self, PyObject* args)
{
	char *datacfg, *cfgfile, *weightfile;
	PyArg_ParseTuple(args, "sss", &datacfg, &cfgfile, &weightfile);
	//---------------------------------------------------------------------
	printf("data: %s\ncfg: %s\nweights: %s\n",datacfg, cfgfile, weightfile);
	//---------------------------------------------------------------------

	srand(2222222);
	__init();	//根据功能不同调用不同的
	list *options = read_data_cfg(datacfg);
	char *name_list = option_find_str(options, "names", "data/names.list");
	names = get_labels(name_list);
	net = load_network(cfgfile, weightfile, 0);
//	set_batch_network(net, 1);

    net_newthread = load_network(cfgfile, weightfile, 0);
//  set_batch_network(net_newthread, 1);

    net_newthread1 = load_network(cfgfile, weightfile, 0);
//  set_batch_network(net_newthread1, 1);

	Py_RETURN_NONE;//用这个维持Python解释器环境的正常
}

/**
 * @brief pydarknet_finalize_detector
 * 当工作结束后回收资源用，并不是所有实现都用的着
 * @param self
 * @param args
 * @return
 */
static PyObject* pydarknet_finalize_detector( PyObject* self, PyObject* args )
{
	__finalize();
	Py_RETURN_NONE;
}

static PyMethodDef meth_list[] =
{
	{"detect", pydarknet_detect, METH_VARARGS},
	{"init_detector", pydarknet_init_detector, METH_VARARGS},
	{"finalize_detector", pydarknet_finalize_detector, METH_NOARGS}, 
	{NULL, NULL, 0, NULL}
};

void initpydarknet()
{
	Py_InitModule("pydarknet", meth_list);
	_import_array();
}

#endif
