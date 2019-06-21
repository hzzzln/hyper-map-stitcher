import cv2
import imutils


def frame_generator(path, frames=10, width=477):
    vidcap = cv2.VideoCapture(path)
    success, image = vidcap.read()
    count = 0
    while success:
        if count % frames == 0:
            image = imutils.resize(image, width=width, inter=cv2.INTER_NEAREST)
            image = image[1:image.shape[0], 1:image.shape[1]]
            yield image
        success, image = vidcap.read()
        count += 1


