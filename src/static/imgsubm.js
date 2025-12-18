/**
 */
export class ImageSubmitter {
    /**
     * 
     * @param {*} ctrl 
     * @param {*} canvas 
     * @param {*} stream 
     * @param {*} video 
     * @param {*} ival 
     */
    constructor(ctrl, canvas, stream, video, ival) {
        this.ctrl     = ctrl
        this.canvas   = canvas
        this.stream   = stream
        this.video    = video
        this.submIval = -1
        this.ival     = ival
        this.stageId  = -1

        /* Create worker thread for image creation. This is so that the ball does not lag due to image processing. */
        this.worker = new Worker('./static/imgmk.js')
    }


    /**
     * 
     * @param {*} stageId 
     */
    startImageSubmitting(stageId) {
        this.submIdx  = 0
        this.stageId  = stageId
        this.submIval = setInterval(this.submitImage.bind(this), this.ival)
    }

    /**
     * 
     */
    endImageSubmitting() {
        if (this.submIval != -1)
            clearInterval(this.submIval)

        this.stageId  = -1
        this.submIval = -1
    }

    /**
     */
    destroy() {
        if (!this.stream)
            return

        this.stream.getTracks().forEach(element => element.stop());
        this.endImageSubmitting()
    }


    /**
     * 
     */
    submitImage() {
        createImageBitmap(this.video).then(bmp => {
            this.worker.postMessage({
                bmp,
                idx:    this.submIdx++,
                ballX:  -1,
                ballY:  -1,
                code:   this.ctrl.sessionCode,
                region: this.stageId,
                time:   Date.now()
            }, [bmp])
        })
    }


    /**
     * 
     * @param {*} ctrl 
     * @param {*} imgWidth 
     * @param {*} imgHeight 
     * @param {*} ival 
     * @returns 
     */
    static async Create(ctrl, imgWidth, imgHeight, ival) {
        let stream

        const canvas = document.createElement('canvas')
        const video  = document.createElement('video')
        {
            try {
                /* Start camera. */
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        width:      { ideal: imgWidth  },
                        height:     { ideal: imgHeight },
                        facingMode: { 
                            ideal: 'user'
                        },
                        frameRate: Math.trunc(1000.0 / ival) + 1.0
                    }
                })
                video.srcObject = stream

                /* Wait for a useable frame. */
                await video.play();
            } catch (err) {
                console.log(`Could not access camera. Reason: ${err}.`)

                //return null
            }

            /* Set the size of the canvas to the actual video stream dimensions. */
            canvas.width  = video.videoWidth
            canvas.height = video.videoHeight
        }

        return new ImageSubmitter(ctrl, canvas, stream, video, ival)
    }
}


