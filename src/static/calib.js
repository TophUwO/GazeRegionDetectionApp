import { IntermediateStage } from "./interm.js"


/**
 * 
 */
export class IntermediateCalibrationStage extends IntermediateStage {
    isInCalib   = false
    frameHandle = -1
    cvHandle    = document.getElementById('canvCalibrationOverlay')
    srcVideo    = null

    CAPTION     = 'Calibration'
    TEXT        = 'This application requires the person in front of the screen to position themselves so that the ' + 
                  'entire face sits comfortably around the vertical center of the frame. Horizontal movement — as long as ' +
                  'the entire face is comfortably (min. 300px distance to any edge) inside the frame — is allowed. Make ' + 
                  'sure that nothing is obstructing your face, e.g. hair, other objects, hands, etc. Also make sure that ' + 
                  'you are in a bright room with relatively soft lighting. Avoid bright light sources behind you.'

    /**
     */
    startIntermediateStage(srcVideo) {
        this.srcVideo  = srcVideo
        this.isInCalib = true
        {
            this.elemCont.style.display = 'block'

            this.cvHandle.width  = 800
            this.cvHandle.height = 600

            this.frameHandle = requestAnimationFrame(this.showCalibration.bind(this))
        }

        super.startIntermediateStage()
    }

    /**
     * 
     */
    endIntermediateStage() {
        this.isInCalib = false
        cancelAnimationFrame(this.frameHandle)

        this.elemCont.style.display = 'none'
        
        this.frameHandle = -1
        this.ctrlHandle  = null
        this.srcVideo    = null

        super.endIntermediateStage()
    }

    /**
     * 
     */
    showCalibration() {
        if (!this.isInCalib)
            return

        const ctx = this.cvHandle.getContext('2d')
        const w   = this.cvHandle.width
        const h   = this.cvHandle.height
        {
            ctx.drawImage(this.srcVideo, 0, 0, this.cvHandle.width, this.cvHandle.height)

            ctx.strokeRect(0, 0.25*h, w, 0.5*h)
        }
        
        this.frameHandle = requestAnimationFrame(this.showCalibration.bind(this))
    }
}


