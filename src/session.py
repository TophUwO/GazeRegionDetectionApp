from random      import *
from dataclasses import dataclass, field


@dataclass
class Pair:
    upper: any = None
    lower: any = None

@dataclass
class Stage:
    activeId:  str  = None
    canSupply: bool = False
    isFinal:   bool = False

@dataclass
class Session:
    sessionCode: str   = ''
    tabs:        Pair  = field(default_factory=lambda: Pair(None, None))
    stageId:     int   = 0
    stage:       Stage = field(default_factory=lambda: Stage(None, False, False))

    def advanceStage(self) -> None:
        GL_SESSTAB: dict[int, Stage] = {
            0: Stage(None, False, False),
            1: Stage(None, False, False),
            2: Stage('H',  True,  False),
            3: Stage('H',  False, False),
            4: Stage('H',  True,  False),
            5: Stage('L',  False, False),
            6: Stage('L',  True,  False),
            7: Stage('H',  False, False),
            8: Stage('H',  True,  False),
            9: Stage(None, False, True)
        }

        self.stageId += 1
        try:
            self.stage = GL_SESSTAB[self.stageId]
        except KeyError:
            self.stageId = 9
            self.stage   = Stage(None, False, True)

            pass
        
    def registerAsRole(self, role: str, ws: any) -> None:
        if role not in ['H', 'L']:
            print(f'error: Unknown role \'{role}\'.')

            return
        
        # Register tablet.
        match role:
            case 'H': self.tabs.upper = ws
            case 'L': self.tabs.lower = ws

    async def sendRole(self, roleId: str, cmd: str, value: any) -> None:
        # Format message.
        msg: str = f'''
            {{
                "command": "{cmd}",
                "value":   "{value}"
            }}
        '''

        # If role is 'any', do a broadcast.
        if roleId == 'any':     
            await self.tabs.upper.send(msg)
            await self.tabs.lower.send(msg)

            return
        
        tab: any = self.tabs.upper if roleId == 'H' else self.tabs.lower if roleId == 'L' else None
        if tab is None:
            print(f'error: Invalid role ID \'{roleId}\'.')

            return
        await tab.send(msg)


class SessionManager:
    def __init__(self) -> None:
        self.sessionDict: dict[str, Session] = {}

    def createSession(self) -> Session:
        def int_GenSessCode() -> str:
            return ''.join(choices('abcdef0123456789', k=6))
        
        # Create the new session.
        while True:
            sess: Session = Session(sessionCode=int_GenSessCode())

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
    

