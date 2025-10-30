import random

from   dataclasses import dataclass


@dataclass
class Session:
    sessionCode: str = ''
    upperTab:    any = None
    lowerTab:    any = None
    stage:       int = 0


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
    

