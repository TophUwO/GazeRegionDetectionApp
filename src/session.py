from os          import makedirs, listdir
from os.path     import isdir, exists
from random      import choices
from dataclasses import dataclass
from asyncio     import create_task, sleep


@dataclass
class Pair:
    upper: any = None
    lower: any = None

@dataclass
class Stage:
    id:        int  = -1
    canSupply: bool = False

class Client:
    def __init__(self, session: str, ws: any, role: str):
        self.sessionCode = session,
        self.wsObj       = ws
        self.roleId      = role

    async def sendCommand(self, msg) -> None:
        await self.wsObj.send(msg)


class Session:
    def __init__(self, config, code):
        self.code    = code
        self.clients = Pair(None, None)
        self.stage   = Stage(-1, False)
        self.config  = config
        self.timer   = None
        self.lastIdx = -1

    def gotoNextStage(self) -> bool:
        stObj = None
        try:
            stObj = self.config['stages'][self.stage.id + 1]
        except IndexError:
            return False
        
        self.stage = Stage(self.stage.id + 1, True)
        create_task(self.disableSupplyAfterDelay(stObj['time']))

        print(f'[SESS#{self.code}] Started stage {stObj.get("id")} ... ending in {stObj.get("time")} seconds.')
        return True
        
    def registerClient(self, role: str, ws: any) -> None:
        if role not in self.config['roleIds']:
            print(f'error: Unknown role \'{role}\'.')

            return
        
        if role == self.config.get('creatorRole'):
            self.clients.upper = Client(self.code, ws, role)
        elif role == self.config.get('joinerRole'):
            self.clients.lower = Client(self.code, ws, role)

    def unregisterClient(self, role: str) -> None:
        if role not in self.config['roleIds']:
            print(f'error: Unknown role \'{role}\'.')

            return
        
        if role == self.config.get('creatorRole'):
            self.clients.upper = None
        elif role == self.config.get('joinerRole'):
            self.clients.lower = None
    
    def setLastIndex(self, idx) -> None:
        self.lastIdx = idx


    def isEmpty(self) -> bool:
        return self.clients.upper is None and self.clients.lower is None
    

    async def sendCommand(self, roleId: str, cmd: str, value: any = None) -> None:
        # Format message.
        msg = f'''
            {{
                "command": "{cmd}",
                "value":   "{value}"
            }}
        '''

        # If role is 'any', do a broadcast.
        if roleId == 'any':
            if self.clients.upper: await self.clients.upper.sendCommand(msg)
            if self.clients.lower: await self.clients.lower.sendCommand(msg)

            return
        
        cl = self.clients.upper if roleId == self.config['creatorRole'] else self.clients.lower if roleId == self.config['joinerRole'] else None
        if cl is None:
            print(f'error: Invalid role ID \'{roleId}\'.')

            return
        await cl.sendCommand(msg)

    async def disableSupplyAfterDelay(self, delay) -> None:
        await sleep(delay)

        self.stage.canSupply = False

        print(f'[SESS#{self.code}] Finished stage {self.config["stages"][self.stage.id]["id"]}.')
        await self.sendCommand('any', 'Cmd_EndStage')


class SessionManager:
    def __init__(self, config) -> None:
        self.sessionDict = {}
        self._config     = config

        # Add 'pseudo'-sessions for the ones already created. These are the ones that are already in files/raw.
        if exists('files/raw'):
            for ent in listdir('files/raw'):
                if isdir(ent):
                    self.sessionDict[ent] = Session(self._config, ent)


    def createSession(self) -> Session:
        def int_GenSessCode() -> str:
            return ''.join(choices('abcdef0123456789', k=6))

        # If no free sessions are left, we simply return an error.
        if len(self.sessionDict) == 2**24:
            print('error: No session codes left.')

            return None

        # Create the new session.
        while True:
            sess = Session(self._config, int_GenSessCode())

            # Add session.
            if sess.code in self.sessionDict:
                continue
            self.sessionDict[sess.code] = sess
            break

        # Create directories.
        makedirs(f'files/raw/{sess.code}')
        makedirs(f'files/proc/{sess.code}')

        # All good.
        return sess

    def deleteSession(self, code: str) -> None:
        if code not in self.sessionDict:
            return

        self.sessionDict.pop(code)

    def getSession(self, code: str) -> Session | None:
        sessCode = code.lower()

        return self.sessionDict.get(sessCode, None)
    

