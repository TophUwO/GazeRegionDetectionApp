# The code in this file is based on https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html.
import cv2
import numpy as np

from sys     import argv, exit
from os      import listdir, makedirs
from os.path import exists


TCRIT      = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
CBDIMS     = (7, 5)
OBJP       = np.zeros((7*5,3), np.float32)
OBJP[:,:2] = np.mgrid[0:7,0:5].T.reshape(-1,2)
IMDIM      = (1920, 1080)

def CalibrateCamera(imgdir) -> None:
    # (0) Initialize result vectors.
    objPts = []
    imgPts = []

    # (1) Enumerate all files we will use for calibration.
    for iname in [x for x in listdir(imgdir)]:
        # (2) Read image as greyscale.
        image = cv2.imread(iname, 0)

        # (3) Find chessboard corners.
        ret, c = cv2.findChessboardCorners(image, CBDIMS, None)

        # (4) Refine the chessboard corners if they were found.
        if ret is True:
            objPts.append(OBJP)

            # Refine.
            rc = cv2.cornerSubPix(image, c, (11, 11), (-1, -1), TCRIT)
            imgPts.append(rc)

            # (5) Calculate camera and distortion matrices.
            r, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objPts, imgPts, image.shape[::-1], None, None)
            if r is True:
                # Calibration done. Refine the camera matrix based on the image size. Since our image size is always
                # 1920x1080, it is always the same. Hence, we can precompute it here.
                cmtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, IMDIM, 1, IMDIM)

                # Save the parameters.
                if not exists('ccres'):
                    makedirs('ccres')
                np.save('ccres/cam', mtx)
                np.save('ccres/dist', dist)
                np.save('ccres/ncam', cmtx)
                np.save('ccres/roi', roi)

                return
            

if __name__ == '__main__':
    # (1) Check parameter.
    try:
        _ = argv[1]
    except IndexError:
        print('error: This script needs the root directory of the images that are to be used for calibration. Aborting.')

        exit(1)

    # (2) Do calibration.
    CalibrateCamera(argv[1])
            

