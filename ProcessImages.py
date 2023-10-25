import cv2
import numpy as np
import matplotlib.pyplot as plt


#https://github.com/intellar/ASN
import ASN_detector as ASN


def process_images():
    DEBUG_FLAG=0
    

    index = 0
    imgW = cv2.imread("./images/img_proj_"+"{0:05d}".format(index)+".jpg", cv2.IMREAD_GRAYSCALE)
    index += 1


    imgB = cv2.imread("./images/img_proj_"+"{0:05d}".format(index)+".jpg", cv2.IMREAD_GRAYSCALE)
    index += 1

    imgW = np.int32(imgW)
    imgB = np.int32(imgB)

    #the corner of interest in inside the white projected square, so covering all "1" value pixel in binary_projection. to avoid boundary corner, we will check in the corner neighboorhood
    binary_projection = (imgW-imgB)>50

    observed_pts = []

    

    for index in range(index,20):
        print("processing "+str(index))
        
        img = cv2.imread("./images/img_proj_"+"{0:05d}".format(index)+".jpg", cv2.IMREAD_GRAYSCALE)
        
        index += 1

        b = (np.int32(img)-imgB)>50
        b = np.uint8(b)

        pts_, accumulateur, convergence_regions = ASN.ASN_detector(img,config_integration_for_solution_size=40)
        
        
        pt = None
        half_window_size = 10
        for p in pts_:
            #is inside binary_projection
            p_ = np.int32(p)
            #check if inside image
            if 0<p_[1]-half_window_size and  p_[1]+half_window_size+1<binary_projection.shape[0] and 0<p_[0]-half_window_size and p_[0]+half_window_size+1<binary_projection.shape[1]:
                region = binary_projection[p_[1]-half_window_size:p_[1]+half_window_size+1, p_[0]-half_window_size:p_[0]+half_window_size+1]
                if np.all(region[:]):
                    # what if there is more than one?
                    if pt != None:
                        raise Exception("problem, more than one corner meet filter value. check why, probably background to strong, too much ambiant light")
                    pt = p
        
        observed_pts.append(pt)


        if DEBUG_FLAG==1:
            cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
            cimg[:,:,0] += np.array(accumulateur,dtype=np.uint8)
            cimg[:,:,1] += np.array(convergence_regions*0.2,dtype=np.uint8)
            

            fig = plt.figure()    
            plt.imshow(cimg)
            plt.plot(pt[0],pt[1],'g+', markersize=20, markeredgewidth=4)


    observed_pts = np.array(observed_pts)
    print(observed_pts)

    if DEBUG_FLAG:
        plt.show()

    return observed_pts

