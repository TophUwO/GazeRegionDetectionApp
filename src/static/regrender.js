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

                /* Taken from: https://stackoverflow.com/a/33082682 */
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

    destroy() {
        this.endDraw()
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
        
        const didHitX   = this.x - this.r <= left || this.x + this.r >= right
        const didHitY   = this.y - this.r <= top  || this.y + this.r >= bottom

        /* In order to cover more ground, we must randomize the angle of reflection a bit. Our max. deviation is ±15°. */
        const deviation = (Math.random() - 0.5) * (Math.PI / 6)

        /* Before we bounce, we clip the ball into the box so it does not cause funny visual glitches. */
        if (this.x - this.r < left)   this.x = left   + this.r
        if (this.x + this.r > right)  this.x = right  - this.r
        if (this.y - this.r < top)    this.y = top    + this.r
        if (this.y + this.r > bottom) this.y = bottom - this.r

        let speed = Math.hypot(this.vx, this.vy)
        let angle = Math.atan2(this.vy, this.vx)
        {
            if (didHitX && !didHitY)
                angle = Math.PI - angle + deviation
            else if (didHitY && !didHitX)
                angle = -angle + deviation
            else if (didHitX && didHitY)
                angle = angle + Math.PI
        }

        /* Update the velocity vector. */
        this.vx = Math.cos(angle) * speed
        this.vy = Math.sin(angle) * speed
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


