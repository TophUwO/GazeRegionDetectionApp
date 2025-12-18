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
                  'entire face sits comfortably in the red box. Inside this box, movement is permitted and explicitly ' +
                  'encouraged.'

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


