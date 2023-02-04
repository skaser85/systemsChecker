import os
import subprocess
from dataclasses import dataclass
from enum import Enum

class WinServiceState(Enum):
    Uninitialized = 0
    Stopped = 1
    StartPending = 2
    StopPending = 3
    Running = 4
    ContinuePending = 5
    PausePending = 6
    Paused = 7

@dataclass
class WinService:
    name: str
    server_name: str = ''
    display_name: str = ''
    state: WinServiceState = WinServiceState.Uninitialized

    def __post_init__(self):
        if len(self.server_name) == 0:
            self.server_name = os.environ['COMPUTERNAME']
        self.display_name = self.get_display_name()
        self.state = self.get_state()

    def sc(self, sc_cmd: str) -> str:
        if len(self.server_name) == 0:
            check = subprocess.run(['sc', sc_cmd, self.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            check = subprocess.run(['sc', rf'\\{self.server_name}', sc_cmd, self.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check.returncode == 0:
            return check.stdout.decode()
        else:
            raise SystemError(check.stdout.decode())

    def get_display_name(self) -> str:
        svc_details = self.sc('getdisplayname')
        return [l.strip() for l in svc_details.split('\n') if len(l.strip()) > 0][-1].split('=')[-1].strip()

    def get_state(self) -> str:
        svc_details = self.sc('query')
        data = [l.strip() for l in svc_details.split('\n') if len(l.strip()) > 0]
        return data[2].split(':')[-1].strip().split(' ')[0].strip()

if __name__ == '__main__':
    print(WinService('Razer Synapse Service'))