# Torch- and system includes
from torch      import load, device, tensor, float32, argmax, no_grad
from torch.cuda import is_available
from os.path    import join
from time       import perf_counter

# GazeReg includes
from model         import GazeRegModel
from tools.preproc import PreprocessImage_Simple
from tools.facelm  import FaceLandmarker


## class GazeRegSalModel
#
# provides the interface to the pre-trained classification model
class GazeRegSalModel:
    MODELNAME4CLS = 'GazeRegModel_4Cls.tmdl'
    MODELNAME3CLS = 'GazeRegModel_3Cls.tmdl'

    ## loads and initializes the classification model
    #
    # @param isThreeCls whether or not to load the simplified three-class model
    # @param modelDir model directory to search for a suitable pre-trained model
    # @param whether or not to send benchmark information alongside the response
    def __init__(self, modelDir: str, allowCUDA: bool = True, isThreeCls: bool = False, bench: bool = False):
        # Initialize face landmarker.
        self._flm = FaceLandmarker()

        # Load model. Use CUDA if available.
        self._bench  = bench
        self._isCuda = is_available() and allowCUDA
        self._dev    = device('cuda' if self._isCuda else 'cpu')
        self._mdl    = GazeRegModel(isThreeCls).to(self._dev)
        self._mdl.load_state_dict(
            load(
                join(modelDir, self.MODELNAME3CLS if isThreeCls else self.MODELNAME4CLS),
                map_location=self._dev,
                weights_only=False
            )
        )
        self._mdl.eval()

        # Print status info.
        print(f'info: Loaded {"3-class" if isThreeCls else "4-class"} GazeReg classification model.')
        if self._isCuda:
            print(f'info: Running classification model on {"CUDA device" if self._isCuda else "CPU"}.')
        if self._bench:
            print('info: Running classification service in benchmark mode.')


    ## predicts the gaze region of a given input image
    #
    # @param   image raw image bytes
    # @returns JSON document containing the predicted gaze region
    # @note    This method is designed for use in a HTTPS request handler or wherever the image is provided as a bytes
    #          object.
    def predictStandalone(self, image: bytes) -> dict:
        result = {
            'status':           None,
            'predicted_region': -1
        }
        if self._bench:
            result['timings'] = []

            t1 = perf_counter()
        
        # (1) Preprocess image.
        try:
            rawRes = PreprocessImage_Simple(self._flm, image, False)

            if rawRes is None:
                result['status'] = 'No face detected.'

                return result
            l, r, lm, p = rawRes[0][1], rawRes[0][0], rawRes[1], rawRes[2]
        except TypeError:
            result['status'] = 'Invalid parameter type.'

            return result
        except:
            result['status'] = 'Unknown internal error.'

            return result
        
        # (2) Prepare inputs.
        l = (tensor(l, dtype=float32).unsqueeze(0).unsqueeze(0) / 255.0).to(self._dev)
        r = (tensor(r, dtype=float32).unsqueeze(0).unsqueeze(0) / 255.0).to(self._dev)
        lm = tensor(lm, dtype=float32).unsqueeze(0).to(self._dev)
        p  = tensor(p, dtype=float32).unsqueeze(0).to(self._dev)
        if self._bench:
            t2 = perf_counter()

            result['timings'].append((t2 - t1) * 1000.0)

        # (3) Predict gaze region.
        with no_grad():
            result['status'] = 'OK'

            if self._bench:
                t1 = perf_counter()
            result['predicted_region'] = int(argmax(self._mdl(l, r, lm, p), dim=1).item())
            if self._bench:
                t2 = perf_counter()

                result['timings'].append((t2 - t1) * 1000.0)

        return result


