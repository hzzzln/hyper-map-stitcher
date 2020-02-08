from video_reader import frame_generator
from panorama import Stitcher
import cv2

infile = "in/hell2.mkv"
outfile = "out/hell2.png"

stitcher = Stitcher()
images = frame_generator(infile, frames=10, width=600, image_crop=(186,694,5,1905))
result = stitcher.multistitch(images, manual=False, os="win")
cv2.imwrite(outfile, result)