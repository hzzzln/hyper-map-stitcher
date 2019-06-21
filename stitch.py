from panorama import Stitcher
from video_reader import frame_generator
import argparse
import cv2


ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="path to the source video")
ap.add_argument("-n", "--name", required=True, help="name of the file to which the stitched map is written")
ap.add_argument("-f", "--frames", required=False, help="Takes every Nth frame where N is this parameter. Default is 10", default=10)
ap.add_argument("-m", "--manual", required=False, help="manual fix mode, default to false", default=False)
ap.add_argument("-o", "--os", required=False, help="os. can be win or linux. determines keycodes for manual mode", default="linux")

args = vars(ap.parse_args())

stitcher = Stitcher()
images = frame_generator(args["video"], frames = int(args["frames"]))
result = stitcher.multistitch(images, manual=args["manual"], os=args["os"])
cv2.imshow("Result", result)
last_key = cv2.waitKeyEx(0)
if last_key == 13:
    filepath = args["name"]
    if filepath[-4:] != ".png":
        filepath = filepath+".png"
    cv2.imwrite(filepath, result)
