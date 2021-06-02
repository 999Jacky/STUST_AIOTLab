import numpy as np
import cv2
import glob
Dir = "C:\\Users\\pc1\\Desktop\\iimg"
images = glob.glob(Dir + '/*.jpg')

for imgs in images:
    image = cv2.imread(imgs)
    (B, G, R) = cv2.split(image)
    bb = B*0.75
    bb = bb.astype(np.uint8)
    merged = cv2.merge([bb, G, R])
    cv2.imwrite(imgs, merged)
print("done")
