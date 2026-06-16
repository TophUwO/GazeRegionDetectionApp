# Camera calibration.
# The code in this file is based on https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html.
import cv2
import numpy as np

from sys     import argv, exit
from os      import listdir, makedirs
from os.path import exists, join


TCRIT      = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
CBDIMS     = (7, 5)
OBJP       = np.zeros((7*5,3), np.float32)
OBJP[:,:2] = np.mgrid[0:7,0:5].T.reshape(-1,2)
IMDIM      = (1920, 1080)

def CalibrateCamera(imgdir, dbg) -> int:
    if dbg and not exists('ccdbg'):
        makedirs('ccdbg')
    print(f'info: Calibrating camera using images from "{imgdir}" ...')

    # (0) Initialize result vectors.
    objPts = []
    imgPts = []

    # (1) Enumerate all files we will use for calibration.
    for iname in [x for x in listdir(imgdir)]:
        # (2) Read image.
        # https://www.geeksforgeeks.org/python/python-opencv-cv2-imread-method/
        image = cv2.imread(join(imgdir, iname), cv2.IMREAD_GRAYSCALE if not dbg else cv2.IMREAD_COLOR)
        if image is None:
            continue
        # https://www.geeksforgeeks.org/python/image-resizing-using-opencv-python/
        image = cv2.resize(image, IMDIM)
        # https://www.geeksforgeeks.org/python/python-grayscaling-of-images-using-opencv/
        workIm = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if dbg else image

        # (3) Find chessboard corners.
        ret, c = cv2.findChessboardCorners(workIm, CBDIMS, None)

        # (4) Refine the chessboard corners if they were found.
        if ret is True:
            objPts.append(OBJP)

            # Refine.
            rc = cv2.cornerSubPix(workIm, c, (11, 11), (-1, -1), TCRIT)
            imgPts.append(rc)
            print(f'  info: Successfully extracted chessboard corners from image "{iname}".')

            # If we want to draw, we draw them. This is used for debugging only.
            if dbg:
                cv2.drawChessboardCorners(image, (7, 5), rc, ret)

                dbgName = join('ccdbg', 'dbg_' + iname)
                cv2.imwrite(dbgName, image)
                print(f'  info: Saved debug image under "{dbgName}".')
        else:
            print(f'  error: Failed to extract chessboard corners from image "{iname}".')

    # (INTERM) Check if we got enough points. We want at least 15 points for this work.
    if len(objPts) < 15:
        print(f'error: Not enough samples for calibration. Needs at least 15, but got {len(objPts)}. Aborting.')

        return 1

    # (5) Calculate camera and distortion matrices.
    _, mtx, dist, rv, tv = cv2.calibrateCamera(objPts, imgPts, workIm.shape[::-1], None, None)
    # Calibration done. Refine the camera matrix based on the image size. Since our image size is always
    # 1920x1080, we can precompute it here.
    ncmtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, IMDIM, 1, IMDIM)

    # Save the parameters.
    if not exists('ccres'):
        makedirs('ccres')
    np.save('ccres/cam', mtx)
    np.save('ccres/dist', dist)
    np.save('ccres/ncam', ncmtx)
    np.save('ccres/roi', roi)

    print('Calibration successful. Saved matrices.')

    # Calculate re-projection error. This is solely to check how good our estimated camera parameters are.
    mean_error = 0
    for i in range(len(objPts)):
        imgpoints2, _ = cv2.projectPoints(objPts[i], rv[i], tv[i], mtx, dist)

        error = cv2.norm(imgPts[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        mean_error += error

    print(f'Reprojection error: {mean_error/len(objPts)}')
    return 0
            

if __name__ == '__main__':
    # (1) Check parameter.
    try:
        _ = argv[1]
    except IndexError:
        print('error: This script needs the root directory of the images that are to be used for calibration. Aborting.')

        exit(1)

    # (2) Print matrices if they are there.
    if '-p' in argv or '--print' in argv:
        if not exists('ccres'):
            print('error: Could not find "ccres" directory. Aborting.')

            exit(1)

        # Print stuff.
        print(f'Camera Matrix:     {np.load("ccres/cam.npy")}')
        print(f'New Camera Matrix: {np.load("ccres/ncam.npy")}')
        print(f'Distortion Matrix: {np.load("ccres/dist.npy")}')
        print(f'ROI:               {np.load("ccres/roi.npy")}')

        mean_error = 0
        exit(0)

    # (3) Do calibration.
    exit(CalibrateCamera(argv[1], '-d' in argv or '--dbg' in argv))
            

