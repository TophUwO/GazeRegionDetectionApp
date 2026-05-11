/**
 * @param {*} msg 
 */
self.onmessage = async(msg) => {
    const s = performance.now();

    const {
        bmp,
        idx,
        ballX,
        ballY,
        code,
        region,
        time
    } = msg.data

    const cvOff = new OffscreenCanvas(1920, 1080)
    const ctx   = cvOff.getContext('2d')
    {
        ctx.drawImage(bmp, 0, 0, 1920, 1080)
    }

    const blob = await cvOff.convertToBlob({type: 'image/jpeg', quality: 0.9 })
    const form = new FormData()
    {
        form.append('image',   blob, 'IMG')
        form.append('session', code)
        form.append('index',   idx)
        form.append('objX',    ballX)
        form.append('objY',    ballY)
        form.append('region',  region)
        form.append('time',    time)
    }

    const res = fetch('/api/submit', {
        method:  'POST',
        headers: {
            'session': code
        },
        body:    form,
    })
    //const data = await res.json()

    //if (data.type != 'ok')
    //    console.error(`Could not submit image. Reason: ${data.desc}`)

    const e = performance.now();
    const t = e - s;
    //if (t > 100)
        console.log(`Making image ${idx} took too long! (${t} ms.)`)
}


