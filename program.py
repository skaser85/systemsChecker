from __future__ import annotations
from typing import List
import os
import subprocess
from dataclasses import dataclass, field

def get_tasklist(server_name: str):
    output = subprocess.run(['tasklist', '/s', rf'\\{server_name}', '/fo', 'csv', '/nh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if output.returncode == 0:
        return output.stdout.decode()
    else:
        raise SystemError(output.stdout.decode())

@dataclass
class WinProc:
    name: str
    server_name: str = ''
    is_running: bool = False
    instances: List[int] = field(default_factory=list)

    def __post_init__(self):
        if (len(self.server_name) == 0):
            self.server_name = os.environ['COMPUTERNAME']
        self.update()

    def update(self):
        tl = [l.strip() for l in get_tasklist(self.server_name).split('\n') if len(l.strip()) > 0]
        tl = [[i.strip('\"') for i in l.split(',"')] for l in tl]
        tasks = [t for t in tl if t[0].lower() == self.name.lower()]
        
        self.is_running = False;
        self.instances = [];
        
        if len(tasks) > 0:
            self.is_running = True
            for task in tasks:
                self.instances.append(int(task[1]))

if __name__ == '__main__':
    proc = WinProc('RazerCentralService.exe')
    print(proc)