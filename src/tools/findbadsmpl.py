# Find bad samples.
import cv2
import numpy as np

from sys       import argv
from os        import walk, makedirs
from os.path   import exists, join
from shutil    import rmtree, copy
from json      import dump
from tqdm      import tqdm

from preproc import int_GetFaceBoundingBox
from facelm  import FaceLandmarker


LEFT_EYE   = [ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398 ]
RIGHT_EYE  = [  33,   7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246 ]
NOSE_RIDGE = [4, 5, 195, 197, 6, 168]


def int_IsBlurry(im, lms, thres=100) -> tuple[bool, float]:
    img = cv2.imread(im, 0)
    if img is None:
        return False, 0.0

    # Crop face.
    bb = int_GetFaceBoundingBox(lms)
    bb = (bb[0] * 1920, bb[1] * 1080, bb[2] * 1920, bb[3] * 1080)
    img = img[int(bb[1]):int(bb[3]), int(bb[0]):int(bb[2])]
    if img.size == 0:
        return False, 0.0

    var = cv2.Laplacian(img, cv2.CV_64F).var()
    return var < thres, var


def int_IsOnlyPartiallyInImage(lm, thres=0.5) -> tuple[bool, tuple[float, float]]:
    # Calculate how many LMs are outside the image for both eyes.
    nLeft  = sum([1 for x in [lm[i] for i in LEFT_EYE]  if x.x < 0.0 or x.x > 1.0 or x.y < 0.0 or x.y > 1.0])
    nRight = sum([1 for x in [lm[i] for i in RIGHT_EYE] if x.x < 0.0 or x.x > 1.0 or x.y < 0.0 or x.y > 1.0])

    return nLeft / len(LEFT_EYE) >= thres or nRight / len(RIGHT_EYE) >= thres, (nLeft / len(LEFT_EYE), nRight / len(RIGHT_EYE))


def int_isObstructedByNoseRidge(lm, thres=0.75) -> tuple[bool, float]:
    # Simple linear regression.
    pts  = np.array([(lm[i].x, lm[i].y) for i in NOSE_RIDGE])
    M, B = np.polyfit(pts[:,0], pts[:,1], 1)

    # Check if eye LMs are below the nose ridge edge, meaning they are potentially obstructed.
    pUnder = 0
    for i in [lm[j] for j in LEFT_EYE + RIGHT_EYE]:
        if M * i.x + B < i.y:
            pUnder += 1

    # Because one eye will always be fully under the line, we need to check if most eye LMs are below the line, meaning
    # the face is tilted, causing the other eye to be partially obstructed, too.
    return pUnder / len(LEFT_EYE + RIGHT_EYE) >= thres, pUnder / len(LEFT_EYE + RIGHT_EYE)



if __name__ == '__main__':
    src = argv[1]
    dst = argv[2]
    blu = '-b' in argv
    par = '-p' in argv
    nos = '-n' in argv

    # Initialize face landmarker.
    flm = FaceLandmarker()

    # Prepare result dirs.
    if exists(dst):
        rmtree(dst)
    makedirs(join(dst, '__OK__'))
    makedirs(join(dst, 'blurry'))
    makedirs(join(dst, 'partial'))
    makedirs(join(dst, 'obstructed'))

    # Prepare result document.
    results = {}
    for i in range(4):
        results[i] = {}

        for j in ['blurry', 'partial', 'obstructed', 'only_blurry', 'only_partial', 'only_obstructed']:
            results[i][j] = 0

    # Do processing.
    files2Proc = []
    for root, d, files in walk(src):
        for f in files:
            fn = join(root, f)
            if not f.endswith('.jpg'):
                continue

            files2Proc.append((f, fn))

    for f, fn in tqdm(files2Proc, desc='Processing'):
            # Get region.
            r = int(f.split('_')[2])

            # Get LMs.
            lm = flm.getFacialLandmarks(fn)
            if lm.multi_face_landmarks is None:
                #print(f'warning: Image "{fn}" does not contain a face. Skipping.')

                results[r]['partial']      += 1
                results[r]['only_partial'] += 1
                continue
            try:
                lm = lm.multi_face_landmarks[0]
                lm = lm.landmark
            except:
                #print(f'warning: Image "{fn}" does not contain a face. Skipping.')

                results[r]['partial']      += 1
                results[r]['only_partial'] += 1
                continue

            # Check blur.
            isBlurry = False
            if blu:
                res, var = int_IsBlurry(fn, lm, 100)

                if res:
                    copy(fn, join(dst, 'blurry', f))

                    isBlurry = True
                    results[r]['blurry'] += 1
                    #print(f'info: Image "{fn}" is blurry (v={var}).')

            # Check partial.
            isPartial = False
            if par:
                res, _ = int_IsOnlyPartiallyInImage(lm, 0.3)

                if res:
                    copy(fn, join(dst, 'partial', f))

                    isPartial = True
                    results[r]['partial'] += 1
                    #print(f'info: Image "{fn}" only contains a partial face. (l={l}, r={r}).')

            # Check obstructed.
            isObstructed = False
            if nos:
                res, p = int_isObstructedByNoseRidge(lm, 0.55)

                if res:
                    copy(fn, join(dst, 'obstructed', f))

                    isObstructed = True
                    results[r]['obstructed'] += 1
                    #print(f'info: Image "{fn}" is obstructed by nose ridge (p={p}).')

            # Update uniques.
            results[r]['only_blurry']     += isBlurry     and not isPartial and not isObstructed
            results[r]['only_partial']    += isPartial    and not isBlurry  and not isObstructed
            results[r]['only_obstructed'] += isObstructed and not isBlurry  and not isPartial

            if not isBlurry and not isPartial and not isObstructed:
                copy(fn, join(dst, '__OK__', f))

    # Write stats.
    with open(join(dst, 'results.json'), 'w') as file:
        dump(results, file, indent=4)

        print(f'info: Wrote results to "{file.name}".')

    exit(0)


