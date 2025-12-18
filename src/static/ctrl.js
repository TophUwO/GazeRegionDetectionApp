import { ImageSubmitter               } from './imgsubm.js'
import { SessionWebSocket             } from './ws.js'
import { IntermediateCalibrationStage } from './calib.js'
import { RegionRenderer               } from './regrender.js'

import { 
    IntermediateReadyStage,
    IntermediateEndStage,
    EndStage,
    IntermediateInstStage
} from './interm.js'            


/**
 */
const IntermediateViewType = Object.freeze({
    READY:        [IntermediateReadyStage,       'READY',        0, 'CALIBRATION'  ],
    CALIBRATION:  [IntermediateCalibrationStage, 'CALIBRATION',  1, 'INSTRUCTIONS' ],
    INSTRUCTIONS: [IntermediateInstStage,        'INSTRUCTIONS', 2, undefined,     ],
    IEND:         [IntermediateEndStage,         'IEND',         3, 'INSTRUCTIONS' ],
    END:          [EndStage,                     'END',          4, undefined      ]
})


/**
 */
export class SessionControl {
    /**
     */
    constructor() {
        this.config         = null
        this.imgSubmitter   = null
        this.currViewId     = null
        this.roleId         = null
        this.sessionCode    = null
        this.websocket      = null
        this.currIntermView = null
        this.calibMngt      = null
        this.currIntermObj  = null
        this.regRender      = null
        this.currStIdx      = -1

        try {
            this.initializeInteractiveElements()
        } catch (err) {
            this.displayFatalError(err.message)
        }
    }


    /**
     */
    initializeInteractiveElements() {
        const crBtn  = document.getElementById('btnCreateSession')
        const jnBtn  = document.getElementById('btnJoinSession')
        const cntBtn = document.getElementById('btnIntermCont')

        /* Create listener for the 'Create session' button in the 'Welcome' view. */
        crBtn.addEventListener('click', async() => {
            const res  = await fetch('/api/create', {
                method: 'POST'
            })
            const data = await res.json()

            if (data.type == 'ok') {
                this.roleId      = data.payload.role
                this.sessionCode = data.payload.code

                /* Create websocket. */
                this.websocket = await SessionWebSocket.Create(this, this.roleId, this.sessionCode)

                /* Show session code so that the user can enter it in another client supposed to join the session. */
                this.switchToView('viewCodeDisplay')
                {
                    const codeDispLabel = document.getElementById('lblCodeDisplay')
                    if (codeDispLabel == null) {
                        this.displayFatalError('Could not display session code.')

                        return
                    }

                    codeDispLabel.textContent = `Session Code: ${this.sessionCode}`
                }

                return
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

                    return
                }
            }

            const res  = await fetch('/api/join', { 
                method:  'POST',
                headers: {
                    'session': code
                }
            })
            const data = await res.json()

            if (data.type == 'ok') {
                this.roleId      = data.payload.role
                this.sessionCode = data.payload.code

                /* Create websocket. */
                this.websocket = await SessionWebSocket.Create(this, this.roleId, this.sessionCode)

                this.switchToIdleView()
                return
            }

            /* Error occurred. */
            this.displayFatalError(data.desc)
        })

        /**
         */
        cntBtn.addEventListener('click', async() => {
            const nextView = SessionControl.GetNextIntermediateView(this.currIntermView)

            /* Do we need to start a stage. */
            if (nextView == null) {
                const res = await fetch('/api/advance', {
                    method:  'POST',
                    headers: {
                        'session': this.sessionCode
                    }
                })
                const data = await res.json()

                if (data.type !== 'ok')
                    this.displayFatalError(data.desc)
                return
            }

            /* Only change intermediate view. */
            this.switchToIntermediateView(nextView)
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

    /**
     */
    switchToIdleView() {
        this.switchToView('viewIdle')
    }

    /**
     * @todo intermViewType must be one of the values of 'IntermediateViewType' directly or else it will not match
     */
    switchToIntermediateView(intermViewType) {
        const [cls, id, n, _] = intermViewType
        {
            if (this.currIntermObj != null)
                this.currIntermObj.endIntermediateStage()

            this.currIntermObj = new cls(this)

            switch (cls) {
                case IntermediateCalibrationStage:
                    this.currIntermObj.startIntermediateStage(this.imgSubmitter.video)

                    break
                default:
                    this.currIntermObj.startIntermediateStage()
            }
            this.currIntermView = intermViewType
        }

        /* Switch to the intermediate view. */
        this.switchToView('viewInterm')
    }


    /**
     * 
     * @param {*} reason 
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
        if (this.imgSubmitter != null) this.imgSubmitter.destroy()
        if (this.calibMngt != null)    this.calibMngt.destroy()
    }

    
    /**
     * 
     * @param {*} msgObj 
     */
    onStartStage(msgObj) {
        this.currStIdx += 1
        {
            if (this.currStIdx >= this.config.stages.length) {
                this.displayFatalError('Internal Error: No more stages left but command to start stage was issued.')

                return
            }

            this.currStObj = this.config.stages[this.currStIdx]

            /* Start image submitter on creator client. */
            if (this.roleId == this.config.creatorRole)
                this.imgSubmitter.startImageSubmitting(this.currStObj.id)

            /* Initialize region renderer on the active client but only if we got a region to render. */
            if (this.currStObj.region != null && this.currStObj.region.roleId == this.roleId) {
                this.regRender = new RegionRenderer(this, this.currStObj)

                this.switchToView('viewStage')
                return
            }
        }

        /* On the inactive client, we simply switch to the idle view. */
        this.switchToIdleView()
    }


    /**
     * 
     * @param {*} msgObj 
     */
    onEndStage(msgObj) {
        const activeRole = this.currStObj.region !== undefined ? this.currStIdx.roleId : this.config.creatorRole

        /* Active client must stop renderer. */
        if (this.roleId === activeRole) {
            if (this.regRender !== null)
                this.regRender.endDraw()

            this.regRender = null
        }

        /* Creator client must display (intermediate) end screen. */
        if (this.roleId == this.config.creatorRole) {
            this.imgSubmitter.endImageSubmitting()

            if (this.currStObj === this.config.stages[this.config.stages.length - 1]) {
                this.switchToIntermediateView(IntermediateViewType.END)

                /* Destroy the session controller. This will also stop the camera. */
                this.destroy()
                return
            }

            this.switchToIntermediateView(IntermediateViewType.IEND)
            return
        }

        /* Go into idle state on inactive tablet. */
        this.switchToIdleView()
        this.destroy()
    }

    /**
     */
    onReady() {
        if (this.roleId != this.config.creatorRole)
            return

        this.switchToIntermediateView(IntermediateViewType.READY)
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
        imgSubmit = await ImageSubmitter.Create(sessCtrl, 1920, 1080, config.ival)
        {
            if (imgSubmit == null)
                throw new Error(
                    'Could not initialize image submitter component. Perhaps no camera is installed or the ' +
                    'application is not allowed to use it.'
                )
        }

        /* All good. Set instance properties. */
        sessCtrl.config       = config
        sessCtrl.imgSubmitter = imgSubmit

        return [sessCtrl, null]
    }

    /**
     * 
     * @param {*} curr 
     * @returns 
     */
    static GetNextIntermediateView(curr) {
        const [_, __, ___, next] = curr

        if (next == undefined)
            return null
        return IntermediateViewType[next]
    }
}


