/**
 * @class ServerEventSource
 * @brief one-way pipe from server to client
 */
export class ServerEventSource {
    constructor(ctrl, code, role) {
        this.ctrl = ctrl
        this.sse  = new EventSource(`/sse/comm/${code}/${role}`)

        this.sse.onopen = (ev) => {
            console.log(`Successfully opened SSE source for [${ctrl.sessionCode}::${role}]`)
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


    close() {
        console.log('Closing SSE connection.')

        this.sse.close()
    }
}


/**
 * @class HookEventSource
 * @brief one-way pipe from server to observer
 */
export class HookEventSource {
    constructor(ctrl, code) {
        this.ctrl = ctrl
        this.sse  = new EventSource(`/sse/hook/${code}`)
        this.code = code

        this.sse.onopen = (ev) => {
            console.log(`Successfully opened SSE hook source for [${ctrl.sessionCode}]`)
        }
        this.sse.onerror = (ev) => {
            console.error('SSE hook error:', ev)
        }
        this.sse.onmessage = this.onMessage.bind(this)

        this.GL_ONMESSAGE_CBTAB = {
            'Cmd_Ready':        this.onReady.bind(this),
            'Cmd_StartSession': this.onStartSession.bind(this),
            'Cmd_StartStage':   this.onStartStage.bind(this),
            'Cmd_EndStage':     this.onEndStage.bind(this),
            'Cmd_EndSession':   this.onEndSession.bind(this),
            'Cmd_SubmitError':  this.onSubmitError.bind(this)
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


    onReady(msgObj) {
        console.info(`Session #${this.code} is ready.`)
    }

    onStartSession(msgObj) {
        console.info(`Session #${this.code} has started.`)
    }

    onStartStage(msgObj) {
        console.info(`Stage has started in session #${this.code}.`)
    }

    onEndStage(msgObj) {
        console.info(`Stage has ended in session #${this.code}.`)
    }

    onEndSession(msgObj) {
        console.info(`Session #${this.code} has finished.`)
    }

    onSubmitError(msgObj) {
        console.error(`Error while submitting image in session #${this.code}: ${msgObj.value}`)
    }
    

    close() {
        console.log('Closing SSE connection.')

        this.sse.close()
    }
}


