/**
 * 
 */
export class IntermediateStage {
    ctrlHandle = null
    intermView = document.getElementById('viewInterm')
    intermH1   = document.getElementById('h1IntermCaption')
    intermText = document.getElementById('lblIntermText')
    elemCont   = document.getElementById('divIntermElementsContainer')

    /**
     * 
     */
    CAPTION    = '--- placeholder caption ---'
    /**
     * 
     */
    TEXT       = '--- placeholder text ---'


    /**
     * 
     */
    constructor(ctrl) {
        if (ctrl == null || ctrl == undefined)
            throw new Error('Could not initialize intermediate stage due to an internal error.')

        this.ctrlHandle = ctrl
    }


    /**
     * 
     */
    startIntermediateStage() {
        this.ctrl.switchToView('viewInterm')
        {
            this.intermH1.textContent   = this.CAPTION
            this.intermText.textContent = this.TEXT
        }
    }

    /**
     * 
     */
    endIntermediateStage() {
        
    }
}



/**
 * 
 */
export class IntermediateEndStage extends IntermediateStage  {
    CAPTION = 'Intermission'
    TEXT    = 'This stage has ended. There are more stages to come.'
}


/**
 * 
 */
export class EndStage extends IntermediateStage {
    CAPTION = 'Finished'
    TEXT    = 'You have successfully completed the collection of the training data. Thank you for your cooperation. You can now close this page on all clients or refresh to have another go.'
}


/**
 * 
 */
export class IntermediateReadyStage extends IntermediateStage {
    CAPTION = 'Ready'
    TEXT    = 'Session has successfully been initialized. Data collection can now be started.'
}


/**
 * 
 */
export class IntermediateInstStage extends IntermediateStage {
    CAPTION = 'inst caption'
    TEXT    = 'inst text'
}


