#include "darknet.h"
#include <numpy/ndarrayobject.h>
#include <string.h>
#include <stdio.h>
#include <pthread.h>

#ifndef __PYDARKNET_
#define __PYDARKNET_

#define NET_SIZE 416
#define IN_W 640
#define IN_H 360
#define NEW_H 234
#define HALF_H 180	
#define NEW_W NET_SIZE
#define SCALE ((float)(IN_W - 1) / (NET_SIZE -1))

//#define GET_PIXEL(ptr, w, h, c) ((float) (ptr)[(h)*IN_W*3 + (w)*3 + 2 - (c)]/255.)

pthread_t t1;
pthread_t t2;
pthread_t t3;

network * net;
// pthread 1
network * net_newthread;
// pthread 2
network * net_newthread1;
// pthread 3

char** names;
int batch_size;

int** do_detection(double*, float);
void __finalize(void);
void __init(void);

#endif
