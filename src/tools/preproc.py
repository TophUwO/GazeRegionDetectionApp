import cv2
import numpy as np

from sys       import argv
from os        import walk, makedirs
from os.path   import join, exists
from numpy     import array, load, float64, float32, save
from mediapipe import solutions
from json      import dumps
from shutil    import rmtree

# Get the model.
FACE_MESH = solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
CMTX      = load('ccres/cam.npy')
DIST      = load('ccres/dist.npy')
NCAM      = load('ccres/ncam.npy')

# Taken from: https://gist.github.com/Asadullah-Dal17/fd71c31bac74ee84e6a31af50fa62961
LEFT_EYE  = [ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398 ]
RIGHT_EYE = [  33,   7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246 ]
FACE      = [ 
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 
    150, 136, 172,  58, 132,  93, 234, 127, 162,  21,  54, 103,  67, 109
]


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


def int_GetEyeBoundingBoxes(lm, size: tuple[int, int]) -> tuple[array, array]:
    MARGIN = 10

    # (2) Get left bounding box.
    lleft   = int(max(0, min([lm[i].x * size[0] for i in LEFT_EYE])       - MARGIN))
    ltop    = int(max(0, min([lm[i].y * size[1] for i in LEFT_EYE])       - MARGIN))
    lright  = int(min(size[0], max([lm[i].x * size[0] for i in LEFT_EYE]) + MARGIN))
    lbottom = int(min(size[1], max([lm[i].y * size[1] for i in LEFT_EYE]) + MARGIN))

    # (2) Get right bounding box.
    rleft   = int(max(0, min([lm[i].x * size[0] for i in RIGHT_EYE])       - MARGIN))
    rtop    = int(max(0, min([lm[i].y * size[1] for i in RIGHT_EYE])       - MARGIN))
    rright  = int(min(size[0], max([lm[i].x * size[0] for i in RIGHT_EYE]) + MARGIN))
    rbottom = int(min(size[1], max([lm[i].y * size[1] for i in RIGHT_EYE]) + MARGIN))

    return [array([lleft, ltop, lright, lbottom]), array([rleft, rtop, rright, rbottom])]
    

def PreprocessImage_Simple(img) -> list[array]:
    # (1) Load image.
    im = cv2.imread(img)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

    # (2.1) Undistort.
    im = cv2.undistort(im, CMTX, DIST, None, NCAM)
    
    # (3) Extract eyes and the landmarks we want.
    lm = FACE_MESH.process(im)
    if lm.multi_face_landmarks is None:
        print(f'warning: Image "{img}" does not contain a face. Skipping.')

        return None
    lm = lm.multi_face_landmarks[0]

    # (4) Convert to grayscale.
    im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
    # (5) Extract features.
    l, r = int_GetEyeBoundingBoxes(lm.landmark, (1920, 1080))

    _l, _t, _r, _b = l
    pts1 = float32([[_l, _t], [_r, _t], [_l, _b], [_r, _b]])
    pts2 = float32([[0,0],[120,0],[0,72],[120,72]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    leftEye = cv2.warpPerspective(im, M, (120, 72))

    _l, _t, _r, _b = r
    pts1 = float32([[_l, _t], [_r, _t], [_l, _b], [_r, _b]])
    pts2 = float32([[0,0],[120,0],[0,72],[120,72]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    rightEye = cv2.warpPerspective(im, M, (120, 72))

    return [cv2.equalizeHist(rightEye), cv2.equalizeHist(leftEye)]


def PreprocessImage_LikeMPIIGaze(imfile) -> list[array]:
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

    generic_3d_face_coordinates_T = generic_3d_face_coordinates.T

    # [33] = v -5.062006 1.934418 2.776093

    im = cv2.imread(imfile)
    im = cv2.resize(im, (1920, 1080))
    im = cv2.undistort(im, CMTX, DIST)

    lm = FACE_MESH.process(im)
    if lm is None:
        print(f'warning: Image "{imfile}" does not contain a face. Skipping.')

        return None
    lm = lm.multi_face_landmarks[0].landmark
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    h, w = im.shape[:2]

    def lm_to_xy(idx):
        return np.array([lm[idx].x * w, lm[idx].y * h], dtype=np.float32)

    face_2d = np.array([
        lm_to_xy(33),     # line 34: v -4.445859 2.663991 3.173422
        lm_to_xy(133),    # line 134: v -1.856432 2.585245 3.757904
        lm_to_xy(362),    # line 363: v 1.856432 2.585245 3.757904
        lm_to_xy(263),    # line 264: v 4.445859 2.663991 3.173422
        lm_to_xy(61),     # line 62: v -2.456206 -4.342621 4.283884
        lm_to_xy(291),    # line 292: v 2.456206 -4.342621 4.283884
        # lm_to_xy(1),      # line 2: v 0.000000 -1.126865 7.475604
        # lm_to_xy(0),      # line 1: v 0.000000 -3.406404 5.979507
        # lm_to_xy(152)     # line 153: v 0.000000 -9.403378 4.264492
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
    eye_screen_distance = np.mean(np.array(np.linalg.norm(eyes[0]), np.linalg.norm(eyes[1])))

    for i, eye in enumerate(eyes):
        # print(f'{i}')
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


if __name__ == '__main__':
    src = argv[1]
    dst = argv[2]
    mpiigaze = '-ii' in argv or '--mpiigaze' in argv
    mat      = '-m'  in argv or '--matrix'   in argv

    # Clear destination directory.
    if exists(dst):
        rmtree(dst)
    makedirs(dst)

    # Go through all files in source dir and process them.
    # Collect all files that we have to parse.
    i = 1
    img2Proc = []
    for r, d, files in walk(src):
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
        if mpiigaze:
            eyes = PreprocessImage_LikeMPIIGaze(n)
        else:
            eyes = PreprocessImage_Simple(n)
        if not eyes:
            continue

        # Write.
        if s not in listing['sessions']:
            listing['sessions'][s]  = []
            listing['nsess']       += 1

        lname = f'{j}_{s}_{r}_l.npy'
        rname = f'{j}_{s}_{r}_r.npy'
        if mat:
            save(join(dst, lname), eyes[1])
            save(join(dst, rname), eyes[0])
        else:
            cv2.imwrite(join(dst, lname + '_img.jpg'), eyes[1])
            cv2.imwrite(join(dst, rname + '_img.jpg'), eyes[0])

        listing['ndata'] += 1
        listing['sessions'][s].append([lname, rname, int(r)])
        print(f'  [{j + 1}/{i}] Processed {n}.')

    # Write file with grouped pairs.
    with open('listing.json', 'w') as file:
        file.write(dumps(listing))
            
        print('Wrote results to "listing.json" in current directory.')

    exit(0)


