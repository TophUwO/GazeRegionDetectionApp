import random

from   dataclasses import dataclass


GL_SESS_TAB: dict[int, dict] = {
        0: { 'active': None },
        1: { 'active': 'H' },
        2: { 'active': 'H' },
        3: { 'active': 'L' },
        4: { 'active': None },
        5: { 'active': 'H' }
    }

@dataclass
class Session:
    sessionCode: str  = ''
    upperTab:    any  = None
    lowerTab:    any  = None
    stage:       int  = 0
    canSupply:   bool = False

    async def sendActive(self, jsonObj: str) -> None:
        # Get active.
        activeId = GL_SESS_TAB.get(self.stage, None)
        if activeId is None:
            return
        
        # Determine tab.
        tab = None
        match activeId['active']:
            case 'H': tab = self.upperTab
            case 'L': tab = self.lowerTab

        # Send.
        await tab.send(jsonObj)

    async def sendPassive(self, jsonObj: str) -> None:
        # Get active.
        activeId = GL_SESS_TAB.get(self.stage, None)
        if activeId is None:
            return
        
        # Determine tab.
        tab = None
        match activeId['active']:
            case 'L': tab = self.upperTab
            case 'H': tab = self.lowerTab

        # Send.
        await tab.send(jsonObj)

class SessionManager:
    def __init__(self) -> None:
        self.sessionDict: dict[str, Session] = {}

    def createSession(self) -> Session:
        def int_GenSessCode() -> str:
            return ''.join(random.choices('abcdef0123456789', k=6))
        
        # Create the new session.
        while True:
            sess: Session = Session(sessionCode=int_GenSessCode(), upperTab=None, lowerTab=None)

            # Add session.
            if sess.sessionCode in self.sessionDict:
                continue
            self.sessionDict[sess.sessionCode] = sess
            break

        # All good.
        return sess
    
    def deleteSession(self, code: str) -> None:
        if code not in self.sessionDict:
            return
        
        self.sessionDict.pop(code)
    
    def getSession(self, code: str) -> Session | None:
        return self.sessionDict.get(code, None)
    

