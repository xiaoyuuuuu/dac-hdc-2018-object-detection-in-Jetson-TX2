
        .text
        .syntax   unified

        .align  4
        .global gemm_ker_pld
        .arm

gemm_ker_pld:
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        @
        @ float gemm_ker_pld(float * vec0,
        @                    float * vec1,
        @                    unsigned int num,
	    @                    float * vec2)
        @
        @  r0: vec0's base pointer
        @  r1: vec1's base pointer
        @  r2: vector length
		@  r3: the result vector
        @
        @  Note: Here we assume r2%16==0
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

	
        vmov.f32          q10, #0.0
        vmov.f32          q11, #0.0
        vmov.f32          q12, #0.0
        vmov.f32          q13, #0.0	


.L_mainloop_vec_16_pld:
    
        vldm  r0!, {d0, d1, d2, d3, d4, d5, d6, d7}
        vldm  r1!, {d10, d11, d12, d13, d14, d15, d16, d17}

        pld [r0, #0]
        pld [r1, #0]
        pld [r0, #32]
        pld [r1, #32]
       	pld [r0, #64]
        pld [r1, #64]
        pld [r0, #96]
        pld [r1, #96]

        
        vmla.f32        q10, q0, q5
        vmla.f32        q11, q1, q6
        vmla.f32        q12, q2, q7
        vmla.f32        q13, q3, q8

        subs            r2, r2, #16
        bgt             .L_mainloop_vec_16_pld 

.L_return_vec_16_pld:
        vadd.f32        q15, q10, q11
        vadd.f32        q14, q12, q13
        vadd.f32        q15, q15, q14
        vadd.f32        d30, d30, d31

		vmov.f32		r0,d30[1]
		vmov.f32 		d31[0],r0

		vadd.f32		d18,d30,d31

		vst1.f32		{d18[0]},[r3]
        @ return
        bx                lr



        .align  4
        .global gemm_ker_nn
        .arm

gemm_ker_nn:
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        @
        @ float gemm_ker_nn(float * vec0,
        @                    float * vec1,
        @                    unsigned int num,
	    @                    float * vec2)
        @
        @  r0: vec0's base pointer
        @  r1: vec1's base pointer
        @  r2: vector length
        @
        @  Note: Here we assume r2%16==0
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

		
		vld1.f32   		  {d0[]},[r0]
		vld1.f32   		  {d1[]},[r0]  	

        pld [r0,#0]				

.L:

        vldm  r1!, {d2, d3, d4, d5, d6, d7, d8, d9}
		vldm  r3,  {d10, d11, d12, d13, d14, d15, d16, d17}
		
		pld [r1,#0]
		pld [r1,#32]
		pld [r1,#64]
		pld [r1,#96]
		pld [r3,#0]
		pld [r3,#32]
		pld [r3,#64]
		pld [r3,#96]

		vmla.f32 		q5,q1,q0
		vmla.f32 		q6,q2,q0		
		vmla.f32 		q7,q3,q0
		vmla.f32 		q8,q4,q0

		vstm  r3!,  {d10, d11, d12, d13, d14, d15, d16, d17}
		
        subs            r2, r2, #16
        bgt             .L

        @ return
        bx                lr


        .align  4
        .global gemm_ker_nn_block
        .arm

gemm_ker_nn_block:
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        @
        @ float gemm_ker_nn(float * vec0,
        @                    float * vec1,
        @                    unsigned int num,
	    @                    float * vec2)
        @
        @  r0: vec0's base pointer
        @  r1: vec1's base pointer
        @  r2: vector length
        @
        @  Note: Here we assume r2%16==0
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

		
		vld1.f32   		  {d0[]},[r0]
		vld1.f32   		  {d1[]},[r0]  	

        pld [r0,#0]				

.L1:

        vldm  r1!, {d2, d3, d4, d5, d6, d7, d8, d9}
		vldm  r3,  {d10, d11, d12, d13, d14, d15, d16, d17}
		
		pld [r1,#0]
		pld [r1,#32]
		pld [r1,#64]
		pld [r1,#96]
		pld [r3,#0]
		pld [r3,#32]
		pld [r3,#64]
		pld [r3,#96]

		vmla.f32 		q5,q1,q0
		vmla.f32 		q6,q2,q0		
		vmla.f32 		q7,q3,q0
		vmla.f32 		q8,q4,q0

		vstm  r3!,  {d10, d11, d12, d13, d14, d15, d16, d17}

        @ return
        bx                lr
