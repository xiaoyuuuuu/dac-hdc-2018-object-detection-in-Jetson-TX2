#include "pydarknet.h"

#define GET_PIXEL(ptr,w,h,c) ((ptr)[(c)*IN_H*IN_W + (h)*IN_W + (w)])

// threads for transfer image
pthread_t transfer_t;
pthread_t transfer_t1;
pthread_t transfer_t2;

image *resized_image;

sem_t sem_pic;
sem_t sem_pic1;
sem_t sem_pic2;

pthread_args *pthread_t1;    
pthread_args *pthread_t2; 
pthread_args *pthread_t3;

struct_transfer_image *transfer_pic;
struct_transfer_image *transfer_pic_1;
struct_transfer_image *transfer_pic_2;

/**
 * @brief get_val
 * @param ptr
 * @param x
 * @param y
 * @param z
 * @param dx
 * @param dy
 * @return
 */
//static inline float get_val(double* ptr, int x, int y, int z, float dx, float dy)
static inline float get_val(float* ptr, int x, int y, int z, float dx, float dy)

{
	float val = GET_PIXEL(ptr, x, y, z);
	//printf("[ %d, %d, %d] = %f\n",x,y,z, val);
	if(x == IN_W-1 && y == IN_H-1) return val;
	if(x == IN_W-1)
	{
		return val*(1-dy) + dy*GET_PIXEL(ptr, x, y+1, z);
	}
	if(y == IN_H-1)
	{
		return val*(1-dx) + dx*GET_PIXEL(ptr, x+1, y, z);
	}
	val = val*(1-dx) + dx*GET_PIXEL(ptr, x+1, y, z);
	float val1 = (1-dx)*GET_PIXEL(ptr, x, y+1, z)+ dx*GET_PIXEL(ptr, x+1, y+1, z);
	return val*(1-dy)+val1*dy;
}


/**
 * @brief our_letterbox_image
 * @param im
 * @param w
 * @param h
 * @return
 */
static void *our_letterbox_image(/*double* conv_ptr, int w, int h, int index*/struct_transfer_image *transfer_arg)
{
	int new_w = IN_W;
	int new_h = IN_H;
	if (((float)(transfer_arg->w)/IN_W) < ((float)(transfer_arg->h)/IN_H)) {
		new_w = transfer_arg->w;
		new_h = (IN_H * transfer_arg->w)/IN_W;
	} else {
		new_h = transfer_arg->h;
		new_w = (IN_W * transfer_arg->h)/IN_H;
	}

	resized_image[transfer_arg->index] = make_image(transfer_arg->w, transfer_arg->h, 3);
	int x, y, z;

	//buffering solution
	float* buf = malloc(sizeof(float)*IN_H*IN_W*3);

	for(y = 0; y < IN_H; y++)
		for(x = 0; x < IN_W; x++)
			for(z = 2; z >= 0; z--)
				buf[z*IN_W*IN_H + y*IN_W + x] = (float) (transfer_arg->conv_ptr[y*3*IN_W+x*3+2-z])/255.;

	float w_scale = (float)(IN_W - 1) / (new_w - 1);
	float h_scale = (float)(IN_H - 1) / (new_h - 1);
	for(z = 0; z < 3; z++)
	{
		for(y = 0; y < transfer_arg->h; y++)
		{
			float sy = (y - (transfer_arg->h-new_h)/2)*h_scale;
			int iy = (int) sy;
			float dy = sy - iy;
			//printf("new line: %d -> old line: %d\n", y, iy);
			if(y < (transfer_arg->h-new_h)/2 || y >= (transfer_arg->h+new_h)/2)
			{
				for(x = 0; x < transfer_arg->w; x++)
					resized_image[transfer_arg->index].data[z*transfer_arg->w*transfer_arg->h + y*transfer_arg->w + x] = .5f;
				continue;
			}
			for(x = 0; x < transfer_arg->w; x++)
			{
				if(x < (transfer_arg->w-new_w)/2 || x >= (transfer_arg->w+new_w)/2 )
				{
					resized_image[transfer_arg->index].data[z*transfer_arg->w*transfer_arg->h + y*transfer_arg->w + x] = .5f;
				} else {
					float sx = (x - (transfer_arg->w-new_w)/2)*w_scale;
					int ix = (int) sx;
					float dx = sx - ix;
					resized_image[transfer_arg->index].data[z*transfer_arg->w*transfer_arg->h + y*transfer_arg->w + x] = get_val(buf, ix, iy, z, dx, dy);//get_val(conv_ptr, ix, iy, z, dx, dy);
					//printf("[ %d, %d, %d] = %f\n",z,y,x,resized.data[z*w*h + y*w + x]);
				}
			}
		}
	}
	free(buf);
	sem_post(&sem_pic);
	return NULL;
}

static void *our_letterbox_image_1(/*double* conv_ptr, int w, int h, int index*/struct_transfer_image *transfer_arg)
{
	int new_w = IN_W;
	int new_h = IN_H;
	if (((float)(transfer_arg->w)/IN_W) < ((float)(transfer_arg->h)/IN_H)) {
		new_w = transfer_arg->w;
		new_h = (IN_H * transfer_arg->w)/IN_W;
	} else {
		new_h = transfer_arg->h;
		new_w = (IN_W * transfer_arg->h)/IN_H;
	}

	resized_image[transfer_arg->index] = make_image(transfer_arg->w, transfer_arg->h, 3);
	int x, y, z;

	//buffering solution
	float* buf = malloc(sizeof(float)*IN_H*IN_W*3);

	for(y = 0; y < IN_H; y++)
		for(x = 0; x < IN_W; x++)
			for(z = 2; z >= 0; z--)
				buf[z*IN_W*IN_H + y*IN_W + x] = (float) (transfer_arg->conv_ptr[y*3*IN_W+x*3+2-z])/255.;

	float w_scale = (float)(IN_W - 1) / (new_w - 1);
	float h_scale = (float)(IN_H - 1) / (new_h - 1);
	for(z = 0; z < 3; z++)
	{
		for(y = 0; y < transfer_arg->h; y++)
		{
			float sy = (y - (transfer_arg->h-new_h)/2)*h_scale;
			int iy = (int) sy;
			float dy = sy - iy;
			//printf("new line: %d -> old line: %d\n", y, iy);
			if(y < (transfer_arg->h-new_h)/2 || y >= (transfer_arg->h+new_h)/2)
			{
				for(x = 0; x < transfer_arg->w; x++)
					resized_image[transfer_arg->index].data[z*transfer_arg->w*transfer_arg->h + y*transfer_arg->w + x] = .5f;
				continue;
			}
			for(x = 0; x < transfer_arg->w; x++)
			{
				if(x < (transfer_arg->w-new_w)/2 || x >= (transfer_arg->w+new_w)/2 )
				{
					resized_image[transfer_arg->index].data[z*transfer_arg->w*transfer_arg->h + y*transfer_arg->w + x] = .5f;
				} else {
					float sx = (x - (transfer_arg->w-new_w)/2)*w_scale;
					int ix = (int) sx;
					float dx = sx - ix;
					resized_image[transfer_arg->index].data[z*transfer_arg->w*transfer_arg->h + y*transfer_arg->w + x] = get_val(buf, ix, iy, z, dx, dy);//get_val(conv_ptr, ix, iy, z, dx, dy);
					//printf("[ %d, %d, %d] = %f\n",z,y,x,resized.data[z*w*h + y*w + x]);
				}
			}
		}
	}
	free(buf);
	sem_post(&sem_pic1);
	return NULL;
}

static void *our_letterbox_image_2(/*double* conv_ptr, int w, int h, int index*/struct_transfer_image *transfer_arg)
{
	int new_w = IN_W;
	int new_h = IN_H;
	if (((float)(transfer_arg->w)/IN_W) < ((float)(transfer_arg->h)/IN_H)) {
		new_w = transfer_arg->w;
		new_h = (IN_H * transfer_arg->w)/IN_W;
	} else {
		new_h = transfer_arg->h;
		new_w = (IN_W * transfer_arg->h)/IN_H;
	}

	resized_image[transfer_arg->index] = make_image(transfer_arg->w, transfer_arg->h, 3);
	int x, y, z;

	//buffering solution
	float* buf = malloc(sizeof(float)*IN_H*IN_W*3);

	for(y = 0; y < IN_H; y++)
		for(x = 0; x < IN_W; x++)
			for(z = 2; z >= 0; z--)
				buf[z*IN_W*IN_H + y*IN_W + x] = (float) (transfer_arg->conv_ptr[y*3*IN_W+x*3+2-z])/255.;

	float w_scale = (float)(IN_W - 1) / (new_w - 1);
	float h_scale = (float)(IN_H - 1) / (new_h - 1);
	for(z = 0; z < 3; z++)
	{
		for(y = 0; y < transfer_arg->h; y++)
		{
			float sy = (y - (transfer_arg->h-new_h)/2)*h_scale;
			int iy = (int) sy;
			float dy = sy - iy;
			//printf("new line: %d -> old line: %d\n", y, iy);
			if(y < (transfer_arg->h-new_h)/2 || y >= (transfer_arg->h+new_h)/2)
			{
				for(x = 0; x < transfer_arg->w; x++)
					resized_image[transfer_arg->index].data[z*transfer_arg->w*transfer_arg->h + y*transfer_arg->w + x] = .5f;
				continue;
			}
			for(x = 0; x < transfer_arg->w; x++)
			{
				if(x < (transfer_arg->w-new_w)/2 || x >= (transfer_arg->w+new_w)/2 )
				{
					resized_image[transfer_arg->index].data[z*transfer_arg->w*transfer_arg->h + y*transfer_arg->w + x] = .5f;
				} else {
					float sx = (x - (transfer_arg->w-new_w)/2)*w_scale;
					int ix = (int) sx;
					float dx = sx - ix;
					resized_image[transfer_arg->index].data[z*transfer_arg->w*transfer_arg->h + y*transfer_arg->w + x] = get_val(buf, ix, iy, z, dx, dy);//get_val(conv_ptr, ix, iy, z, dx, dy);
					//printf("[ %d, %d, %d] = %f\n",z,y,x,resized.data[z*w*h + y*w + x]);
				}
			}
		}
	}
	free(buf);
	sem_post(&sem_pic2);
	return NULL;
}

void __init( void ) {}

void __finalize( void ) {}

static void test_detector(float thresh, int** coords)
{

	float nms=.45;

 	pthread_t1 = (pthread_args *)malloc(sizeof(pthread_args));
        pthread_t1->net = net;
        pthread_create(&t1, NULL, (void *)network_predict_pthread, pthread_t1);

        pthread_t2 = (pthread_args *)malloc(sizeof(pthread_args));
        pthread_t2->net = net_newthread;
        pthread_create(&t2, NULL, (void *)network_predict_pthread1, pthread_t2);

	pthread_t3 = (pthread_args *)malloc(sizeof(pthread_args));
        pthread_t3->net = net_newthread1;
        pthread_create(&t3, NULL, (void *)network_predict_pthread2, pthread_t3);
	
   	pthread_join(t1, NULL);
	pthread_join(t2, NULL);
	pthread_join(t3, NULL);
  
	free(pthread_t1);
	free(pthread_t2);
	free(pthread_t3);


   	image im;
  	im.h = IN_H;
  	im.w = IN_W;
    //printf("%s: Predicted in %f seconds.\n", path, what_time_is_it_now()-time);
    	int nboxes = 0;
    	detection *dets = get_network_boxes(net, im.w, im.h, thresh, thresh, 0, 1, &nboxes);

    	int nboxes1 = 0;
    	detection *dets1 = get_network_boxes(net_newthread, im.w, im.h, thresh, thresh, 0, 1, &nboxes1);

    	int nboxes2 = 0;
    	detection *dets2 = get_network_boxes(net_newthread1, im.w, im.h, thresh, thresh, 0, 1, &nboxes2);

    //printf("%d\n", nboxes);
    	layer l = net->layers[net->n-1];
    	if (nms)
        	do_nms_sort(dets, nboxes, l.classes, nms);
    	if (nms)
        	do_nms_sort(dets1, nboxes1, l.classes, nms);
    	if (nms)
        	do_nms_sort(dets2, nboxes2, l.classes, nms);

    	draw_detections(im, dets, nboxes, thresh, names, l.classes, coords[0]);
    	draw_detections(im, dets1, nboxes1, thresh, names, l.classes, coords[1]);
    	draw_detections(im, dets2, nboxes2, thresh, names, l.classes, coords[2]);

    	free_detections(dets, nboxes);
    	free_detections(dets1, nboxes1);
    	free_detections(dets2, nboxes2);

	pthread_join(transfer_t, NULL);
	pthread_join(transfer_t1, NULL);
	pthread_join(transfer_t2, NULL);

	free(transfer_pic);
	free(transfer_pic_1);
	free(transfer_pic_2);

    //free_image(im);
    //save_image(sized,"res");
}


int** do_detection(double* data, float thresh)
{

	int	i;//, h, w, c;
	double*	float_buf = data;

	sem_init(&sem_pic, 0, 0);
	sem_init(&sem_pic1, 0, 0);
	sem_init(&sem_pic2, 0, 0);

	resized_image = (image *)calloc(batch_size, sizeof(image));

	//initialize coordinates
	int **coords = (int**)calloc(batch_size, sizeof(int*));
	int *real_coord = (int*) calloc(batch_size*4, sizeof(int));
	for(int j = 0; j < batch_size; ++j){
		coords[j] = real_coord + 4*j;
	}

	transfer_pic = (struct_transfer_image *)malloc(sizeof(struct_transfer_image));
	transfer_pic->w=NET_SIZE;
	transfer_pic->h=NET_SIZE;
	transfer_pic->index=0;
	transfer_pic->conv_ptr=float_buf+transfer_pic->index*IN_H*IN_W*3;
	pthread_create(&transfer_t, NULL, (void *)our_letterbox_image, transfer_pic);	

	transfer_pic_1 = (struct_transfer_image *)malloc(sizeof(struct_transfer_image));
	transfer_pic_1->w=NET_SIZE;
	transfer_pic_1->h=NET_SIZE;
	transfer_pic_1->index=1;
	transfer_pic_1->conv_ptr=float_buf+transfer_pic_1->index*IN_H*IN_W*3;
	pthread_create(&transfer_t1, NULL, (void *)our_letterbox_image_1, transfer_pic_1);

	transfer_pic_2 = (struct_transfer_image *)malloc(sizeof(struct_transfer_image));
	transfer_pic_2->w=NET_SIZE;
	transfer_pic_2->h=NET_SIZE;
	transfer_pic_2->index=2;
	transfer_pic_2->conv_ptr=float_buf+transfer_pic_2->index*IN_H*IN_W*3;
	pthread_create(&transfer_t2, NULL, (void *)our_letterbox_image_2, transfer_pic_2);

	test_detector(thresh, coords);

	for(i=0; i<batch_size; i++){
	    free_image(resized_image[i]);
    }
	
	return coords;
}


