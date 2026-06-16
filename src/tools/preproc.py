# Preprocess input data to make it ready for training.
import cv2
import numpy as np

from sys       import argv
from os        import walk, makedirs
from os.path   import join, exists
from numpy     import array, load, float64, float32, save
from json      import dumps
from shutil    import rmtree
from PIL       import Image, ImageDraw

from tools.estimator import EstimatePitchYawRoll
from tools.facelm    import FaceLandmarker


CMTX      = load('ccres/cam.npy')
DIST      = load('ccres/dist.npy')
NCAM      = load('ccres/ncam.npy')

# Taken from: https://gist.github.com/Asadullah-Dal17/fd71c31bac74ee84e6a31af50fa62961
LEFT_EYE   = [ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398 ]
RIGHT_EYE  = [  33,   7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246 ]
FACE       = [ 
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 
    150, 136, 172,  58, 132,  93, 234, 127, 162,  21,  54, 103,  67, 109
]
LEFT_IRIS  = 473
RIGHT_IRIS = 468
S          = (1920, 1080)
ER         = 5


def int_EstimatePose(w, h, lm, ncmtx) -> tuple[array, array]:
    FACE_REAL_WORLD = array([
        [285, 528, 200],
        [285, 371, 152],
        [197, 574, 128],
        [173, 425, 108],
        [360, 574, 128],
        [391, 425, 108]
    ], dtype=float64)
    faceImg = []
        
    for idx, l in enumerate(lm):
        if idx in [1, 9, 57, 130, 287, 359]:
            x, y = l.x * w, l.y * h
            faceImg.append([x, y])
            
    faceImg   = array(faceImg, dtype=float64)
    _, rv, tv = cv2.solvePnP(FACE_REAL_WORLD, faceImg, ncmtx, None)
            
    return rv, tv


def int_NormLm(lm, outer: tuple[float, float, float, float]) -> tuple[float, float]:
    l, t, r, b = outer

    return (lm.x - l) / (r - l), (lm.y - t) / (b - t)


def int_GetFaceBoundingBox(lm) -> tuple[float, float, float, float]:
    left   = min([lm[i].x for i in FACE])
    top    = min([lm[i].y for i in FACE])
    right  = max([lm[i].x for i in FACE])
    bottom = max([lm[i].y for i in FACE])

    return left, top, right, bottom


def int_GetEyeBoundingBoxes(lm) -> tuple[array, array]:
    MARGIN_X = 10.0 / S[0]
    MARGIN_Y = 10.0 / S[1]

    # (2) Get left bounding box.
    lleft   = max(0.0, min([lm[i].x for i in LEFT_EYE]) - MARGIN_X)
    ltop    = max(0.0, min([lm[i].y for i in LEFT_EYE]) - MARGIN_Y)
    lright  = min(1.0, max([lm[i].x for i in LEFT_EYE]) + MARGIN_X)
    lbottom = min(1.0, max([lm[i].y for i in LEFT_EYE]) + MARGIN_Y)

    # (2) Get right bounding box.
    rleft   = max(0.0, min([lm[i].x for i in RIGHT_EYE]) - MARGIN_X)
    rtop    = max(0.0, min([lm[i].y for i in RIGHT_EYE]) - MARGIN_Y)
    rright  = min(1.0, max([lm[i].x for i in RIGHT_EYE]) + MARGIN_X)
    rbottom = min(1.0, max([lm[i].y for i in RIGHT_EYE]) + MARGIN_Y)

    return [array([lleft, ltop, lright, lbottom]), array([rleft, rtop, rright, rbottom])]


def int_GetSortKey(n) -> tuple:
    _, _, r, i = n.split('_')
    i          = i.split('.')[0]

    return int(r), int(i)
    

def PreprocessImage_Simple(flm: FaceLandmarker, img, draw, norm=True) -> tuple[list[array], array, array, Image]:
    if isinstance(img, str):
        # (1) Load image.
        im = cv2.imread(img)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    elif isinstance(img, bytes):
        # Raw bytes.
        # Convert raw bytes to numpy array
        image_array = np.frombuffer(img, dtype=np.uint8)
        # Decode JPG bytes into OpenCV image
        im = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    else:
        print(f'error: Incorrect type.')

        raise
    if draw:
        drImg = Image.new('RGB', (1920, 1080), 'white')
        imgDr = ImageDraw.Draw(drImg)

    # (2.1) Undistort.
    im = cv2.undistort(im, CMTX, DIST, None, NCAM)
    
    # (3) Extract eyes and the landmarks we want.
    lm = flm.getFacialLandmarks(im)
    if lm.multi_face_landmarks is None:
        print(f'warning: Image does not contain a face. Skipping.')

        return None
    try:
        lm = lm.multi_face_landmarks[0]
        lm = lm.landmark
    except:
        print(f'warning: Image does not contain a face. Skipping.')

        return None
    
    # (4) Extract features.
    fb   = int_GetFaceBoundingBox(lm)
    l, r = int_GetEyeBoundingBoxes(lm)
    # Get yaw, pitch and roll.
    pitch, yaw, roll = EstimatePitchYawRoll(lm, im, CMTX, NCAM, DIST)
    pose             = array([pitch / 45.0, yaw / 45.0, roll / 45.0], dtype=float32).flatten()

    # (5) Convert to grayscale.
    im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)

    # (6) Normalize landmarks to face bounding box.
    lml = FACE + LEFT_EYE + RIGHT_EYE
    if draw:
        for k in lml:
            lMark = (lm[k].x * S[0], lm[k].y * S[1])
            imgDr.ellipse([(lMark[0] - ER, lMark[1] - ER), (lMark[0] + ER, lMark[1] + ER)], fill='purple')
    lms = [int_NormLm(lm[i], fb) if norm else (lm[i].x, lm[i].y) for i in lml]
    # Finally convert to array.
    lms = array(lms, dtype=float32).flatten()

    # https://theailearner.com/tag/cv2-getperspectivetransform/
    # Warp left eye to perspective.
    w, h           = S
    _l, _t, _r, _b = l
    pts1           = float32([[_l * w, _t * h], [_r * w, _t * h], [_l * w, _b * h], [_r * w, _b * h]])
    pts2           = float32([[0, 0], [120, 0], [0, 72], [120, 72]])
    T              = cv2.getPerspectiveTransform(pts1, pts2)
    leftEye        = cv2.warpPerspective(im, T, (120, 72))

    # Warp right eye to perspective.
    _l, _t, _r, _b = r
    pts1           = float32([[_l * w, _t * h], [_r * w, _t * h], [_l * w, _b * h], [_r * w, _b * h]])
    pts2           = float32([[0, 0], [120, 0], [0, 72], [120, 72]])
    T              = cv2.getPerspectiveTransform(pts1, pts2)
    rightEye       = cv2.warpPerspective(im, T, (120, 72))

    # return [rightEye, leftEye], lms, pose, drImg if draw else None
    return [cv2.equalizeHist(rightEye), cv2.equalizeHist(leftEye)], lms, pose, drImg if draw else None


"""
def PreprocessImage_LikeKURIC(flm: FaceLandmarker, imfile) -> list[array]:
    generic_3d_face_coordinates = np.array([
        [-45.0967681126441, -21.3128582097374, 21.3128582097374, 45.0967681126441, -26.2995769055718, 26.2995769055718],
        [-0.483773045049757, 0.483773045049757, 0.483773045049757, -0.483773045049757, 68.5950352778326, 68.5950352778326],
        [2.39702984214363, -2.39702984214363, -2.39702984214363, 2.39702984214363, -9.86076131526265 * (10 ** -32), -9.86076131526265 * (10 ** -32)],
    ])
    # Other generic face model. Needs 30-35 distance in 'z_scale' below
    # generic_3d_face_coordinates = np.array([
    #    [-4.445859, -1.856432,  1.856432,  4.445859, -2.456206,  2.456206,  0.000000,  0.000000,  0.000000],
    #    [ 2.663991,  2.585245,  2.585245,  2.663991, -4.342621, -4.342621, -1.126865, -3.406404, -9.403378],
    #    [ 3.173422,  3.757904,  3.757904,  3.173422,  4.283884,  4.283884,  7.475604,  5.979507,  4.264492],
    # ], dtype=np.float32)
    # Taken from the generic face model found in models/face/canonical_face_model.obj.
    generic_3d_face_coordinates_T = generic_3d_face_coordinates.T

    im = cv2.imread(imfile)
    im = cv2.resize(im, (1920, 1080))
    im = cv2.undistort(im, CMTX, DIST)

    lm = flm.getFacialLandmarks(im)
    if lm is None:
        print(f'warning: Image "{imfile}" does not contain a face. Skipping.')

        return None
    try:
        lm = lm.multi_face_landmarks[0].landmark
    except:
        print(f'warning: Image "{imfile}" does not contain a face. Skipping.')

        return None
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    h, w = im.shape[:2]

    def lm_to_xy(idx):
        return np.array([lm[idx].x * w, lm[idx].y * h], dtype=np.float32)

    # The commented out coordiates were taken from the generic face model found in models/face/canonical_face_model.obj.
    face_2d = np.array([
        lm_to_xy(33),     # line 34: v -4.445859 2.663991 3.173422
        lm_to_xy(133),    # line 134: v -1.856432 2.585245 3.757904
        lm_to_xy(362),    # line 363: v 1.856432 2.585245 3.757904
        lm_to_xy(263),    # line 264: v 4.445859 2.663991 3.173422
        lm_to_xy(61),     # line 62: v -2.456206 -4.342621 4.283884
        lm_to_xy(291),    # line 292: v 2.456206 -4.342621 4.283884
        # lm_to_xy(1),    # line 2: v 0.000000 -1.126865 7.475604
        # lm_to_xy(0),    # line 1: v 0.000000 -3.406404 5.979507
        # lm_to_xy(152)   # line 153: v 0.000000 -9.403378 4.264492
    ], dtype=np.float32)

    _, rot_vec, trans_vec = cv2.solvePnP(generic_3d_face_coordinates_T,
        face_2d,
        CMTX,
        DIST,
        flags=cv2.SOLVEPNP_EPNP
    )
    _, rot_vec, trans_vec = cv2.solvePnP(generic_3d_face_coordinates_T,
        face_2d,
        CMTX,
        DIST,
        rot_vec,
        trans_vec,
        True
    )

    head_translation = trans_vec.reshape((3, 1))
    head_rotation = cv2.Rodrigues(rot_vec)[0]
    face_landmarks_3d = np.dot(head_rotation, generic_3d_face_coordinates) + head_translation
    right_eye = 0.5 * (face_landmarks_3d[:, 0] + face_landmarks_3d[:, 1]).reshape((3, 1))
    left_eye = 0.5 * (face_landmarks_3d[:, 2] + face_landmarks_3d[:, 3]).reshape((3, 1))
    eyes = [right_eye, left_eye]
    processed_eyes = []

    for i, eye in enumerate(eyes):
        distance = np.linalg.norm(eye)
        z_scale = 300 / distance # 600 or 30 with the other generic face coords

        camera_norm = np.array([
            [960 * 1.05, 0, 120 / 2], # 60
            [0, 960 * 1.05, 72 / 2], # 36
            [0, 0, 1.0],
        ])
        scaling_matrix = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, z_scale],
        ])
        forward = (eye / distance).reshape(3)
        down = np.cross(forward, head_rotation[:, 0])  # Second arg. is head_rotation X
        down /= np.linalg.norm(down)
        right = np.cross(down, forward)
        right /= np.linalg.norm(right)
        rotation_matrix = np.c_[right, down, forward].T

        transformation_matrix = np.dot(
        np.dot(camera_norm, scaling_matrix),
        np.dot(rotation_matrix, np.linalg.inv(CMTX)))

        img_warped = cv2.warpPerspective(im, transformation_matrix, (120, 72)) # (60, 36)
        img_warped = cv2.equalizeHist(img_warped)

        processed_eyes.append(img_warped)

    return processed_eyes
"""


def Preprocess_OnlyFace(flm: FaceLandmarker, imfile, eq = False) -> array:
    im = cv2.imread(imfile)
    im = cv2.undistort(im, CMTX, DIST)

    lm = flm.getFacialLandmarks(im)
    if lm is None:
        print(f'warning: Image "{imfile}" does not contain a face. Skipping.')

        return None
    try:
        lm = lm.multi_face_landmarks[0].landmark
    except:
        print(f'warning: Image "{imfile}" does not contain a face. Skipping.')

        return None
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    l, t, r, b = int_GetFaceBoundingBox(lm)
    im = im[int(t*S[1]):int(b*S[1]), int(l*S[0]):int(r*S[0])]

    if eq:
        im = cv2.equalizeHist(im)

    return im


if __name__ == '__main__':
    src   = argv[1] # source directory
    dst   = argv[2] # destination directory
    kuric = '-k' in argv or '--kuric'  in argv # preprocess like KURIC et al. in "Democratizing Eye Tracking"
    mat   = '-m' in argv or '--matrix' in argv # Generate matrices and not images.
    fac   = '-f' in argv # Extract only face
    dr    = '-d' in argv # Draw landmarks to image (for debugging)
    norm  = '-n' in argv # Normalize landmarks to head bounding box
    sort  = '-s' in argv # Sort sequentially.
    if kuric:
        print('error: Preprocessing like the paper "Democratizing Eye-Tracking" is currently not supported.')

        exit(1)
    if not norm:
        print('info: Not normalizing face- and eye landmarks before saving.')

    # Clear destination directory.
    if exists(dst):
        rmtree(dst)
    makedirs(dst)

    # Initialize face landmarker.
    flm = FaceLandmarker()

    # Go through all files in source dir and process them.
    # Collect all files that we have to parse.
    i = 1
    img2Proc = []
    for r, d, files in walk(src):
        if sort:
            files = sorted(files, key=int_GetSortKey)

        for f in files:
            if f.endswith('.jpg'):
                _, s, reg, _ = f.split('_')

                img2Proc.append((s, reg, r + '/' + f))
                i += 1

    print(f'Collected {len(img2Proc)} files. Processing ...')
    
    # Preprocess.
    listing = {
        'nsess':    0,
        'ndata':    0,
        'sessions': {}
    }
    for j, f in zip([j for j in range(i)], img2Proc):
        # Extract tuple.
        s, r, n = f

        # Get eye crops.
        if not fac and kuric:
            #res = PreprocessImage_LikeKURIC(flm, n)

            #eyes = res
            pass
        elif not fac:
            res = PreprocessImage_Simple(flm, n, dr, norm)
        else:
            res = Preprocess_OnlyFace(flm, n)
        if res is None:
            continue
        if not fac and not kuric:
            eyes, lms, pose, lmImg = res

        # Write.
        if not fac and s not in listing['sessions']:
            listing['sessions'][s]  = []
            listing['nsess']       += 1

        if not fac:
            lname = f'{j}_{s}_{r}_l.npy'
            rname = f'{j}_{s}_{r}_r.npy'
            lmf   = f'{j}_{s}_{r}_lm.npy'
            pf    = f'{j}_{s}_{r}_p.npy'
            if mat:
                save(join(dst, lname), eyes[1])
                save(join(dst, rname), eyes[0])
            else:
                cv2.imwrite(join(dst, lname + '_img.jpg'), eyes[1])
                cv2.imwrite(join(dst, rname + '_img.jpg'), eyes[0])
            save(join(dst, lmf), lms)
            save(join(dst, pf), pose)
            if dr:
                lmImg.save(join(dst, f'{j}_{s}_{r}_lmimg.jpg'))

            listing['ndata'] += 1
            listing['sessions'][s].append([lname, rname, lmf, pf, int(r)])
        else:
            fname = join(dst, f'{j}_{s}_{r}_f_u.jpg')

            cv2.imwrite(fname, res)
        print(f'  [{j + 1}/{i}] Processed {n}.')

    # Write file with grouped pairs.
    with open(f'listing{"_nn" if not norm else ""}{"_sor" if sorted else ""}.json', 'w') as file:
        file.write(dumps(listing, indent=4))
            
        print(f'Wrote results to "{file.name}" in current directory.')

    exit(0)


