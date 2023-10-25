

import cv2,time
import numpy as np
import matplotlib.pyplot as plt


def create_corner_image(projector_dimension,center):
    #center = [x,y]

    img = np.zeros(projector_dimension,np.uint8)
    
    img[0:center[1],0:center[0]]=255
    img[center[1]:359,center[0]:639]=255

    img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR565)
    
    return img

def project_capture_and_save(my_prj, my_cam, index_to_save,img):
        my_prj.showImage(img)
        print("wait for proj")
        time.sleep(0.2)

        print("capture")
        my_cam.capture_next_flag = True
        while(my_cam.capture_next_flag):
            time.sleep(0.1)

        cv2.imwrite("./images/img_proj_"+"{0:05d}".format(index_to_save)+".jpg",my_cam.image_buffer)
        

def project_images(projector_pts):   
    
    #import in function if no developing on pi
    import WorkerFunctionsProjectorControl as WFPC
    from screeninfo import get_monitors
    import picamera2
    from libcamera import controls
    import fractions
    import io
    import Acquisition
    
    w = 320
    h = 240
    my_cam = Acquisition.AcquisitionCamera(w,h)

    my_cam.start()
    my_prj = WFPC.Projector()

    projector_dimension = my_prj.projector_dimension[0:2]

    index = 0
    img = create_corner_image(projector_dimension, [0,0])
    project_capture_and_save(my_prj,my_cam,index,img)
    index += 1
    img = create_corner_image(projector_dimension, [projector_dimension[1],0])
    project_capture_and_save(my_prj,my_cam,index,img)
    index += 1
    for pt in projector_pts:
            pt = np.int32(pt)
            img = create_corner_image(projector_dimension, [pt[0],pt[1]] )
            project_capture_and_save(my_prj,my_cam,index,img)
            index += 1            
    my_cam.stop()
    
    


def Estimate_homography(project_image_flag=False, extract_camera_pts_flag = False, display_flag=False):

    if project_image_flag:
        import Acquisition
        projector_dimension = [360,640]
        step = 80
        projector_pts = []
        for x in range(step,projector_dimension[1]-step,step):
            for y in range(step,projector_dimension[0]-step,step):
                projector_pts.append([x,y])
        projector_pts = np.array(projector_pts)
        np.savetxt("./images/projector_pts.txt",projector_pts)
        project_images(projector_pts)
    else:
        #load the points
        projector_pts = np.loadtxt("./images/projector_pts.txt")     

    if extract_camera_pts_flag:
        import ProcessImages as PI
        camera_pts = PI.process_images()       
        np.savetxt("./images/camera_pts.txt",camera_pts)
    else:
        camera_pts = np.loadtxt("./images/camera_pts.txt")



    H, inlier_mask = cv2.findHomography(camera_pts,projector_pts)
    camera_pts = np.concatenate((camera_pts,np.ones((camera_pts.shape[0],1))),axis=1)
    camera_pts_ = (H@camera_pts.T).T
    camera_pts_[:,0] /= camera_pts_[:,2]
    camera_pts_[:,1] /= camera_pts_[:,2]

    

    if display_flag:  
        print(H)
        v = camera_pts_[:,0:2]-projector_pts
        fig = plt.figure()
        plt.quiver(camera_pts_[:,0],camera_pts_[:,1],v[:,0],v[:,1])
        plt.show()

    return H