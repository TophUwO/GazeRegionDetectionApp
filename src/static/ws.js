/**
 */
export class SessionWebSocket {
    /**
     * 
     * @param {*} ctrl 
     * @param {*} obj 
     */
    constructor(ctrl, obj) {
        this.ctrl  = ctrl
        this.wsObj = obj
        {
            this.wsObj.onmessage = this.onMessage.bind(this)
        }

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
        this.wsObj.send(JSON.stringify({ 'type': 'msg', 'message': msg }))
    }



    /**
     * 
     * @param {*} ctrl 
     * @param {*} role 
     * @param {*} sessionCode 
     * @returns 
     */
    static async Create(ctrl, role, sessionCode) {
        /* Connect to websocket. */
        let websocketObj = null
        {
            const wsConnProc = new Promise((resolve, reject) => {
                websocketObj = new WebSocket(`wss://${location.host}/ws/${sessionCode}/${role}`)

                websocketObj.onopen  = ()   => { 
                    websocketObj.send(JSON.stringify({ 'type': 'msg', 'message': `hello from role ${role}.` }))

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
        return new SessionWebSocket(ctrl, websocketObj)
    }
}


