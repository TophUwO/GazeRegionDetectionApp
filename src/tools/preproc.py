import cv2

from os                     import getenv
from numpy                  import array, load
from mediapipe.tasks        import python
from mediapipe.tasks.python import vision


det = None
if getenv('DATACOLL_PREPROC', None) is not None:
    bopt = python.BaseOptions('models/face_landmarker.task')
    opt  = vision.FaceLandmarkerOptions(base_options=bopt, num_faces=1)
    det  = vision.FaceLandmarker.create_from_options(opt)


def int_ExtractFeatures(im, lm) -> tuple[array, array, list[tuple[float, float]]]:
    # https://gist.github.com/Asadullah-Dal17/fd71c31bac74ee84e6a31af50fa62961
    LEFT_EYE  = [ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398 ]
    RIGHT_EYE = [  33,   7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246 ]
    FACE      = [ 
        10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 
        150, 136, 172,  58, 132,  93, 234, 127, 162,  21,  54, 103,  67, 109
    ]

    # https://opencv.org/cropping-an-image-using-opencv/
    IMAGE_DIMS = (1920, 1080)




def PreprocessImage(img) -> None:
    if det is None:
        print('warning: No FaceMesh model loaded. Cannot preprocess image.')

        return
    
    # (1) Load image.
    im = cv2.imread(img)

    # (2.1) Undistort.
    cmtx = load('ccres/cam.npy')
    dist = load('ccres/dist.npy')
    ncam = load('ccres/ncam.npy')
    roi  = load('ccres/roi.npy')
    im   = cv2.undistort(im, cmtx, dist, None, ncam)
    # (2.2) Crop.
    x, y, w, h = roi
    im   = im[y:y+h, x:x+w]
    
    # (3) Extract eyes and the landmarks we want.
    lm = None
    try:
        lm = det.detect(im).face_landmarks[0]
    except:
        print(f'warning: Image "{img}" does not contain a face. Skipping.')

        return

    l, r, lms = int_ExtractFeatures(im, lm)

    # (4) Greyscale conversion.
    # https://www.geeksforgeeks.org/python/python-grayscaling-of-images-using-opencv/

    # (5) Normalize contrast.
    # https://www.geeksforgeeks.org/python/histograms-equalization-opencv/

    # (6) Save.

