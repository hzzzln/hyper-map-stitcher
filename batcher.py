import os
from panorama import Stitcher
from video_reader import frame_generator
import cv2
from threading import Thread
from queue import Queue
import sys

THREADS = 1

def one_stitch(queue):
    stitcher = Stitcher()
    while not queue.empty():
        filename, images = queue.get()
        print(f'Processing video {queue.maxsize-queue.qsize()} of {queue.maxsize}, filename {filename}', flush=True)
        result = stitcher.multistitch(images, manual=False, os="win")
        cv2.imwrite(filename, result)


if __name__ == "__main__":
    dirpath = sys.argv[1]
    videos = os.listdir(dirpath)
    frames = 30
    width = 1050
    image_crop = (5,1045,5,1915)
    #image_crop = (126,938,4,1916)
    #ui_cuts = [(39,99,39,315)]
    q = Queue(maxsize=len(videos))
    threads = []
    for video in videos:
        filename = f'{os.path.splitext(os.path.basename(video))[0]}.png'
        images = frame_generator(dirpath+video, frames=frames, width=width, image_crop=image_crop)
        q.put((filename, images))
    for _ in range(THREADS):
        t = Thread(None, one_stitch, args=(q,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    
    