from os          import makedirs, listdir
from os.path     import isdir, exists
from random      import choices
from dataclasses import dataclass, field
from secrets     import token_hex


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
    idx:         int   = 0
    stage:       Stage = field(default_factory=lambda: Stage(None, False, False))

    tokens = {}

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
        self.idx      = 0
        try:
            self.stage = GL_SESSTAB[self.stageId]
        except KeyError:
            self.stageId = 9
            self.stage   = Stage(None, False, True)

            pass
        
    def registerAsRole(self, role: str, ws: any) -> None:
        if role not in self.config['roleIds']:
            print(f'error: Unknown role \'{role}\'.')

            return
        
        # Register tablet.
        match role:
            case self.config.get('creatorRole'): self.tabs.upper = ws
            case self.config.get('joinerRole'):  self.tabs.lower = ws

        # Create first submission token.
        self.generateTokenForRole(role)


    async def sendRole(self, roleId: str, cmd: str, value: any = None) -> None:
        # Format message.
        msg = f'''
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
        
        tab: any = self.tabs.upper if roleId == self.config['creatorRole'] else self.tabs.lower if roleId == self.config['joinerRole'] else None
        if tab is None:
            print(f'error: Invalid role ID \'{roleId}\'.')

            return
        await tab.send(msg)

    def generateTokenForRole(self, roleId: str) -> str:
        tok = token_hex(32)

        self.tokens[roleId] = tok
        return tok


class SessionManager:
    def __init__(self) -> None:
        self.sessionDict = {}
        self._config     = {}

        # Add 'pseudo'-sessions for the ones already created. These are the ones that are already in files/raw.
        if exists('files/raw'):
            for ent in listdir('files/raw'):
                if isdir(ent):
                    self.sessionDict[ent] = Session(sessionCode=ent)


    def createSession(self) -> Session:
        def int_GenSessCode() -> str:
            return ''.join(choices('abcdef0123456789', k=6))
        
        # If no free sessions are left, we simply return an error.
        if len(self.sessionDict) == 2**24:
            print('error: No session codes left.')

            return None

        # Create the new session.
        while True:
            sess = Session(sessionCode=int_GenSessCode())

            # Add session.
            if sess.sessionCode in self.sessionDict:
                continue
            self.sessionDict[sess.sessionCode] = sess
            break

        # Create directories.
        makedirs(f'files/raw/{sess.sessionCode}')
        makedirs(f'files/proc/{sess.sessionCode}')

        # All good.
        return sess
    
    def deleteSession(self, code: str) -> None:
        if code not in self.sessionDict:
            return
        
        self.sessionDict.pop(code)
    
    def getSession(self, code: str) -> Session | None:
        sessCode = code.lower()

        return self.sessionDict.get(sessCode, None)
    

