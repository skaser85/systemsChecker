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
    is_running: bool = False

    def __post_init__(self):
        if len(self.server_name) == 0:
            self.server_name = os.environ['COMPUTERNAME']
        self.display_name = self.get_display_name()
        self.update()

    def sc(self, sc_cmd: str) -> str:
        output = subprocess.run(['sc', rf'\\{self.server_name}', sc_cmd, self.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode == 0:
            return output.stdout.decode()
        else:
            raise SystemError(output.stdout.decode())

    def get_display_name(self) -> str:
        svc_details = self.sc('getdisplayname')
        return [l.strip() for l in svc_details.split('\n') if len(l.strip()) > 0][-1].split('=')[-1].strip()

    def get_state(self) -> str:
        svc_details = self.sc('query')
        data = [l.strip() for l in svc_details.split('\n') if len(l.strip()) > 0]
        return list(WinServiceState)[int(data[2].split(':')[-1].strip().split(' ')[0].strip())]

    def update(self):
        self.state = self.get_state()
        self.is_running = self.state == WinServiceState.Running

if __name__ == '__main__':
    rss = WinService('Razer Synapse Service')
    print(rss.get_state())