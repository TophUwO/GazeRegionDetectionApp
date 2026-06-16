# Facial recognition and eye checking during data collection.
from __future__             import annotations

from io                     import BytesIO
from PIL                    import Image as PILImage
from numpy                  import asarray, linalg, array
from mediapipe              import Image as MPImage, ImageFormat
from mediapipe.tasks        import python
from mediapipe.tasks.python import vision
from enum                   import Enum
from dataclasses            import dataclass
from threading              import Lock
from concurrent.futures     import ThreadPoolExecutor

# TODO: Use face landmarker.
from dlmdl import DownloadFaceLandmarkerModelBundle
from numpy import load


# Get the camera parameters for undistortion.
CMTX = load('ccres/cam.npy')
DIST = load('ccres/dist.npy')
NCAM = load('ccres/ncam.npy')


class EntityId(Enum):
    FACE  = 0,
    LEFT  = 1,
    RIGHT = 2


@dataclass
class BoundingBox:
    """represents a bounding box"""

    left:   float = 0
    top:    float = 0
    right:  float = 0
    bottom: float = 0


    @staticmethod
    def Null() -> BoundingBox:
        return BoundingBox(float('inf'), float('inf'), float('-inf'), float('-inf'))
    

    def __iter__(self):
        yield self.left
        yield self.top
        yield self.right
        yield self.bottom

    def tuple(self):
        return (self.left, self.top, self.right, self.bottom)

    def scale(self, size: tuple[float, float]) -> BoundingBox:
        w, h = size

        self.left   *= w
        self.top    *= h
        self.right  *= w
        self.bottom *= h

        return self
    
    def pad(self, extra: BoundingBox | tuple[float, float, float, float]) -> BoundingBox:
        l, t, r, b = extra

        self.left   = max(0,    self.left   - l)
        self.top    = max(0,    self.top    - t)
        self.right  = min(1280, self.right  + r)
        self.bottom = min(720,  self.bottom + b)

        return self
    

class LabelGenerator:
    """provides a label generator function; the labels used here are unused in the actual preprocessing, evaluation and training process"""

    @staticmethod
    def GenerateLabel(rawimg, code, index, region, x, y, ts) -> str:
        return f'''
            {{
                "image":  "{rawimg}",
                "code":   "{code}",
                "index":  {index},
                "region": {region},
                "x":      {x},
                "y":      {y},
                "time":   {ts}
            }}
        '''

class FaceParser:
    """provides functionality dedicated to do basic real-time face parsing; note that this is used only when collecting the data"""

    def __init__(self, rawImgSize: tuple[float, float]):
        # This still uses a face landmarker model that was taken from Google's repo. The preprocessing code uses the
        # model included in mediapipe. Results differ. This should be upgraded to use the internal model as well.
        if not DownloadFaceLandmarkerModelBundle():
            print('error: Could not download model bundle. Exiting.')

            exit(1)
    
        self._bopt = python.BaseOptions('models/face_landmarker.task')
        self._opt  = vision.FaceLandmarkerOptions(base_options=self._bopt, num_faces=1)
        self._det  = vision.FaceLandmarker.create_from_options(self._opt)
        self._size = rawImgSize
        self._lock = Lock()
        self._exec = ThreadPoolExecutor(16)


    def processRawImage(self, sess, image: bytes, imgPath: str, sessId: str, stId: int, idx: int) -> None:
        """runs the facial recognition and eye check on the input image and saves it if both tests succeed"""

        def int_actualProcessRawImage(image: bytes, sess, imgPath: str, sessId: str, stId: int, idx: int) -> None:
            # Load image.
            rawImg = PILImage.open(BytesIO(image)).convert('RGB')
            npImg  = asarray(rawImg)
            mpImg  = MPImage(image_format=ImageFormat.SRGB, data=npImg)

            # Detect face landmarks.
            res = None
            try:
                with self._lock:
                    res = self._det.detect(mpImg).face_landmarks[0]
            except:
                print(f'[SESS#{sessId}] warning: No face detected for stage {stId} (idx: {idx}). Discarding the image.')

                sess.stageStats[stId].nFNoHead += 1
                sess.sendCommandToHook('Cmd_SubmitError', 'No face detected.')
                return
            
            # Calculate EAR and decide if the person's eyes are closed.
            ear_l, ear_r = Internal_CalcEAR(res)
            print(f'[SESS#{sessId}] [{sessId}, {stId}, {idx}] info: EAR = {ear_l}, {ear_r}')
            if ear_l < 0.25 or ear_r < 0.25:
                print(f'[SESS#{sessId}] warning: At least one eye closed or nearly closed. Discarding the image.')

                sess.stageStats[stId].nFEyesCl += 1
                sess.sendCommandToHook('Cmd_SubmitError', 'At least one eye is almost or fully closed.')
                return
            
            # Save raw image.
            try:
                rawImg.save(imgPath)

                sess.stageStats[stId].nSucc += 1
            except:
                sess.stageStats[stId].nFOther += 1

                print(f'[SESS#{sessId}] error: Failed to write image file {imgPath}.')

        # Spawn a thread that does the actual processing in order not to overload the request handler. Doing the
        # processing on the same thread as the request blocks one of the Flask workers.
        self._exec.submit(int_actualProcessRawImage, image, sess, imgPath, sessId, stId, idx)



def Internal_CalcEAR(lm: list) -> tuple[float, float]:
    """calculate eye aspect ratio (EAR) for both eyes individually"""

    # Taken from: https://github.com/Pushtogithub23/Eye-Blink-Detection-using-MediaPipe-and-OpenCV
    LEFT_EYE_LM  = [362, 380, 374, 263, 386, 385]
    RIGHT_EYE_LM = [33, 159, 158, 133, 153, 145]

    leftEAR  = 0.0
    rightEAR = 0.0
    for i, eye in [(0, LEFT_EYE_LM), (1, RIGHT_EYE_LM)]:
        p1, p2, p3, p4, p5, p6 = eye

        # EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
        numEAR  = linalg.norm(array([lm[p2].x, lm[p2].y]) - array([lm[p6].x, lm[p6].y])) + linalg.norm(array([lm[p3].x, lm[p3].y]) - array([lm[p5].x, lm[p5].y]))
        denEAR  = 2 * linalg.norm(array([lm[p1].x, lm[p1].y]) - array([lm[p4].x, lm[p4].y]))
        EAR     = numEAR / denEAR if denEAR != 0.0 else 0.0

        if i == 0: leftEAR  = EAR
        if i == 1: rightEAR = EAR

    return leftEAR, rightEAR


