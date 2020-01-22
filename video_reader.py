import math
import cv2
#import imutils


def frame_generator(path, frames=10, width=477, image_crop=None):
    vidcap = cv2.VideoCapture(path)
    success, image = vidcap.read()
    count = 0
    while success:
        if count % frames == 0:
            if image_crop is not None:
                a, b, c, d = image_crop
                image = image[a:b, c:d]
            #image = imutils.resize(image, width=width, inter=cv2.INTER_NEAREST)
            factor = width / image.shape[1]
            dsize = (int(math.floor(image.shape[1]*factor)), int(math.floor(image.shape[0]*factor)))
            image = cv2.resize(image, dsize, interpolation=cv2.INTER_NEAREST)
            image = image[1:image.shape[0], 1:image.shape[1]]
            yield image
        success, image = vidcap.read()
        count += 1
