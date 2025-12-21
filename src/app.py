from __future__    import annotations
from flask         import Flask, Response, render_template, request, abort
from flask.helpers import make_response
from session       import SessionManager
from error         import ResponseStatus, FormatResponse
from parse         import FaceParser, LabelGenerator
from json          import loads
from os            import getenv
from jsonschema    import validate
from queue         import Empty


# TODO: document the fuck out of this
# TODO: schema


class DataCollectionApp(Flask):
    def _readSessionConfigFile(self) -> bool:
        try:
            with open(self._cfgFileName) as fp:
                self._rawCfgFileContents = fp.read()
        except OSError as exc:
            print(f'error: Could not open session configuration file. Reason: {exc}')

            return False
        
        # All good.
        return True
    
    def _validateSessionConfig(self) -> bool:
        CONFIG_SCHEMA = r'''
            {

            }
        '''

        try:
            self._cfgDict = loads(self._rawCfgFileContents)

            validate(self._cfgDict, loads(CONFIG_SCHEMA))
        except Exception as exc:
            print(f'error: Session configuration file validation failed. Reason: {exc}')

            return False
        
        # All good.
        return True


    def __init__(self):
        super().__init__(__name__)

        # Read config from env.
        self._cfgFileName        = getenv('DATACOLL_USED_REGION_CONFIG')
        self._rawCfgFileContents = ''
        self._cfgDict            = {}

        if not self._cfgFileName or self._cfgFileName == '' or not self._readSessionConfigFile():
            print(
                'error: Could not load session configuration file. Set \'DATACOLL_USED_REGION_CONFIG\' to the '
                'file containing a valid session configuration.'
            )

            exit(1)

        # Validate session config.
        if not self._validateSessionConfig():
            exit(1)

        # Initialize sub-components.
        self.sman   = SessionManager(config=self._cfgDict)
        self.parser = FaceParser((1920, 1080))

        print('info: Initialized application. Ready.')


# $env:DATACOLL_USED_REGION_CONFIG="src/conf/mtmsession.json"; $env:DATACOLL_USED_CERT="..."; $env:DATACOLL_USED_KEY="..."; python src/app.py
app = DataCollectionApp()


@app.route('/')
def index():
    return render_template('index.html', GL_SESSION_CONFIG=app._cfgDict)

@app.after_request
def disableClientSideCaching(response: Response):
    response.headers['Cache-Control']     = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma']            = 'no-cache'
    response.headers['Expires']           = '0'
    response.headers['Surrogate-Control'] = 'no-store'

    return response


@app.route('/api/create', methods=['POST'])
def createSession():
    sess = app.sman.createSession()
    if sess is None:
        return FormatResponse(ResponseStatus.CannotCreateSession)

    print(f'[SESS#{sess.code}] Opened session.')

    # Return session code.
    sess.registerClient(app._cfgDict['creatorRole'])
    return FormatResponse(ResponseStatus.Ok, { 
        'code':  sess.code,
        'role':  app._cfgDict['creatorRole']
    })

@app.route('/api/join', methods=['POST'])
def joinSession():
    code = request.headers.get('session', type=str, default=None)
    if code is None:
        return FormatResponse(ResponseStatus.InvalidSessionToken)
    
    # Get session.
    sess = app.sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)
    sess.registerClient(app._cfgDict['joinerRole'])
    
    # All good.
    sess.sendCommand(app._cfgDict['creatorRole'], 'Cmd_Ready')
    return FormatResponse(ResponseStatus.Ok, {
        'code': sess.code,
        'role': app._cfgDict['joinerRole']
    })

@app.route('/api/advance', methods=['POST'])
def advanceStage():
    code = request.headers.get('session', type=str, default=None)
    if code is None:
        return FormatResponse(ResponseStatus.InvalidSessionToken)

    sess = app.sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)

    if not sess.gotoNextStage():
        return FormatResponse(ResponseStatus.InvalidStage)

    sess.sendCommand('any', 'Cmd_StartStage')
    return FormatResponse(ResponseStatus.Ok)

@app.route('/api/submit', methods=['POST'])
def saveImage():
    code = request.headers.get('session', type=str, default=None)
    if code is None:
        return FormatResponse(ResponseStatus.InvalidSessionToken)

    sess = app.sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)
    elif not sess.stage.canSupply:
        return FormatResponse(ResponseStatus.CannotSupplyImages)

    # Parse request.
    form   = None
    img    = None
    index  = -1
    region = -1
    time   = -1
    x      = -1
    y      = -1
    try:
        form   = request.form
        img    = request.files['image'].read()

        x      = int(form['objX'])
        y      = int(form['objY'])
        index  = int(form['index'])
        region = int(form['region'])
        time   = int(form['time'])
    except:
        return FormatResponse(ResponseStatus.MalformedRequest)

    # Save and process.
    imgPath = f'files/raw/{code}/img_{code}_{region}_{index}.png'
    lblPath = f'files/raw/{code}/lbl_{code}_{region}_{index}.json'

    with open(lblPath, 'w') as labelFile:
        labelFile.write(LabelGenerator.GenerateLabel(imgPath, code, index, region, x, y, time))

    # This spawns a worker thread processing the image.
    app.parser.processRawImage(img, imgPath, code, region, index)
    return FormatResponse(ResponseStatus.Ok)


@app.route('/sse/<code>/<role>', methods=['GET'])
def handleSSE(code, role):
    if "text/event-stream" not in request.accept_mimetypes:
        abort(400)

    sess = app.sman.getSession(code)
    if sess is None or role not in app._cfgDict['roleIds']:
        abort(404)
    
    q = sess.getQueue(role)
    def int_dispatchMessage():
        yield ': __HELLO__\n\n'

        while True:
            message = None
            try:
                message = q.get(timeout=10)

                # End the generator if the session has ended.
                if message == 'SysCmd_EndSession':
                    return
            except Empty:
                yield ': __HEATBEAT__\n\n'

                print(f'sent heartbeat to {role}')
                continue

            yield f'data: {message}\n\n'

    res = make_response(int_dispatchMessage(), {
        'Content-Type':      'text/event-stream',
        'Cache-Control':     'no-cache',
        'Transfer-Encoding': 'chunked',
    })
    res.timeout = None
    return res


if __name__ == "__main__":
    certFile = getenv('DATACOLL_USED_CERT', None)
    keyFile  = getenv('DATACOLL_USED_KEY',  None)

    if not certFile or not keyFile:
        print('error: You need to specify a key and a certificate file to use.')

        exit(1)

    # Run the thing.
    app.run(
        host="0.0.0.0",
        port=8443,
        threaded=True,
        ssl_context=(certFile, keyFile),
    )


