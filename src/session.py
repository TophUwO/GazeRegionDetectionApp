# Session management.
from os                 import makedirs, listdir
from os.path            import isdir, exists
from random             import choices
from dataclasses        import dataclass
from json               import dumps
from queue              import Queue
from concurrent.futures import ThreadPoolExecutor
from time               import sleep


@dataclass
class Pair:
    """represents a 2-tuple"""
    upper: any = None
    lower: any = None

@dataclass
class Stage:
    """represents the per-stage state for a session"""
    id:        int  = -1
    canSupply: bool = False

@dataclass
class StageStatistics:
    """collects statistics regarding reasons for dropped data points"""
    nSucc:     int  = 0
    nFNoHead:  int  = 0
    nFEyesCl:  int  = 0
    nFOther:   int  = 0


class Client:
    """represents a session client (device)"""

    def __init__(self, session: str, role: str):
        self.sessionCode = session,
        self.roleId      = role
        self.queue       = Queue()

    def sendCommand(self, msg) -> None:
        """adds a command to the client's SSE queue"""
        jsonObj = dumps(msg, separators=[',', ':'])

        self.queue.put(jsonObj)


class Session:
    """represents a session state object"""

    def __init__(self, man, config, code):
        self.code       = code             # session code
        self.clients    = Pair(None, None) # clients
        self.hook       = None             # optional hook client
        self.stage      = Stage(-1, False) # current stage
        self.config     = config           # session config
        self.timer      = None             # stage timer
        self.lastIdx    = -1               # last session index
        self.man        = man              # session manager
        self.isFinished = False            # whether or not the session is finished
        
        self.stageStats = [StageStatistics() for i in range(len(self.config['stages']))] # stats for each stage


    def gotoNextStage(self) -> bool:
        stObj = None
        try:
            stObj = self.config['stages'][self.stage.id + 1]
        except IndexError:
            return False
        
        def int_finalizeStage(delay) -> None:
            """run when a stage ends"""
            sleep(delay)

            print(f'[SESS#{self.code}] Finished stage {self.config["stages"][self.stage.id]["id"]}.')
            self.sendCommand('any', 'Cmd_EndStage')
            self.sendCommandToHook('Cmd_EndStage')
            self.stage.canSupply = False

            # We might also have finished the session.
            if self.stage.id == self.config['stages'][len(self.config['stages']) - 1]['id']:
                self.sendCommand('any', 'Cmd_EndSession')
                self.sendCommandToHook('Cmd_EndSession')

                print(f'[SESS#{self.code}] Finished session #{self.code}.')
                self.endSession()
        
        self.stage = Stage(self.stage.id + 1, True)
        self.man._timers.submit(int_finalizeStage, stObj['time']) # Set the stage timer.

        print(f'[SESS#{self.code}] Started stage {stObj.get("id")} ... ending in {stObj.get("time")} seconds.')
        return True
        
    def registerClient(self, role: str) -> None:
        """registers a client and assigns role"""

        if role not in self.config['roleIds']:
            print(f'error: Unknown role \'{role}\'.')

            return
        
        if role == self.config.get('creatorRole'):
            self.clients.upper = Client(self.code, role)
        elif role == self.config.get('joinerRole'):
            self.clients.lower = Client(self.code, role)

    def createHook(self) -> None:
        """register hook client"""
        self.hook = Client(self.code, '')

    def destroyHook(self) -> None:
        """destroy hook client"""
        self.hook = None

    def unregisterClient(self, role: str) -> None:
        """remove client"""
        if role not in self.config['roleIds']:
            print(f'error: Unknown role \'{role}\'.')

            return
        
        if role == self.config.get('creatorRole'):
            self.clients.upper = None
        elif role == self.config.get('joinerRole'):
            self.clients.lower = None

    
    def getQueue(self, role) -> Queue | None:
        """get queue for client"""
        cl = self.clients.upper if role == self.config['creatorRole'] else self.clients.lower if role == self.config['joinerRole'] else None
        if cl is not None:
            return cl.queue
        
        return None
    
    def getHookQueue(self) -> Queue | None:
        """get hook client queue"""
        if self.hook is None:
            return None
        
        return self.hook.queue
    

    def sendCommand(self, roleId: str, cmd: str, value: any = None) -> None:
        """send an SSE command"""

        # Format message.
        msg = {
            'command': cmd,
            'value':   value
        }

        # If role is 'any', do a broadcast.
        if roleId == 'any':
            if self.clients.upper: self.clients.upper.sendCommand(msg)
            if self.clients.lower: self.clients.lower.sendCommand(msg)

            return
        
        cl = self.clients.upper if roleId == self.config['creatorRole'] else self.clients.lower if roleId == self.config['joinerRole'] else None
        if cl is None:
            print(f'error: Invalid role ID \'{roleId}\'.')

            return
        cl.sendCommand(msg)

    def sendCommandToHook(self, cmd: str, value: any = None) -> None:
        """send an SSE command to hook client"""

        if self.hook is None:
            return
        
        # Format and send message.
        msg = {
            'command': cmd,
            'value':   value
        }
        self.hook.sendCommand(msg)

    def endSession(self) -> None:
        """ends a session"""

        # Write command to stop SSE stream server-side.
        self.sendCommand('any', 'SysCmd_EndSession')
        self.sendCommandToHook('SysCmd_EndSession')

        # Write session stats file. */
        with open(f'files/stats/stats_{self.code}.json', 'w') as f:
            stats = {}
            for i, s in zip([i for i in range(0, len(self.config['stages']))], self.stageStats):
                stats[f'{i}'] = {
                    'succeeded': s.nSucc,
                    'failed': {
                        'nohead':     s.nFNoHead,
                        'eyesclosed': s.nFEyesCl,
                        'other':      s.nFOther
                    }
                }

            f.write(dumps(stats, indent=4))

        # Do not delete session because there might still be images that need to be processed or received.
        # self.man.deleteSession(self.code)
        self.isFinished = True


class SessionManager:
    """manages the sessions"""

    def __init__(self, config) -> None:
        self.sessionDict = {}
        self._config     = config
        self._timers     = ThreadPoolExecutor(64)

        # Add 'pseudo'-sessions for the ones already created. These are the ones that are already in files/raw.
        # Also add some global directory that store stuff from all sessions together.
        if not exists('files/pos'):   makedirs(f'files/pos')
        if not exists('files/stats'): makedirs(f'files/stats')
        if exists('files/raw'):
            for ent in listdir('files/raw'):
                if isdir(ent):
                    self.sessionDict[ent] = Session(self, self._config, ent)

                    # Make it so you cannot use that session any longer.
                    self.sessionDict[ent].isFinished = True


    def createSession(self) -> Session | None:
        """creates a new session"""

        def int_GenSessCode() -> str:
            return ''.join(choices('abcdef0123456789', k=6))

        # If no free sessions are left, we simply return an error.
        if len(self.sessionDict) == 2**24:
            print('error: No session codes left.')

            return None

        # Create the new session. Generate new session code until we got a code that does not refer to an already
        # existing session.
        while True:
            sess = Session(self, self._config, int_GenSessCode())

            # Add session.
            if sess.code in self.sessionDict:
                continue
            self.sessionDict[sess.code] = sess
            break

        # Create diretory to store raw data.
        makedirs(f'files/raw/{sess.code}')

        return sess

    def deleteSession(self, code: str) -> None:
        if code not in self.sessionDict:
            return

        self.sessionDict.pop(code)


    def getSession(self, code: str) -> Session | None:
        sessCode = code.lower()

        return self.sessionDict.get(sessCode, None)
    

