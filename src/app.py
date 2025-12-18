from __future__ import annotations
from quart      import Quart, Response, render_template, request, websocket
from session    import *
from error      import ResponseStatus, FormatResponse
from parse      import FaceParser, LabelGenerator
from json       import loads
from os         import getenv
from jsonschema import validate


# TODO: document the fuck out of this
# TODO: show insts given in config
# TODO: process images


class DataCollectionApp(Quart):
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


# On windows powershell run with:
#     $env:DATACOLL_USED_REGION_CONFIG="src/conf/mtmsession.json"; hypercorn src/app:app --bind 0.0.0.0:8443 --certfile 192.168.0.130+1.pem --keyfile 192.168.0.130+1-key.pem
app = DataCollectionApp()


@app.route('/')
async def index():
    return await render_template('index.html', GL_SESSION_CONFIG=app._cfgDict)

@app.after_request
async def disableClientSideCaching(response: Response):
    response.headers['Cache-Control']     = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma']            = 'no-cache'
    response.headers['Expires']           = '0'
    response.headers['Surrogate-Control'] = 'no-store'

    return response


@app.route('/api/create', methods=['POST'])
async def createSession():
    # TODO: can fail
    sess = app.sman.createSession()

    print(f'[SESS#{sess.code}] Opened session.')

    # Return session code.
    return FormatResponse(ResponseStatus.Ok, { 
        'code':  sess.code,
        'role':  app._cfgDict['creatorRole'],
        'token': sess.token
    })

@app.route('/api/join', methods=['POST'])
async def joinSession():
    code = request.headers.get('session', type=str, default=None)
    if code is None:
        return FormatResponse(ResponseStatus.InvalidSessionToken)
    
    # Get session.
    sess = app.sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)
    
    # All good.
    await sess.sendCommand(app._cfgDict['creatorRole'], 'Cmd_Ready')
    return FormatResponse(ResponseStatus.Ok, {
        'code': sess.code,
        'role': app._cfgDict['joinerRole']
    })

@app.route('/api/advance', methods=['POST'])
async def advanceStage():
    code = request.headers.get('session', type=str, default=None)
    if code is None:
        return FormatResponse(ResponseStatus.InvalidSessionToken)

    sess = app.sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)

    if not sess.gotoNextStage():
        return FormatResponse(ResponseStatus.InvalidStage)

    await sess.sendCommand('any', 'Cmd_StartStage')
    return FormatResponse(ResponseStatus.Ok)

@app.route('/api/submit', methods=['POST'])
async def saveImage():
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
        form   = await request.form
        img    = (await request.files)['image']

        x      = int(form['objX'])
        y      = int(form['objY'])
        index  = int(form['index'])
        region = int(form['region'])
        time   = int(form['time'])
    except Exception as err:
        return FormatResponse(ResponseStatus.MalformedRequest)

    # Save and process.
    imgPath = f'files/raw/{code}/img_{code}_{region}_{index}.png'
    lblPath = f'files/raw/{code}/lbl_{code}_{region}_{index}.json'

    sess.setLastIndex(index)
    with open(lblPath, 'w') as labelFile:
        labelFile.write(LabelGenerator.GenerateLabel(imgPath, code, index, region, x, y, time))
    await img.save(imgPath)

    # # TODO: make it so that this runs in a worker thread
    # await app.parser.processRawImage(image_bytes, code, sess.stageId, sess.idx)
    return FormatResponse(ResponseStatus.Ok)


@app.websocket('/ws/<code>/<role>')
async def handleWebsocket(code, role):
    sess = app.sman.getSession(code)
    if sess is None or role not in app._cfgDict['roleIds']:
        await websocket.close(1000)

    print(f'[SESS#{sess.code}] Opened WebSocket for role \'{role}\'.')

    # Run loop.
    sess.registerClient(role, websocket._get_current_object())
    try:
        while True:
            data = await websocket.receive_json()

            match data['type']:
                case 'msg':
                    print(f'[SESS#{sess.code}] Received JSON from role \'{role}\': {data}')
    except:
        print(f'[SESS#{sess.code}] Closed WebSocket for role {role}.')

        # Delete session if both sockets are None.
        sess.unregisterClient(role)
        if sess.isEmpty():
            try:
                app.sman.deleteSession(sess.code)

                await websocket.close(1000)
            except:
                pass

            print(f'[SESS#{sess.code}] Closed session.')


