import math
import cv2
import numpy
from tqdm import tqdm
import time
#import imutils


def frame_generator(path, frames=10, width=477, image_crop=None, ui_cuts = []):
    vidcap = cv2.VideoCapture(path)
    max_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    count = 0
    pbar = tqdm(total=max_frames)
    success = vidcap.grab()
    while success:
        if count % frames == 0:
            success, image = vidcap.retrieve()
            time.sleep(0.01)
            if image_crop is not None:
                a, b, c, d = image_crop
                image = image[a:b, c:d]
            for (a,b,c,d) in ui_cuts:
                #print(image[a:b, c:d].shape)
                black = numpy.zeros((b-a, d-c, 3))
                image[a:b, c:d] = black
            #image = imutils.resize(image, width=width, inter=cv2.INTER_NEAREST)
            #factor = width / image.shape[1]
            #dsize = (int(math.floor(image.shape[1]*factor)), int(math.floor(image.shape[0]*factor)))
            #image = cv2.resize(image, dsize, interpolation=cv2.INTER_NEAREST)
            #image = image[0:image.shape[0], 0:image.shape[1]]
            #print(f'{int((count/max_frames)*100)}%')
            yield image
        success = vidcap.grab()
        count += 1
        pbar.update()

    pbar.close()
