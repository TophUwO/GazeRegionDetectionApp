export class CalibrationManagement {
    isInCalib   = false
    frameHandle = -1


    /**
     * 
     * @param {*} srcVideo 
     */
    startCalibration(srcVideo) {
        this.isInCalib = true
        {
            this.frameHandle = requestAnimationFrame(this.showCalibration.bind(this))
        }
    }

    /**
     * 
     */
    endCalibration() {
        cancelAnimationFrame(this.frameHandle)

        this.isInCalib   = false
        this.frameHandle = -1
    }

    /**
     * 
     */
    showCalibration() {
        if (!this.isInCalib)
            return
        
        this.frameHandle = requestAnimationFrame(this.showCalibration.bind(this))
    }

    /**
     */
    destroy() {
        if (this.isInCalib)
            this.endCalibration()
    }
}


