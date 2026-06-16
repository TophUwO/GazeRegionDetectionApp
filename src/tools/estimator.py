# This script is based on the one found in here (estimator.py): https://github.com/shenasa-ai/head-pose-estimation
# All I did was modify the input (no longer webcam but a static image) and add a return value to the function
# corresponding to the yaw/pitch angles that I want.
# This has also helped a bit in understanding: https://medium.com/@susanne.thierfelder/head-pose-estimation-with-mediapipe-and-opencv-in-javascript-c87980df3acb
import math

import cv2
import numpy as np

from tools.facelm import FaceLandmarker


#mp_face_mesh = mp.solutions.face_mesh
#face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def rotation_matrix_to_angles(rotation_matrix):
    """
    Calculate Euler angles from rotation matrix.
    :param rotation_matrix: A 3*3 matrix with the following structure
    [Cosz*Cosy  Cosz*Siny*Sinx - Sinz*Cosx  Cosz*Siny*Cosx + Sinz*Sinx]
    [Sinz*Cosy  Sinz*Siny*Sinx + Sinz*Cosx  Sinz*Siny*Cosx - Cosz*Sinx]
    [  -Siny             CosySinx                   Cosy*Cosx         ]
    :return: Angles in degrees for each axis
    """
    x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
    y = math.atan2(-rotation_matrix[2, 0], math.sqrt(rotation_matrix[0, 0] ** 2 +
                                                     rotation_matrix[1, 0] ** 2))
    z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    return np.array([x, y, z]) * 180. / math.pi



def EstimatePitchYawRoll(lms, imfile, cmtx, ncmtx, dist, roi = None) -> tuple[float, float]:
    if isinstance(imfile, str):
        # Load and undistort.
        image = cv2.imread(imfile)
        image = cv2.undistort(image, cmtx, dist, None, ncmtx)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        im    = image
    else:
        # OpenCV image.
        im = imfile

    face_coordination_in_real_world = np.array([
        [285, 528, 200],
        [285, 371, 152],
        [197, 574, 128],
        [173, 425, 108],
        [360, 574, 128],
        [391, 425, 108]
    ], dtype=np.float64)

    h, w, _ = im.shape
    face_coordination_in_image = []

    yaw   = 0.0
    pitch = 0.0
    roll  = 0.0
    for idx, lm in enumerate(lms):
        if idx in [1, 9, 57, 130, 287, 359]:
            x, y = lm.x * w, lm.y * h
            face_coordination_in_image.append([x, y])
    face_coordination_in_image = np.array(face_coordination_in_image, dtype=np.float64)

    _, rotation_vec, _ = cv2.solvePnP(face_coordination_in_real_world, face_coordination_in_image, ncmtx, None)
    rotation_matrix, _ = cv2.Rodrigues(rotation_vec)

    result = rotation_matrix_to_angles(rotation_matrix)
    pitch = result[0]
    yaw   = result[1]
    roll  = result[2]

    return pitch, yaw, roll


