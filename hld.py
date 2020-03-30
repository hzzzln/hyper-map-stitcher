from video_reader import frame_generator
from panorama import Stitcher
import cv2

infile = "in/2020-01-26 14-16-23.mkv"
outfile = "test.png"

stitcher = Stitcher()
images = frame_generator(infile, frames=10, width=600, image_crop=(126,938,4,1916))
result = stitcher.multistitch(images, manual=False, os="win")
cv2.imwrite(outfile, result)