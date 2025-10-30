from quart import *

gl_Application: Quart = Quart(__name__)


@gl_Application.route('/')
async def index():
    return await send_from_directory('static', 'index.html')

@gl_Application.route('/static/scripts/<path:path>')
async def int_ServeScripts(path):
    return await send_from_directory('static/scripts', path)

@gl_Application.route('/static/styles/<path:path>')
async def int_ServeStyleSheets(path):
    return await send_from_directory('static/styles', path)


