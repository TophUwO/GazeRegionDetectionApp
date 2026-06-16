# Google FaceMesh-based landmarker module.
import cv2
import numpy as np
import mediapipe as mp

from typing import Any



class FaceLandmarker:
    def __init__(self):
        # Load mediapipe FaceLandmark model.
        self._det = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        

    def getFacialLandmarks(self, image: bytes | str | Any) -> any:
        if isinstance(image, bytes):
            # Image from HTTP request.
            arr = np.frombuffer(im, np.uint8)
            im  = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            im  = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        elif isinstance(image, str):
            im = cv2.imread(image)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        else:
            # OpenCV image.
            im = image

        return self._det.process(im)
    

