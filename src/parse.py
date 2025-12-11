from __future__             import annotations

from io                     import BytesIO
from PIL                    import Image as PILImage
from numpy                  import asarray
from mediapipe              import Image as MPImage, ImageFormat
from mediapipe.tasks        import python
from mediapipe.tasks.python import vision
from enum                   import Enum
from dataclasses            import dataclass

from dlmdl                  import DownloadFaceLandmarkerModelBundle


class EntityId(Enum):
    FACE  = 0,
    LEFT  = 1,
    RIGHT = 2


@dataclass
class BoundingBox:
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

        self.left  = max(0,     self.left   - l)
        self.top   = max(0,     self.top    - t)
        self.right = min(1920,  self.right  + r)
        self.bottom = min(1080, self.bottom + b)

        return self

class FaceParser:
    def __init__(self, rawImgSize: tuple[float, float]):
        if not DownloadFaceLandmarkerModelBundle():
            print('error: Could not download model bundle. Exiting.')

            exit(1)
    
        self._bopt = python.BaseOptions('models/face_landmarker.task')
        self._opt  = vision.FaceLandmarkerOptions(base_options=self._bopt, num_faces=1)
        self._det  = vision.FaceLandmarker.create_from_options(self._opt)
        self._size = rawImgSize

    async def processRawImage(self, image: bytes, sessId: str, stId: int, idx: int) -> None:
        # Load image.
        rawImg = PILImage.open(BytesIO(image)).convert('RGB')
        npImg  = asarray(rawImg)
        mpImg  = MPImage(image_format=ImageFormat.SRGB, data=npImg)

        # Detect face landmarks.
        res = None
        try:
            res = self._det.detect(mpImg).face_landmarks[0]
        except IndexError:
            print(f'[SESS#{sessId}] warning: No face detected for stage {stId} (idx: {idx}).')

            return
        # Calculate bounding boxes.
        fbbox  = Internal_GetEntityBoundingBox(EntityId.FACE, res).scale(self._size).pad((250, 250, 250, 250))
        lebbox = Internal_GetEntityBoundingBox(EntityId.LEFT, res).scale(self._size).pad((40, 40, 40, 40))
        rebbox = Internal_GetEntityBoundingBox(EntityId.RIGHT, res).scale(self._size).pad((40, 40, 40, 40))

        # Crop face, left eye, and right eye.
        faceCrop = rawImg.crop(fbbox.tuple()).resize((512, 512))
        leCrop   = rawImg.crop(lebbox.tuple()).resize((256, 256))
        reCrop   = rawImg.crop(rebbox.tuple()).resize((256, 256))
        # Save results.
        faceCrop.save(f'files/proc/{sessId}/face_{sessId}_{stId}_{idx}.jpg')
        leCrop.save(f'files/proc/{sessId}/left_{sessId}_{stId}_{idx}.jpg')
        reCrop.save(f'files/proc/{sessId}/right_{sessId}_{stId}_{idx}.jpg')


def Internal_GetEntityBoundingBox(id: EntityId, landmarks: list) -> BoundingBox:
    # Taken from: https://gist.github.com/Asadullah-Dal17/fd71c31bac74ee84e6a31af50fa62961
    LEFT_EYE  = [ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398 ]
    RIGHT_EYE = [  33,   7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246 ]
    FACE      = [ 
         10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
        150, 136, 172,  58, 132,  93, 234, 127, 162,  21,  54, 103,  67, 109
    ]

    # Determine the set of landmarks to iterate over.
    targetLandmarks = []
    match id:
        case EntityId.FACE:  targetLandmarks = FACE
        case EntityId.LEFT:  targetLandmarks = LEFT_EYE
        case EntityId.RIGHT: targetLandmarks = RIGHT_EYE

    res = BoundingBox.Null()
    for lmIdx in targetLandmarks:
        lm = landmarks[lmIdx]

        res.left   = min(res.left,   lm.x)
        res.top    = min(res.top,    lm.y)
        res.right  = max(res.right,  lm.x)
        res.bottom = max(res.bottom, lm.y)

    return res


