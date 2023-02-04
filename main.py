from typing import List
from dataclasses import dataclass
from enum import Enum, auto
from json import loads
from service import WinService
from url import Url
from program import WinProc

class CheckType(Enum):
    JOB = auto()
    PROGRAM = auto()
    SERVICE = auto()
    URL = auto()

class ServiceType(Enum):
    NONE = auto()
    AVA = auto()
    EDI = auto()
    JOB = auto()
    NAS = auto()
    PRINT = auto()
    PROPHESY = auto()
    RTC = auto()
    SHAREPOINT = auto()
    SMS = auto()
    SQL = auto()
    WEBPAGE = auto()
    WS09R2 = auto()


@dataclass
class Check:
    name: str
    server: str
    check_type: CheckType
    service_type: ServiceType = ServiceType.NONE
    service: str = ''
    url: str = ''
    program: str = ''
    instance_count: int = 0
    database: str = ''
    company: str = ''
    business_unit: str = 'all'
    system: str = 'all'

def get_check_type(t: str) -> CheckType:
    t = t.lower()
    types = list(CheckType)
    for tp in types:
        if tp.name.lower() == t:
            return tp
    raise KeyError(f'Cannot find a valid job type for {t}.')

def get_service_type(t: str) -> ServiceType:
    t = t.lower()
    types = list(ServiceType)
    for tp in types:
        if tp.name.lower() == t:
            return tp
    return ServiceType.NONE

if __name__ == '__main__':
    with open('checklist.json', 'r') as f:
        data = loads(f.read())
    
    checks: List[Check] = []
    for item in data:
        ct = get_check_type(item['type'])
        st = get_service_type(item['service_type'])
        program = ''
        instance_count = 0
        if 'program' in item:
            program = item['program']
        if 'instanceCount' in item:
            instance_count = item['instanceCount']
        check = Check(item['name'], item['server'], ct, st, item['service'], item['url'], program, instance_count, item['db'], item['company'], item['bu'], item['system'])
        checks.append(check)

    for check in checks:
        if check.check_type == CheckType.JOB:
            ...
        elif check.check_type == CheckType.PROGRAM:
            proc = WinProc(check.program, check.server)
            if not proc.is_running:
                print(f'NOT RUNNING:\n{proc}')
        elif check.check_type == CheckType.SERVICE:
            svc = WinService(check.service, check.server)
            if not svc.is_running:
                print(f'NOT RUNNING:\n{svc}')
        elif check.check_type == CheckType.URL:
            url = Url(check.url)
            if not url.is_running:
                print(f'NOT RUNNING:\n{url}')
        else:
            raise KeyError(f'Unknown check type: {check.check_type}\n{check}')