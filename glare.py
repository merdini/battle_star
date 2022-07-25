import cv2
import numpy as np
import time

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import k_means
from params import cam_pos


def remove_glare2(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = ((img_hsv > np.array([0, 0, 230])).astype(np.float32) + (img_hsv > np.array([0, 0, 230])).astype(np.float32) * (-0.5) + 0.5)
    img_partly_darken = cv2.cvtColor(mask * img_hsv, cv2.COLOR_HSV2BGR)
    plt.imshow(cv2.cvtColor(img_partly_darken, cv2.COLOR_BGR2RGB))
    plt.show()

    cv2.imwrite("t.png", img_partly_darken)
    # Save the img now, and ... Surprise! You can feel the mystery:
    plt.imshow(cv2.cvtColor(cv2.imread("t.png"), cv2.COLOR_BGR2RGB))
    plt.show()

    # Then, you can just pick out the green ones:
    green_mask = img[:, :, 1] > img[:, :, 2]    # value of green channel > that of red channel
    # Here is a trick, I use color space convertion to boardcast one channel to three channels
    green_mask = (green_mask.astype(np.uint8)) * 255
    green_mask = cv2.cvtColor(green_mask, cv2.COLOR_GRAY2BGR)
    green3_mask = (green_mask > 0).astype(np.uint8) * 255
    img_green = cv2.bitwise_and(green3_mask, img)
    plt.imshow(cv2.cvtColor(img_green, cv2.COLOR_BGR2RGB))
    plt.show()

    # Back to the original img's colors:
    ret, thr = cv2.threshold(cv2.cvtColor(img_green, cv2.COLOR_BGR2GRAY), 10, 255, cv2.THRESH_BINARY)
    blue_mask = (cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR) > 0).astype(np.uint8) * 255
    kernel_open =cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel_open)
    yellow_mask = 255 - blue_mask

    # use k-means to get the two main colors -- blue and yellow
    pixels = img
    pixels = pixels.reshape(pixels.shape[0] * pixels.shape[1], 3)
    [centroids, labels, inertia] = k_means(pixels, 2)
    centroids = np.array(sorted(centroids.astype(np.uint8).tolist(), key=lambda x: x[0]))       # B channel
    blue_centroid = centroids[1]
    yellow_centroid = centroids[0]
    blue_ones = cv2.bitwise_and(blue_mask, centroids[1])
    yellow_ones = cv2.bitwise_and(yellow_mask, centroids[0])
    plt.imshow(cv2.cvtColor(cv2.add(blue_ones, yellow_ones), cv2.COLOR_BGR2RGB))
    plt.show()

def remove_glare(img):
    clahefilter = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16,16))

    while True:
        t1 = time.time() 
        img = img.copy()

        ## crop if required 
        #FACE
        # x,y,h,w = 550,250,400,300
        # img = img[y:y+h, x:x+w]

        #NORMAL
        # convert to gray
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # grayimg = gray


        GLARE_MIN = np.array([0, 0, 50],np.uint8)
        GLARE_MAX = np.array([0, 0, 225],np.uint8)

        hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

        #HSV
        frame_threshed = cv2.inRange(hsv_img, GLARE_MIN, GLARE_MAX)
        #INPAINT + HSV
        result = cv2.inpaint(img, frame_threshed, 0.1, cv2.INPAINT_TELEA) 
        return result


        # #INPAINT
        # mask1 = cv2.threshold(grayimg , 220, 255, cv2.THRESH_BINARY)[1]
        # result1 = cv2.inpaint(img, mask1, 0.1, cv2.INPAINT_TELEA) 



        # #CLAHE
        # claheCorrecttedFrame = clahefilter.apply(grayimg)

        # #COLOR 
        # lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        # lab_planes = list(cv2.split(lab))
        # clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
        # lab_planes[0] = clahe.apply(lab_planes[0])
        # lab = cv2.merge(lab_planes)
        # clahe_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


        


        #INPAINT + CLAHE
        # grayimg1 = cv2.cvtColor(clahe_bgr, cv2.COLOR_BGR2GRAY)
        # mask2 = cv2.threshold(grayimg1 , 220, 255, cv2.THRESH_BINARY)[1]
        # result2 = cv2.inpaint(img, mask2, 0.1, cv2.INPAINT_TELEA) 



        # #HSV+ INPAINT + CLAHE
        # lab1 = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
        # lab_planes1 = list(cv2.split(lab1))
        # clahe1 = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
        # lab_planes1[0] = clahe1.apply(lab_planes1[0])
        # lab1 = cv2.merge(lab_planes1)
        # clahe_bgr1 = cv2.cvtColor(lab1, cv2.COLOR_LAB2BGR)




        # # fps = 1./(time.time()-t1)
        # # cv2.putText(clahe_bgr1    , "FPS: {:.2f}".format(fps), (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255))    

        # # display it
        # cv2.imshow("GRAY", gray)
        # cv2.imwrite("gray.png", gray)
        # # cv2.imshow("HSV", frame_threshed)
        # # cv2.imwrite("hsv.png", frame_threshed)
        # cv2.imshow("CLAHE", clahe_bgr)
        # cv2.imwrite("clahe_bgr.png", clahe_bgr)
        # # cv2.imshow("LAB", lab)
        # # cv2.imwrite("lab.png", lab)
        # cv2.imshow("HSV + INPAINT", result)
        # cv2.imwrite("result.png", result)
        # # cv2.imshow("INPAINT", result1)
        # # cv2.imwrite("result1.png", result1)
        # # cv2.imshow("CLAHE + INPAINT", result2) 
        # # cv2.imwrite("result2.png", result2) 
        # cv2.imshow("HSV + INPAINT + CLAHE   ", clahe_bgr1)
        # cv2.imwrite("clahe_bgr1.png", clahe_bgr1)

        # # Break with esc key
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break


    cv2.destroyAllWindows()

if __name__ == "__main__":
    img = cv2.imread(f'targets_up_{cam_pos}.jpg')
    remove_glare(img)