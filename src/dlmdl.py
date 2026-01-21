from os.path        import exists
from os             import makedirs
from urllib.request import urlretrieve
from urllib.error   import URLError, HTTPError


def DownloadFaceLandmarkerModelBundle() -> bool:
    print('info: Checking for \'face_landmarker.task\' ... ', end='')

    # Only download if it isn't already there.
    if exists('models/face_landmarker.task'):
        print('found.')

        return True
    print('not found. Downloading ... ', end='')

    # Create directory if needed.
    makedirs('models', exist_ok=True)
    
    # Download the model bundle.
    try:
        urlretrieve(
            'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task',
            'models/face_landmarker.task'
        )
        
        print('done.')
    except (URLError, HTTPError) as exc:
        print('failed.')

        print(f'error: Error downloading latest face_landmarker.task bundle. Reason: {exc}')
        return False
    
    # All good.
    return True

    
