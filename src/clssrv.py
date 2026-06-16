# System includes
from flask   import Flask, request, jsonify
from os      import getenv
from os.path import exists
from dotenv  import load_dotenv

# GazeReg includes
from clsmdl import GazeRegClassificationModel


## class GazeRegClassificationServer
#
# represents the classification server application
class GazeRegClassificationServer(Flask):
    def __init__(self):
        super().__init__(__name__)

        # If a .env file has been supplied, load configuration from there.
        dEnvFile = getenv('GAZEREG_ENV_PATH', 'None')
        if dEnvFile != 'None':
            if not exists(dEnvFile):
                print(f'error: Could not find environment configuration file \"{dEnvFile}\".')
            else:
                load_dotenv(dotenv_path=dEnvFile, override=True, encoding='utf-8')

                print(f'info: Successfully loaded environment configuration file \"{dEnvFile}\".')
        else:
            print('info: No environment configuration file provided. Using process environment configuration.')

        # Load pre-trained model.
        self._model = GazeRegClassificationModel(
            getenv('GAZEREG_MODEL_DIR', 'models'),
            getenv('GAZEREG_USE_CUDA', 'False') != 'False',
            getenv('GAZEREG_3_CLASS', 'False') != 'False',
            getenv('GAZEREG_BENCH', 'False') != 'False'
        )

    
    ## predicts the gaze region for the given image provided as a bytes object
    #
    # @param  imageBytes bytes object holding the images obtained from the request object
    # @return response as JSON object
    def predictFromBytes(self, imageBytes: bytes) -> dict:
        return self._model.predictStandalone(imageBytes)


# Initialize application.
app = GazeRegClassificationServer()


@app.route('/api/classify', methods=['POST'])
def handleClassifyRequest():
    # Get image.
    try:
        img = request.files['image'].read()
    except:
        print('error: Could not determine gaze region. Reason: No image submitted.')

        return jsonify({
            'status':           'No valid image submitted.',
            'predicted_region': -1
        }), 200
    
    # Predict gaze region.
    return jsonify(app.predictFromBytes(img)), 200



if __name__ == '__main__':
    # Load SSL context.
    certFile = getenv('GAZEREG_CERT_FILE', 'None')
    keyFile  = getenv('GAZEREG_KEY_FILE', 'None')
    if certFile == 'None' or keyFile == 'None':
        print('error: You need to specify a key- and a certificate file to use.')

        exit(1)

    # Run application.
    app.run(
        host="0.0.0.0",
        port=8443,
        threaded=True,
        ssl_context=(certFile, keyFile),
    )


