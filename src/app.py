from quart   import *
from session import *


app:  Quart          = Quart(__name__)
sman: SessionManager = SessionManager()

@app.route('/')
async def index():
    return await send_from_directory('static', 'index.html')


@app.route('/api/create', methods=["POST"])
async def createSession():
    sess: Session = sman.createSession()

    print(f'[SESS#{sess.sessionCode}] Opened session.')

    # Return session code.
    return jsonify({"status": "ok", 'code': sess.sessionCode}), 200

@app.route('/api/join', methods=["POST"])
async def joinSession():
    code = request.args.get('code', None)
    if code is None:
        return jsonify({"status": "error", "error": "Invalid session token"}), 404
    
    # Get session.
    sess: Session = sman.getSession(code)
    if sess is None:
        return jsonify({"status": "error", "error": "Session not found."}), 404
    
    # Send to upper ready msg.
    await sess.upperTab.send(json.dumps({"type": "ready"}))
    # All good.
    return jsonify({"status": "ok"}), 200


@app.websocket('/ws/<code>/<role>')
async def handleWebsocket(code, role):
    # Get session.
    sess: Session = sman.getSession(code)
    if sess is None or role not in ['upper', 'lower']:
        await websocket.close()

    # Set the websocket connection.
    ws = websocket._get_current_object()
    match role:
        case 'upper': sess.upperTab = ws
        case 'lower': sess.lowerTab = ws

    print(f'[SESS#{sess.sessionCode}] Opened WebSocket for role \'{role}\'.')

    # Run loop.
    try:
        while True:
            data = await websocket.receive_json()

            print(f'[SESS#{sess.sessionCode}] Received JSON from role \'{role}\': {data}')
    except:
        print(f'[SESS#{sess.sessionCode}] Closed WebSocket for role {role}.')

        match role:
            case 'upper': sess.upperTab = None
            case 'lower': sess.lowerTab = None

        # Delete session if both sockets are None.
        if sess.upperTab is None and sess.lowerTab is None:
            try:
                sman.deleteSession(sess.sessionCode)

                await websocket.close(1000)
            except:
                pass

            print(f'[SESS#{sess.sessionCode}] Closed session.')


