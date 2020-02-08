from video_reader import frame_generator
from panorama import Stitcher
import cv2

infile = "in/age.mkv"
outfile = "out/age.png"

stitcher = Stitcher()
images = frame_generator(infile, frames=10, width=600, image_crop=(50,900,0,1920))
result = stitcher.multistitch(images, manual=False, os="win")
cv2.imwrite(outfile, result)