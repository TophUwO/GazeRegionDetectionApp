export class ImageSubmitter {
    constructor(canvas, stream, video) {
        this.canvas = canvas
        this.stream = stream
        this.video  = video
    }

    static async Create(imgWidth, imgHeight) {
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
                        }
                    }
                })
                video.srcObject = stream

                /* Wait for a useable frame. */
                await video.play();
            } catch (err) {
                console.log(`Could not access camera. Reason: ${err}.`)

                return null
            }

            /* Set the size of the canvas to the actual video stream dimensions. */
            canvas.width  = video.videoWidth
            canvas.height = video.videoHeight
        }

        return new ImageSubmitter(canvas, stream, video)
    }

    async submitImage() {
        ctx = this.canvas.getContext('2d')
        {
            ctx.drawImage(this.video, 0, 0)
        }

        return this.canvas.toDataURL('image/jpeg', 0.9)
    }

    destroy() {
        if (!this.stream)
            return;

        this.stream.getTracks().forEach(element => element.stop());
    }
}


