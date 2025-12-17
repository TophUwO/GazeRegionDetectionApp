from __future__            import annotations
from quart                 import Quart, Response, render_template, request, websocket
from session               import *
from error                 import ResponseStatus, FormatResponse
from parse                 import FaceParser
from json                  import loads
from base64                import *
from os                    import getenv
from jsonschema            import validate


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
        self.sman   = SessionManager()
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

    print(f'[SESS#{sess.sessionCode}] Opened session.')

    # Return session code.
    return FormatResponse(ResponseStatus.Ok, { 
        'code': sess.sessionCode,
        'role': app._cfgDict['creatorRole']
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
    # await sess.sendRole('H', 'ready')
    return FormatResponse(ResponseStatus.Ok, {
        'code': sess.sessionCode,
        'role': app._cfgDict['joinerRole']
    })

@app.route('/api/advance/<code>', methods=['POST'])
async def advanceStage(code):
    sess = app.sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)
    
    # sess.advanceStage()
    # await sess.sendRole('any', 'start_stage', sess.stageId)
    # if sess.stageId == 9:
    #    await sess.sendRole('H', 'fini')
    return FormatResponse(ResponseStatus.Ok)

@app.route('/api/submit/<code>', methods=['POST'])
async def saveImage(code):
    sess = app.sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)
    elif not sess.stage.canSupply:
        return FormatResponse(ResponseStatus.CannotSupplyImages)
    
    data = await request.get_json()
    image_data = data["image"]

    # Remove "data:image/jpeg;base64," prefix if present
    if image_data.startswith("data:image"):
        header, image_data = image_data.split(",", 1)

    # Decode base64
    image_bytes = b64decode(image_data)

    # Save to file
    with open(f"files/raw/{code}/raw_{code}_{sess.stageId}_{sess.idx}.jpg", "wb") as f:
        f.write(image_bytes)
    sess.idx += 1

    # TODO: make it so that this runs in a worker thread
    await app.parser.processRawImage(image_bytes, code, sess.stageId, sess.idx)
    return FormatResponse(ResponseStatus.Ok)


@app.websocket('/ws/<code>/<role>')
async def handleWebsocket(code, role):
    # Get session.
    sess = app.sman.getSession(code)
    if sess is None or role not in app._cfgDict['roleIds']:
        await websocket.close()

    # Set the websocket connection.
    ws = websocket._get_current_object()
    if   role == app._cfgDict.get('creatorRole'): sess.tabs.upper = ws
    elif role == app._cfgDict.get('joinerRole'):  sess.tabs.lower = ws

    print(f'[SESS#{sess.sessionCode}] Opened WebSocket for role \'{role}\'.')

    # Run loop.
    try:
        while True:
            data = await websocket.receive_json()

            match data['type']:
                case 'msg':
                    print(f'[SESS#{sess.sessionCode}] Received JSON from role \'{role}\': {data}')
    except:
        print(f'[SESS#{sess.sessionCode}] Closed WebSocket for role {role}.')

        # Remove the ws.
        if   role == app._cfgDict.get('creatorRole'): sess.tabs.upper = None
        elif role == app._cfgDict.get('joinerRole'):  sess.tabs.lower = None

        # Delete session if both sockets are None.
        if sess.tabs.upper is None and sess.tabs.lower is None:
            try:
                app.sman.deleteSession(sess.sessionCode)

                await websocket.close(1000)
            except:
                pass

            print(f'[SESS#{sess.sessionCode}] Closed session.')


