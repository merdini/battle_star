import cv2
import numpy as np
from params import cam_pos
from glare import remove_glare


def quantize_image(img, k):

    z = img.reshape((-1,3))
    # convert to np.float32
    z = np.float32(z)
    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret,label,center=cv2.kmeans(z, k,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))
    return res2



if __name__ == "__main__":
    img = cv2.imread(f'targets_up_{cam_pos}.jpg')
    img = remove_glare(img)
    for k in range(4, 9):
        res2 = quantize_image(img, k)

        cv2.imshow(f'k={k}',res2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
