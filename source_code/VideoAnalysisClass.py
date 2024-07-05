import numpy as np
import cv2 as cv
import time

class VideoAnalysis:
    def __init__(self):
        pass
       
    def ApplyFarnebackOpticalFlow(self,PrvsFrame,CurrentFrame,initial_flow,Set={}):

        params = dict( pyr_scale  = Set['pyr_scale'],
                  levels = Set['levels'],
                  winsize = Set['winsize'],
                  iterations = Set['iterations'],
                  poly_n = Set['poly_n'],
                  poly_sigma = Set['poly_sigma'],
                  flags=Set['flags'])
        
        params_List = list(params)
        for Var in params_List:
            if Var in Set:
              params[Var] == Set[Var]

        if initial_flow is not None:
            params['flags'] = cv.OPTFLOW_USE_INITIAL_FLOW
            
        start_time = time.time()
        flow = cv.calcOpticalFlowFarneback(PrvsFrame, CurrentFrame, initial_flow, **params)
        end_time = time.time()
        #print('calc time=',end_time-start_time)
        return flow
    
    def ApplyDisOpticalFlow(self,dis,frame_1,frame_2,initial_flow):
        flow = dis.calc(frame_1, frame_2, initial_flow)
        return flow

    def ApplyHornSchunckOpticalFlow(self,frame_1,frame_2,initial_flow):
        u,v = self.computeHS(frame_1, frame_2, initial_flow, alpha = 15, delta = 10**-8)
        flow = np.transpose(np.array([u, v]),axes=(1, 2, 0))
        return flow

    def computeHS(self,frame1, frame2, flow, alpha, delta):

        beforeImg = frame1.astype(np.float32)
        afterImg = frame2.astype(np.float32)

        # #reduce noise
        beforeImg  = cv.GaussianBlur(beforeImg, (1, 1), 0.62)
        afterImg = cv.GaussianBlur(afterImg, (1, 1), 0.62)

        # set up initial values
        r, c = beforeImg.shape

        if flow is None:
            u = np.zeros((r,c),dtype=np.float32)
            v = np.zeros((r,c),dtype=np.float32)
        else:
            u = flow[:,:,0].astype(np.float32)
            v = flow[:,:,1].astype(np.float32)

        fx, fy, ft = self.get_derivatives(beforeImg, afterImg)
        avg_kernel = np.array([[1 / 12, 1 / 6, 1 / 12],
                                [1 / 6, 0, 1 / 6],
                                [1 / 12, 1 / 6, 1 / 12]], np.float32)

        # avg_kernel = np.ones((5, 5), np.float32) / 25
        iter_counter = 0
        d = alpha ** 2 + fx ** 2 + fy ** 2
        start = time.time()
        while True:
            iter_counter += 1
            u_avg = cv.filter2D(u, -1, avg_kernel)
            v_avg = cv.filter2D(v, -1, avg_kernel)
            # p = cv.add(cv.add(cv.multiply(fx,u_avg), cv.multiply(fy, v_avg)),ft)

            p = fx * u_avg + fy * v_avg + ft

            prevu = u
            prevv = v

            u = u_avg - fx * (p / d)
            # u = cv.subtract(u_avg, cv.multiply(fx, cv.divide(p,d)))
            v = v_avg - fy * (p / d)
            # v = cv.subtract(v_avg, cv.multiply(fy, cv.divide(p, d)))

            diff = (cv.norm(u-prevu) + cv.norm(v-prevv))/(r * c)

            # if iter_counter % 50 == 0:
            #     print("iteration number:{} diff:{}".format(iter_counter, diff))
            #converges check (at most 300 iterations)
            if  diff < delta or iter_counter > 500:
                print("Final iteration number:{} diff:{}".format(iter_counter, diff))
                break
        print(f'Elapsed: {(time.time() - start)} secs')
        return [u, v]
    
    def get_derivatives(self,img1, img2):
        #derivative masks
        x_kernel = np.array([[-1, 1], [-1, 1]]) * 0.25
        y_kernel = np.array([[-1, -1], [1, 1]]) * 0.25
        t_kernel = np.ones((2, 2)) * 0.25

        # fx = cv.filter2D(img1, -1, x_kernel) + cv.filter2D(img2, -1, x_kernel)

        fx = cv.filter2D((img1 + img2) / 2, -1, x_kernel)
        fy = cv.filter2D((img1 + img2) / 2, -1, y_kernel)
        ft = cv.filter2D(img2 - img1, -1, t_kernel)
        return [fx,fy,ft]
