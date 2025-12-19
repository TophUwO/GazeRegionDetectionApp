/**
 */
export class RegionRenderer {
    constructor(ctrl, config) {
        this.ctrl      = ctrl
        this.cfg       = config
        this.isDraw    = false
        this.startTime = -1
        {
            /* Create the ball in the middle of the region. */
            this.ball = new Ball(
                this.cfg.region,
                (this.cfg.region.left + (this.cfg.region.right  - this.cfg.region.left) * 0.5) * window.innerWidth,
                (this.cfg.region.top  + (this.cfg.region.bottom - this.cfg.region.top)  * 0.5) * window.innerHeight,
                this.cfg.region.objrad,
                this.cfg.speed
            )

            this.cvArea = document.getElementById('canvArea')
            {
                this.cvArea.width  = window.innerWidth
                this.cvArea.height = window.innerHeight
            }
        }
    }


    /**
     */
    draw() {
        if (!this.isDraw)
            return

        this.ball.move()

        const ctx = this.cvArea.getContext('2d')
        {
            /* Clear the entire screen. */
            ctx.clearRect(0, 0, this.cvArea.width, this.cvArea.height)

            /* Draw elements. */
            ctx.fillStyle = this.cfg.region.color
            ctx.fillRect(
                this.cfg.region.left                            * this.cvArea.width,
                this.cfg.region.top                             * this.cvArea.height,
                (this.cfg.region.right  - this.cfg.region.left) * this.cvArea.width,
                (this.cfg.region.bottom - this.cfg.region.top)  * this.cvArea.height
            )
            this.ball.draw(ctx, this.cfg.region.objcol)

            /* Draw timer inside the current region. */
            const currTime = Date.now() / 1000
            {
                const remMins = Math.trunc((this.cfg.time - (currTime - this.startTime)) / 60)
                const remSecs = Math.trunc((this.cfg.time - (currTime - this.startTime)) % 60)
                const remTime = `${String(remMins).padStart(2, '0')}:${String(remSecs).padStart(2, '0')}`

                ctx.fillStyle    = 'white'
                ctx.font         = '36px monospace'
                ctx.textAlign    = 'center'
                ctx.textBaseline = 'middle'
                {
                    ctx.fillText(
                        remTime,
                        (this.cfg.region.left + (this.cfg.region.right  - this.cfg.region.left) * 0.5) * window.innerWidth,
                        (this.cfg.region.top  + (this.cfg.region.bottom - this.cfg.region.top)  * 0.5) * window.innerHeight
                    )
                }
            }
        }

        this.frame = requestAnimationFrame(this.draw.bind(this))
    }

    /**
     * 
     */
    beginDraw() {
        if (this.isDraw != true) {
            this.isDraw    = true
            this.startTime = Date.now() / 1000

            this.frame = requestAnimationFrame(this.draw.bind(this))
        }
    }

    /**
     */
    endDraw() {
        if (this.isDraw != false) {
            cancelAnimationFrame(this.frame)
            
            this.isDraw = false
            this.frame  = -1
        }
    }
}


/**
 */
class Ball {
    /**
     * 
     * @param {*} startX 
     * @param {*} startY 
     * @param {*} radius 
     */
    constructor(region, startX, startY, radius, speed) {
        this.x   = startX
        this.y   = startY
        this.r   = radius
        this.reg = region
        this.vx  = speed
        this.vy  = speed
    }


    /**
     */
    move() {
        /* Update position. */
        this.x += this.vx
        this.y += this.vy

        /* Check if we bounced on any side. */
        const left   = this.reg.left   * window.innerWidth
        const top    = this.reg.top    * window.innerHeight
        const right  = this.reg.right  * window.innerWidth
        const bottom = this.reg.bottom * window.innerHeight

        /* Have we bounced left or right side? */
        if (this.x - this.r <= left || this.x + this.r >= right)
            this.vx = -this.vx
        /* Have we bounced top or bottom side? */
        if (this.y - this.r <= top || this.y + this.r >= bottom)
            this.vy = -this.vy
    }

    /**
     * 
     * @param {CanvasRenderingContext2D} ctx 2D rendering context for the area canvas 
     * @param {String}                   col color to fill the ball with
     */
    draw(ctx, col) {
        ctx.beginPath()
        {
            ctx.fillStyle = col

            ctx.arc(this.x, this.y, this.r, 0, 2 * Math.PI)
        }
        ctx.fill()
    }
}


