from quart   import Quart, send_from_directory, request, websocket
from session import *
from error   import *
from json    import *
from time    import *
from base64  import *


app:  Quart          = Quart(__name__)
sman: SessionManager = SessionManager()


ctr = 0


@app.route('/')
async def index():
    return await send_from_directory('static', 'index.html')

@app.after_request
async def disableClientSideCaching(response: Response):
    response.headers['Cache-Control']     = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    response.headers['Pragma']            = 'no-cache'
    response.headers['Expires']           = '0'
    response.headers['Surrogate-Control'] = 'no-store'

    return response


@app.route('/api/create', methods=['POST'])
async def createSession():
    sess: Session = sman.createSession()

    print(f'[SESS#{sess.sessionCode}] Opened session.')

    # Return session code.
    return FormatResponse(ResponseStatus.Ok, { 'code': sess.sessionCode })

@app.route('/api/join', methods=['POST'])
async def joinSession():
    code = request.args.get('code', None)
    if code is None:
        return FormatResponse(ResponseStatus.InvalidSessionToken)
    
    # Get session.
    sess: Session = sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)
    
    # All good.
    await sess.sendRole('H', 'ready', '')
    return FormatResponse(ResponseStatus.Ok)

@app.route('/api/advance/<code>', methods=['POST'])
async def advanceStage(code):
    sess: Session = sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)
    
    global ctr
    ctr = 0
    sess.advanceStage()
    await sess.sendRole('any', 'start_stage', sess.stageId)
    if sess.stageId == 9:
        await sess.sendRole('H', 'fini', '')
    return FormatResponse(ResponseStatus.Ok)

@app.route('/api/submit/<code>', methods=['POST'])
async def saveImage(code):
    sess: Session = sman.getSession(code)
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
    global ctr
    with open(f"files/img_{code}_{sess.stageId}_{ctr}.jpg", "wb") as f:
        f.write(image_bytes)
    ctr += 1

    print('processed files')
    return FormatResponse(ResponseStatus.Ok)

@app.route('/api/pause/<code>', methods=['POST'])
async def pause(code):
    sess: Session = sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)
    
    await sess.sendRole('any', 'pause', time() + 1)
    return FormatResponse(ResponseStatus.Ok)

@app.route('/api/resume/<code>', methods=['POST'])
async def resume(code):
    sess: Session = sman.getSession(code)
    if sess is None:
        return FormatResponse(ResponseStatus.SessionNotFound)
    
    await sess.sendRole('any', 'resume', time() + 1)
    return FormatResponse(ResponseStatus.Ok)


@app.websocket('/ws/<code>/<role>')
async def handleWebsocket(code, role):
    # Get session.
    sess: Session = sman.getSession(code)
    if sess is None or role not in ['H', 'L']:
        await websocket.close()

    # Set the websocket connection.
    ws = websocket._get_current_object()
    match role:
        case 'H': sess.tabs.upper = ws
        case 'L': sess.tabs.lower = ws

    print(f'[SESS#{sess.sessionCode}] Opened WebSocket for role \'{role}\'.')

    # Run loop.
    try:
        while True:
            data = await websocket.receive_json()

            print(f'[SESS#{sess.sessionCode}] Received JSON from role \'{role}\': {data}')
    except:
        print(f'[SESS#{sess.sessionCode}] Closed WebSocket for role {role}.')

        # Remove the ws.
        match role:
            case 'H': sess.tabs.upper = None
            case 'L': sess.tabs.lower = None

        # Delete session if both sockets are None.
        if sess.tabs.upper is None and sess.tabs.lower is None:
            try:
                sman.deleteSession(sess.sessionCode)

                await websocket.close(1000)
            except:
                pass

            print(f'[SESS#{sess.sessionCode}] Closed session.')


