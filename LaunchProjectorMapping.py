
import Acquisition
import numpy as np
import AcquisitionComputationHomograpy as AcqH
import WorkerFunctionsProjectorControl as WFPC
import time
import cv2


def draw_line(img,p0,p1):
    x0 = int(p0[0])
    y0 = int(p0[1])
    x1 = int(p1[0])
    y1 = int(p1[1])
    
    rgb = np.array(np.random.randint(0,255,3))
    color = ( int (rgb [ 0 ]), int (rgb [ 1 ]), int (rgb [ 2 ])) 
    #cv2.line(img,(x0,y0),(x1,y1),(255,255,255),2)
    cv2.line(img,(x0,y0),(x1,y1),tuple(color),2)

def draw_line_segments(img, pts):
    #print(pts)
    for i in range(len(pts)-1):
        if pts[i][2] > 0:
            if np.abs(pts[i][2]-pts[i+1][2])<5:
                draw_line(img,pts[i],pts[i+1])
                pts[i][2]= -1

def create_canvas_image(w,h):
    img_to_project = np.zeros(projector_dimension,np.uint8)
    img_to_project[0,:]=255
    img_to_project[359,:]=255
    img_to_project[:,0]=255
    img_to_project[:,639]=255
    img_to_project[0:12,0:12] = 255
    img_to_project = cv2.cvtColor(img_to_project,cv2.COLOR_GRAY2BGR565)
    return img_to_project




w = 320
h = 240

H = AcqH.Estimate_homography(project_image_flag=False,extract_camera_pts_flag=False,display_flag=False)



my_cam = Acquisition.AcquisitionCamera(w,h)
my_cam.set_exposure_time_ms(0.5)
my_cam.start()

my_prj = WFPC.Projector()
projector_dimension = my_prj.projector_dimension[0:2]

# Set up the detector with default parameters.
fast = cv2.FastFeatureDetector_create()



pts = []

img_to_project = create_canvas_image(w,h)
my_prj.showImage(img_to_project)
print("wait for proj")
time.sleep(0.5)


index=0
while(1):
    
    index += 1
    
    if 1:
        my_cam.capture_next_flag = True
        while(my_cam.capture_next_flag):
            time.sleep(0.01)
        img = my_cam.image_buffer
    else:
        img = my_cam.capture_array()

    #quick extraction of spot    
    kp = fast.detect(img,None)    

    if len(kp)>0:
        p = np.array([kp[0].pt[0],kp[0].pt[1], 1])       
        #transfer to projector
        p  = (H@p.T).T
        p /= p[2]
        p[2] = index
        pts.append(p)

        if p[0]<12 and p[1]<12:
            img_to_project = create_canvas_image(w,h)            
            pts = []

    draw_line_segments(img_to_project,pts)
    my_prj.showImage(img_to_project)
    
my_cam.stop()