export class ServerEventSource {
    constructor(ctrl) {
        this.ctrl = ctrl
        this.sse  = new EventSource(`/sse/${ctrl.sessionCode}/${ctrl.roleId}`)

        this.sse.onopen = (ev) => {
            console.log(`Successfully opened SSE source for [${ctrl.sessionCode}::${ctrl.roleId}]`)
        }
        this.sse.onerror = (ev) => {
            console.error('SSE error:', ev)
        }
        this.sse.onmessage = this.onMessage.bind(this)

        this.GL_ONMESSAGE_CBTAB = {
            'Cmd_Ready':      this.ctrl.onReady.bind(this.ctrl),
            'Cmd_StartStage': this.ctrl.onStartStage.bind(this.ctrl),
            'Cmd_EndStage':   this.ctrl.onEndStage.bind(this.ctrl),
            'Cmd_EndSession': this.ctrl.onEndSession.bind(this.ctrl)
        }
    }


    async onMessage(event) {
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

            await callback(msgObj)
        } catch (err) {
            console.log(`Error while processing command \"${msgObj.command}\". Description: ${err}`)
        }
    }


    /**
     * 
     */
    close() {
        console.log('Closing SSE connection.')

        this.sse.close()
    }
}


