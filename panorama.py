import numpy as np
import imutils
import cv2


class Stitcher:
    def __init__(self):
        # determine if we are using OpenCV v3.X
        self.isv3 = imutils.is_cv3(or_better=True)

    def multistitch(self, image_generator, ratio=0.75, reproj_thresh=4.0, manual=True, os="linux"):
        """
        Takes an iterable of image paths. Will try to match the Nth image to the N-1th image, stitches the images
        together based on the found match to build a big panorama from all images.
        Will continue until iterable has no more images or no match was found during one iteration.
        :param image_paths: Iterable of image paths
        :param ratio:
        :param reproj_thresh:
        :return: None if one iteration didn't find a match or all images have been stitched
        """

        # init result, iteration variables
        last_image = next(image_generator)
        result = last_image.copy()
        (last_kps, last_features) = self.detectAndDescribe(last_image)
        accumulated_vector = (0, 0)

        # iteration variable. start at 1 because first iteration checks images n and n-1
        i = 1
        for next_image in image_generator:
            (next_kps, next_features) = self.detectAndDescribe(next_image)

            M = self.matchKeypoints(next_kps, last_kps,
                                    next_features, last_features, ratio, reproj_thresh)

            if M is None:
                print("No Matches at i = " + str(i))
                return None

            (matches, H, status) = M

            # this stuff only works for isometric anyway, so we only respect the translation
            trans_x = int(H[0][2])
            trans_y = int(H[1][2])

            if manual:
                last_key = None
                while last_key != 13:
                    test_image = self.translate_and_merge((last_image, next_image), (trans_x, trans_y))
                    cv2.imshow("testimage", test_image)
                    last_key = cv2.waitKeyEx(0)
                    print(last_key)

                    if os == "win":
                        if last_key == 2490368: trans_y = trans_y + 1
                        if last_key == 2555904: trans_x = trans_x - 1
                        if last_key == 2621440: trans_y = trans_y - 1
                        if last_key == 2424832: trans_x = trans_x + 1
                    else: 
                        if last_key == 65361: trans_x = trans_x + 1
                        if last_key == 65362: trans_y = trans_y - 1
                        if last_key == 65363: trans_x = trans_x - 1
                        if last_key == 65364: trans_y = trans_y + 1


            # translation is only between images n and n-1 - we have to keep track of all translations up to here
            accumulated_vector = (accumulated_vector[0] + trans_x, accumulated_vector[1] + trans_y)

            result = self.translate_and_merge((result, next_image), accumulated_vector)

            # if the new image extended the canvas in negative x or y, we need discard the change in the total vector -
            # the change is already contained in the moved canvas origin
            if accumulated_vector[0] < 0:
                accumulated_vector = (0, accumulated_vector[1])
            if accumulated_vector[1] < 0:
                accumulated_vector = (accumulated_vector[0], 0)

            last_image = next_image
            (last_kps, last_features) = (next_kps, next_features)
            i = i + 1

        return result

    def stitch(self, images, ratio=0.75, reprojThresh=4.0,
               showMatches=True):
        # unpack the images, then detect keypoints and extract
        # local invariant descriptors from them
        (imageB, imageA) = images
        (kpsA, featuresA) = self.detectAndDescribe(imageA)
        (kpsB, featuresB) = self.detectAndDescribe(imageB)

        # match features between the two images
        M = self.matchKeypoints(kpsA, kpsB,
                                featuresA, featuresB, ratio, reprojThresh)

        # if the match is None, then there aren't enough matched
        # keypoints to create a panorama
        if M is None:
            print("no matches")
            return None

        # otherwise, apply a perspective warp to stitch the images
        # together
        (matches, H, status) = M
        x = int(round(H[0][2]))
        y = int(round(H[1][2]))
        result = self.translate_and_merge(images, (x,y))

        # check to see if the keypoint matches should be visualized
        if showMatches:
            vis = self.drawMatches(imageA, imageB, kpsA, kpsB, matches,
                                   status)

            # return a tuple of the stitched image and the
            # visualization
            return (result, vis)

        # return the stitched image
        return result

    def translate_and_merge(self, images, vector):
        """
        Takes two images as a tuple and a (x,y) translation vector.
        Expands and translates the second image, then pastes the
        first into the second. Respects special cases with negative
        translation values."""

        (imageA, imageB) = images
        (x, y) = vector

        inc_y, inc_x = (0, 0)

        if y < 0:
            inc_y = abs(y)
        if x < 0:
            inc_x = abs(x)
        if imageB.shape[0] + y > imageA.shape[0]:
            inc_y = imageB.shape[0] + y - imageA.shape[0]
        if imageB.shape[1] + x > imageA.shape[1]:
            inc_x = imageB.shape[1] + x - imageA.shape[1]

        result = np.zeros((imageA.shape[0] + inc_y, imageA.shape[1] + inc_x, 3), np.uint8)

        if x < 0 and y < 0:
            x = abs(x)
            y = abs(y)
            result[y:imageA.shape[0] + y, x:imageA.shape[1] + x] = imageA
            result[0:imageB.shape[0], 0:imageB.shape[1]] = imageB
            return result
        elif x < 0 <= y:
            x = abs(x)
            result[0:imageA.shape[0], x:imageA.shape[1] + x] = imageA
            result[y:imageB.shape[0] + y, 0:imageB.shape[1]] = imageB
            return result
        elif x >= 0 > y:
            y = abs(y)
            result[y:imageA.shape[0] + y, 0:imageA.shape[1]] = imageA
            result[0:imageB.shape[0], x:imageB.shape[1] + x] = imageB
            return result
        else:
            result[0:imageA.shape[0], 0:imageA.shape[1]] = imageA
            result[y:imageB.shape[0] + y, x:imageB.shape[1] + x] = imageB
            return result

    def detectAndDescribe(self, image):
        # convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # check to see if we are using OpenCV 3.X
        if self.isv3:
            # detect and extract features from the image
            descriptor = cv2.ORB_create(edgeThreshold=0, nfeatures=10000, scoreType=cv2.ORB_FAST_SCORE)
            #descriptor = cv2.AKAZE_create(threshold=0)
            (kps, features) = descriptor.detectAndCompute(image, None)

        # otherwise, we are using OpenCV 2.4.X
        else:
            # detect keypoints in the image
            detector = cv2.FeatureDetector_create("SIFT")
            kps = detector.detect(gray)

            # extract features from the image
            extractor = cv2.DescriptorExtractor_create("SIFT")
            (kps, features) = extractor.compute(gray, kps)

        # convert the keypoints from KeyPoint objects to NumPy
        # arrays
        kps = np.float32([kp.pt for kp in kps])

        # return a tuple of keypoints and features
        return (kps, features)

    def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB,
                       ratio, reprojThresh):
        # compute the raw matches and initialize the list of actual
        # matches
        matcher = cv2.DescriptorMatcher_create("BruteForce")
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
        matches = []

        # loop over the raw matches
        for m in rawMatches:
            # ensure the distance is within a certain ratio of each
            # other (i.e. Lowe's ratio test)
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                matches.append((m[0].trainIdx, m[0].queryIdx))

        # computing a homography requires at least 4 matches
        if len(matches) > 4:
            # construct the two sets of points
            ptsA = np.float32([kpsA[i] for (_, i) in matches])
            ptsB = np.float32([kpsB[i] for (i, _) in matches])

            # compute the homography between the two sets of points
            (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
                                             reprojThresh)

            # return the matches along with the homograpy matrix
            # and status of each matched point
            return (matches, H, status)

        # otherwise, no homograpy could be computed
        return None

    def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
        # initialize the output visualization image
        (hA, wA) = imageA.shape[:2]
        (hB, wB) = imageB.shape[:2]
        vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
        vis[0:hA, 0:wA] = imageA
        vis[0:hB, wA:] = imageB

        # loop over the matches
        for ((trainIdx, queryIdx), s) in zip(matches, status):
            # only process the match if the keypoint was successfully
            # matched
            if s == 1:
                # draw the match
                ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
                ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
                cv2.line(vis, ptA, ptB, (0, 255, 0), 1)

        # return the visualization
        return vis