/**
 */
export class RegionRenderer {
    constructor(ctrl, config) {
        this.ctrl   = ctrl
        this.cfg    = config
        this.isDraw = true
        {
            /* Create the ball in the middle of the region. */
            this.ball = new Ball(
                this,
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
            this.frame = requestAnimationFrame(this.draw.bind(this))
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
        }

        this.frame = requestAnimationFrame(this.draw.bind(this))
    }

    /**
     */
    endDraw() {
        cancelAnimationFrame(this.frame)
        {
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
        this.v   = speed
        this.reg = region
        this.p   = 0.1
    }


    /**
     */
    move() {
        this.x += Math.cos(this.p) * this.v
        this.y += Math.sin(this.p) * this.v

        // TODO: bounce ball
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


