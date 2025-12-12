import { ImageSubmitter } from './imgsubm.js'


/**
 */
class SessionControlWebSocket {
    /**
     */
    constructor(obj) {
        this.wsObj = obj

        this.wsObj.onmessage = this.onMessage.bind(this)
    }


    /**
     */
    onMessage() {

    }


    /**
     */
    static async Create(role, sessionCode) {
        /* Connect to websocket. */
        let websocketObj = null
        {
            const wsConnProc = new Promise((resolve, reject) => {
                websocketObj = new WebSocket(`wss://${location.host}/ws/${sessionCode}/${role}`)

                websocketObj.onopen  = ()   => { 
                    websocketObj.send(JSON.stringify({ 'message': `hello from role ${role}.` }))

                    resolve(websocketObj)
                }
                websocketObj.onerror = (ev) => {
                    const err = new Error(`Could not initialize websocket. Reason: ${ev}`)

                    reject(err)
                }
            })
            await wsConnProc
        }

        /* Create actual websocket object. */
        return new SessionControlWebSocket(websocketObj)
    }
}

/**
 */
export class SessionControl {
    /**
     */
    constructor() {
        this.config       = null
        this.imgSubmitter = null
        this.currViewId   = null
        this.roleId       = null
        this.sessionCode  = null
        this.websocket    = null

        try {
            this.initializeInteractiveElements()
        } catch (err) {
            this.displayFatalError(err.message)
        }
    }


    /**
     */
    initializeInteractiveElements() {
        const crBtn = document.getElementById('btnCreateSession')
        const jnBtn = document.getElementById('btnJoinSession')

        /* Create listener for the 'Create session' button in the 'Welcome' view. */
        crBtn.addEventListener('click', async() => {
            const response = await fetch('/api/create', { method: 'POST' })
            const data     = await response.json()

            if (data.type == 'ok') {
                this.roleId      = data.payload.role
                this.sessionCode = data.payload.code

                /* Create websocket. */
                this.websocket = await SessionControlWebSocket.Create(this.roleId, this.sessionCode)

                /* Show session code so that the user can enter it in another client supposed to join the session. */
                this.switchToView('viewCodeDisplay')
                {
                    const codeDispLabel = document.getElementById('lblCodeDisplay')
                    if (codeDispLabel == null) {
                        this.displayFatalError('Could not display session code.')

                        return;
                    }

                    codeDispLabel.textContent = `Session Code: ${this.sessionCode}`
                }

                return;
            }

            /*
             * Error occurred. Display it in the global error view so that the user cannot interact with the app any
             * more.
             */
            this.displayFatalError(data.desc)
        })

        /*
         * Create a listener for the button allowing the user to submit a code of an already created session. This
         * session code should be the one shown to the user after having created a session.
         */
        jnBtn.addEventListener('click', async() => {
            let code

            /* Get the session code from the respective input element. */
            const inpElem = document.getElementById('inpSessionToken')
            {
                if (inpElem == null || (code = inpElem.value) == '') {
                    this.displayFatalError(
                        'Could not retrieve session code from the input field. Perhaps it was empty. Refresh the ' + 
                        'page to retry.'
                    )

                    return;
                }
            }

            const response = await fetch('/api/join', { 
                method:  'POST',
                headers: {
                    'session': code
                }
            })
            const data     = await response.json()

            if (data.type == 'ok') {
                this.roleId      = data.payload.role
                this.sessionCode = data.payload.code

                /* Create websocket. */
                this.websocket = await SessionControlWebSocket.Create(this.roleId, this.sessionCode)

                this.switchToIdleView()
                return;
            }

            /* Error occurred. */
            this.displayFatalError(data.desc)
        })
    }

    /**
     */
    switchToView(viewId) {
        const newView  = document.getElementById(viewId)
        const currView = document.getElementById(this.currViewId)
        {
            if (newView == null)
                this.displayFatalError(`View with id "${viewId}" does not exist.`)
            
            if (this.currViewId != null)
                currView.style.display = 'none'
            newView.style.display = 'block'
        }

        this.currViewId = viewId
    }

    switchToIdleView() {
        this.switchToView('viewIdle')
    }

    /**
     */
    displayFatalError(reason) {
        const errorLabel = document.getElementById('lblFatalErrorDesc')
        {
            errorLabel.textContent = reason
        }

        this.switchToView('viewFatalError')
        this.destroy()
    }

    /**
     */
    destroy() {
        this.imgSubmitter.destroy()
    }


    /**
     */
    static async Create() {
        let config
        let imgSubmit

        /* Create session control. */
        const sessCtrl = new SessionControl()

        /* We need to be in a secure context for this application to even work. */
        if (!window.isSecureContext)
            return [sessCtrl, new Error('This application requires a secure context.')]

        /*
         * Load session configuration from the script element containing it. The actual configuration is provided by the
         * server.
         */ 
        const cfg = document.getElementById('scrSessionConfig')
        {
            if (cfg == null)
                return [sessCtrl, new Error('Could not retrieve session configuration.')]

            config = JSON.parse(cfg.textContent)
        }

        /* Create image submitter component. */
        imgSubmit = await ImageSubmitter.Create(1920, 1080)
        {
            if (imgSubmit == null);
                //throw new Error(
                //    'Could not initialize image submitter component. Perhaps no camera is installed or the ' +
                //    'application is not allowed to use it.'
                //)
        }

        /* All good. Set instance properties. */
        sessCtrl.config       = config
        sessCtrl.imgSubmitter = imgSubmit

        return [sessCtrl, null]
    }
}


