/**
 */
export class SessionWebSocket {
    /**
     * 
     * @param {*} ctrl 
     */
    constructor(ctrl) {
        this.ctrl  = ctrl
        this.wsObj = null
        this.rdy   = null
        this.rec   = false

        this.GL_ONMESSAGE_CBTAB = {
            'Cmd_Ready':      this.ctrl.onReady.bind(this.ctrl),
            'Cmd_StartStage': this.ctrl.onStartStage.bind(this.ctrl),
            'Cmd_EndStage':   this.ctrl.onEndStage.bind(this.ctrl)
        }
    }


    /**
     * 
     * @param {*} event 
     */
    onMessage(event) {
        /* Parse message object. If it fails, something is wrong. */
        let msgObj = null
        try {
            msgObj = JSON.parse(event.data)
        } catch (err) {
            console.log(`Error while parsing message as JSON. Reason: ${err}`)

            return
        }

        /* Process message. */
        try {
            const callback = this.GL_ONMESSAGE_CBTAB[msgObj.command]
            if (callback == null)
                throw new Error(`Unknown command \"${msgObj.command}\".`)
            else if (typeof callback !== 'function')
                throw new Error(`Command \"${msgObj.command}\" is misconfigured (callback is not a function.`)

            callback(msgObj)
        } catch (err) {
            console.log(`Error while processing command \"${msgObj.command}\". Description: ${err}`)
        }
    }



    /**
     * 
     * @param {*} msg 
     */
    sendMessage(msg) {
        if (this.wsObj?.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket is not open. Not sending message.')

            return
        }

        this.wsObj.send(JSON.stringify({ 'type': 'msg', 'message': msg }))
    }



    /**
     * 
     */
    async connect(ctrl, role, sessionCode) {
        this.rdy = new Promise((resolve, reject) => {
            let wasOpened = false
            this.wsObj    = new WebSocket(`wss://${location.host}/ws/${sessionCode}/${role}`)

            this.wsObj.onopen  = ()   => {
                this.wsObj.send(JSON.stringify({ 'type': 'msg', 'message': `hello from role ${role}.` }))

                wasOpened = true
                resolve(this.wsObj)
            }
            this.wsObj.onerror = (ev) => {
                console.error(`Could not initialize websocket. Reason: ${ev}`)
            }
            this.wsObj.onclose = async(ev) => {
                if (!wasOpened) {
                    const errStr = `Could not connect to websocket. Reason: ${ev}`

                    this.ctrl.displayFatalError(errStr)
                    reject(errStr)
                } else if (!this.rec && !ev.wasClean) {
                    console.error('Websocket was closed abruptly. Attempting a reconnect ...')

                    this.rec = true
                    try {
                        await this.connect(ctrl, role, sessionCode)

                        console.log('Successfully reestablished connection to WebSocket.')
                    } catch (err) {
                        this.ctrl.displayFatalError(
                            'Could not reconnect to WebSocket. Please restart the session by refreshing the page on ' + 
                            'both clients.'
                        )
                    }
                }
            }
            this.wsObj.onmessage = this.onMessage.bind(this)
        })
        await this.rdy
    }


    /**
     * 
     * @param {*} ctrl 
     * @param {*} role 
     * @param {*} sessionCode 
     * @returns 
     */
    static async Create(ctrl, role, sessionCode) {
        /* Create actual websocket object. */
        const wsObj = new SessionWebSocket(ctrl)

        await wsObj.connect(ctrl, role, sessionCode)
        return wsObj
    }
}


